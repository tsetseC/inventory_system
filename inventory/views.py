from collections import defaultdict

from django.conf import settings
from django.db.models import Sum, Case, When, IntegerField, Q
from django.shortcuts import render
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

import pandas as pd
import requests

from .models import Item, StockMovement, Tag
from .serializers import ScanSerializer
from .ml_predictor import predict_demand



from django.views.decorators.http import require_POST
from django.utils.dateparse import parse_datetime
from django.http import JsonResponse
import json

from .models import UltrasonicReading


from django.db.models.functions import TruncDate
from django.utils import timezone

import json
import datetime
from pathlib import Path

from joblib import load as joblib_load






# ---------------------------------------------------------------------------
# API: Scan from RFID device
# ---------------------------------------------------------------------------

class ScanView(APIView):
    """Handles RFID scan POST requests (Pi → backend)"""

    def post(self, request):
        serializer = ScanSerializer(data=request.data)
        if serializer.is_valid():
            movement = serializer.save()
            return Response(
                {
                    "message": "Scan recorded",
                    "item": movement.item.name,
                    "direction": movement.direction,
                    "location": movement.location,
                    "timestamp": movement.scanned_at,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------------------------------------------------------------------
# DASHBOARD VIEW
# --------------------------------------------------------------------------


from pathlib import Path
import pandas as pd
from django.conf import settings
# ...rest of imports...


import os
import json
import pandas as pd

from django.conf import settings
from django.db.models import Sum, Q
from django.shortcuts import render

from .models import Item, StockMovement, UltrasonicReading


def load_kaggle_df():
    """
    Load the retail_store_inventory.csv file and return a DataFrame,
    or None if it cannot be loaded.
    """
    csv_path = os.path.join(settings.BASE_DIR, "retail_store_inventory.csv")
    # If you keep the file in a subfolder, e.g. BASE_DIR / "data" / "retail_store_inventory.csv"
    # then change the line above to:
    # csv_path = os.path.join(settings.BASE_DIR, "data", "retail_store_inventory.csv")

    if not os.path.exists(csv_path):
        return None

    try:
        df = pd.read_csv(csv_path, parse_dates=["Date"])
        return df
    except Exception:
        return None


def dashboard(request):
    # ---------------- RFID / STOCK SUMMARY ----------------
    items = Item.objects.all()

    current_rows = []
    total_items_tracked = items.count()
    total_stock_in_system = 0
    low_critical_items = 0

    for item in items:
        stock_in = (
            StockMovement.objects
            .filter(item=item, direction="IN")
            .aggregate(total=Sum("quantity"))["total"] or 0
        )
        stock_out = (
            StockMovement.objects
            .filter(item=item, direction="OUT")
            .aggregate(total=Sum("quantity"))["total"] or 0
        )
        current = stock_in - stock_out
        total_stock_in_system += current
        if current <= 1:
            low_critical_items += 1

        current_rows.append({
            "item_name": item.name,
            "stock_in": stock_in,
            "stock_out": stock_out,
            "current": current,
        })

    chart_labels = [row["item_name"] for row in current_rows]
    chart_values = [row["current"] for row in current_rows]

    # Last ultrasonic reading for the BIN / SHELF card
    last_reading = UltrasonicReading.objects.order_by("-created_at").first()
    bin_distance = last_reading.distance_cm if last_reading else None
    bin_updated_at = last_reading.created_at if last_reading else None

    # ---------------- KAGGLE CSV – SALES BY DATE & CATEGORY ----------------
    # Adjust this path if your CSV lives somewhere else
    csv_path = Path(settings.BASE_DIR) / "data" / "retail_store_inventory.csv"

    daily_labels = []
    daily_values = []
    category_labels = []
    category_values = []

    if csv_path.exists():
        df = pd.read_csv(csv_path)

        # Make sure the columns we need are present
        if {"Date", "Category", "Units Sold"}.issubset(df.columns):
            # Parse dates
            df["Date"] = pd.to_datetime(df["Date"])

            # ---- LEFT CHART: Units Sold by Date ----
            daily = (
                df.groupby("Date")["Units Sold"]
                  .sum()
                  .sort_index()
            )
            daily_labels = [d.strftime("%Y-%m-%d") for d in daily.index]
            daily_values = [int(v) for v in daily.values]

            # ---- RIGHT CHART: Units Sold by Category ----
            cat = (
                df.groupby("Category")["Units Sold"]
                  .sum()
                  .sort_values(ascending=False)
            )
            category_labels = list(cat.index)
            category_values = [int(v) for v in cat.values]

    # ---------------- TEMPLATE CONTEXT ----------------
    context = {
        # KPI cards
        "total_items_tracked": total_items_tracked,
        "total_stock_in_system": total_stock_in_system,
        "low_critical_items": low_critical_items,

        # BIN / shelf distance card
        "bin_distance": bin_distance,
        "bin_updated_at": bin_updated_at,

        # RFID table + bar chart
        "current_rows": current_rows,
        "chart_labels": chart_labels,
        "chart_values": chart_values,

        # Kaggle charts
        "daily_labels": daily_labels,          # LEFT: Rolling Units Sold (by date)
        "daily_values": daily_values,
        "category_labels": category_labels,    # RIGHT: Top Categories (Units Sold by category)
        "category_values": category_values,
    }

    return render(request, "inventory/dashboard.html", context)
# FORECAST FORM (HTML PAGE USING ML API)
# ---------------------------------------------------------------------------

def forecast_form(request):
    """
    Renders the Inventory Forecast page and, on POST,
    calls the /api/predict-inventory/ endpoint to get the prediction.
    """
    initial = {
        "date": "",
        "store_id": "S001",
        "product_id": "P0001",
        "category": "Groceries",
        "region": "North",
        "inventory_level": "50",
        "units_ordered": "40",
        "demand_forecast": "45",
        "price": "30",
        "discount": "0",
        "competitor_pricing": "29",
        "weather": "Sunny",
        "seasonality": "Summer",
        "holiday_promotion": "0",  # 0 = No, 1 = Yes
    }

    form_values = initial.copy()
    result = None
    error_msg = None

    if request.method == "POST":
        for key in form_values.keys():
            form_values[key] = request.POST.get(key, form_values[key])

        payload = {
            "Date": form_values["date"] or "2022-01-01",
            "Store_ID": form_values["store_id"],
            "Product_ID": form_values["product_id"],
            "Category": form_values["category"],
            "Region": form_values["region"],
            "Inventory_Level": int(form_values["inventory_level"] or 0),
            "Units_Ordered": int(form_values["units_ordered"] or 0),
            "Demand_Forecast": int(form_values["demand_forecast"] or 0),
            "Price": float(form_values["price"] or 0),
            "Discount": float(form_values["discount"] or 0),
            "Competitor_Pricing": float(form_values["competitor_pricing"] or 0),
            "Weather_Condition": form_values["weather"],
            "Seasonality": form_values["seasonality"],
            "Holiday_Promotion": int(form_values["holiday_promotion"] or 0),
        }

        try:
            resp = requests.post(
                "http://127.0.0.1:8000/api/predict-inventory/",
                json=payload,
                timeout=5,
            )
            if resp.ok:
                data = resp.json()
                result = {
                    "prediction_units_sold": round(
                        data.get("prediction_units_sold", 0), 2
                    ),
                    "recommended_inventory_level": round(
                        data.get("recommended_inventory_level", 0), 2
                    ),
                }
            else:
                error_msg = f"API error: {resp.status_code}"
        except Exception as e:
            error_msg = f"Error calling prediction API: {e}"

    context = {
        "form": form_values,
        "result": result,
        "error": error_msg,
    }
    return render(request, "inventory/predict.html", context)


# ---------------------------------------------------------------------------
# STOCK HISTORY (HTML)
# ---------------------------------------------------------------------------

def stock_history(request):
    """Shows last 50 stock movements"""
    movements = (
        StockMovement.objects.select_related("item")
        .order_by("-scanned_at")[:50]
    )
    return render(request, "inventory/stock_history.html", {"movements": movements})


def stock_history_filter(request):
    """Filtered stock history (HTML)"""
    items = Item.objects.all()
    movements = StockMovement.objects.select_related("item").order_by("-scanned_at")

    item_id = request.GET.get("item")
    start = request.GET.get("start")
    end = request.GET.get("end")
    direction = request.GET.get("direction")

    if item_id:
        movements = movements.filter(item_id=item_id)

    if direction and direction in ("IN", "OUT"):
        movements = movements.filter(direction=direction)

    if start:
        movements = movements.filter(scanned_at__date__gte=parse_date(start))

    if end:
        movements = movements.filter(scanned_at__date__lte=parse_date(end))

    return render(
        request,
        "inventory/stock_history_filter.html",
        {"items": items, "movements": movements},
    )


# ---------------------------------------------------------------------------
# JSON APIs FOR CHARTS / INTEGRATION
# ---------------------------------------------------------------------------

@api_view(["GET"])
def items_summary(request):
    """GET /api/items-summary/ → stock per item (for JS/Power BI)"""
    items = Item.objects.all().annotate(
        total_in=Sum(
            Case(
                When(movements__direction="IN", then="movements__quantity"),
                default=0,
                output_field=IntegerField(),
            )
        ),
        total_out=Sum(
            Case(
                When(movements__direction="OUT", then="movements__quantity"),
                default=0,
                output_field=IntegerField(),
            )
        ),
    )

    data = []
    for item in items:
        current_stock = (item.total_in or 0) - (item.total_out or 0)
        data.append(
            {
                "id": item.id,
                "name": item.name,
                "sku": item.sku,
                "total_in": item.total_in or 0,
                "total_out": item.total_out or 0,
                "current_stock": current_stock,
            }
        )
    return Response(data)


@api_view(["GET"])
def movements_list(request):
    """GET /api/movements/ → last 100 movements as JSON"""
    movements = (
        StockMovement.objects.select_related("item")
        .order_by("-scanned_at")[:100]
    )

    data = []
    for mv in movements:
        data.append(
            {
                "item": mv.item.name,
                "direction": mv.direction,
                "location": mv.location,
                "quantity": mv.quantity,
                "scanned_at": mv.scanned_at,
            }
        )
    return Response(data)


@api_view(["GET"])
def tag_info(request, uid):
    """
    GET /api/tag-info/<uid>/
    Returns item + current stock for a given RFID tag UID.
    """
    try:
        tag = Tag.objects.select_related("item").get(uid=uid)
    except Tag.DoesNotExist:
        return Response({"detail": "Unknown tag UID"}, status=404)

    item = tag.item
    totals = item.movements.aggregate(
        total_in=Sum(
            Case(
                When(direction="IN", then="quantity"),
                default=0,
                output_field=IntegerField(),
            )
        ),
        total_out=Sum(
            Case(
                When(direction="OUT", then="quantity"),
                default=0,
                output_field=IntegerField(),
            )
        ),
    )
    current_stock = (totals["total_in"] or 0) - (totals["total_out"] or 0)

    return Response(
        {
            "uid": tag.uid,
            "item": item.name,
            "sku": item.sku,
            "current_stock": current_stock,
        }
    )


# ---------------------------------------------------------------------------
# ML PREDICTION ENDPOINTS
# ---------------------------------------------------------------------------

@api_view(["POST"])
def predict_inventory(request):
    """
    POST /api/predict-inventory/
    Returns predicted units sold + recommended inventory level.
    """
    try:
        input_data = request.data
        prediction = predict_demand(input_data)
        return Response(
            {
                "prediction_units_sold": float(prediction),
                "recommended_inventory_level": max(float(prediction) * 1.2, 1),
            }
        )
    except Exception as e:
        return Response({"error": str(e)}, status=400)


@csrf_exempt
def prediction_view(request):
    """
    Alternative web form that calls the ML helper directly (not the API).
    Still rendering inventory/predict.html.
    """
    context = {
        "prediction": None,
        "recommended_level": None,
        "error": None,
    }

    if request.method == "POST":
        try:
            form = request.POST

            input_data = {
                "Date": form.get("date") or "2024-01-01",
                "Store_ID": form.get("store_id") or "S001",
                "Product_ID": form.get("product_id") or "P0001",
                "Category": form.get("category") or "Groceries",
                "Region": form.get("region") or "North",
                "Inventory_Level": int(form.get("inventory_level") or 50),
                "Units_Ordered": int(form.get("units_ordered") or 40),
                "Demand_Forecast": int(form.get("demand_forecast") or 45),
                "Price": float(form.get("price") or 30),
                "Discount": float(form.get("discount") or 0),
                "Weather_Condition": form.get("weather") or "Sunny",
                "Holiday_Promotion": int(form.get("holiday_promo") or 0),
                "Competitor_Pricing": float(
                    form.get("competitor_price") or 29
                ),
                "Seasonality": form.get("seasonality") or "Summer",
            }

            y_pred = predict_demand(input_data)
            prediction = float(y_pred)
            recommended_level = max(prediction * 1.2, 1)

            context["prediction"] = round(prediction, 2)
            context["recommended_level"] = round(recommended_level, 2)

        except Exception as e:
            context["error"] = str(e)

    return render(request, "inventory/predict.html", context)


# ---------------------------------------------------------------------------
# EXTRA API: Forecast vs Actual (for charts + AI insight text)
# ---------------------------------------------------------------------------

@api_view(["GET"])
def forecast_vs_actual(request):
    """
    GET /api/forecast-vs-actual/
    Returns monthly actual Units Sold vs Demand Forecast (2022–2024),
    plus % error and high-level insights for the dashboard.
    """
    csv_path = settings.BASE_DIR / "data" / "retail_store_inventory.csv"

    try:
        df = pd.read_csv(csv_path)
        required_cols = ["Date", "Units Sold", "Demand Forecast"]
        for col in required_cols:
            if col not in df.columns:
                raise KeyError(f"Column not found: {col}")

        df["Date"] = pd.to_datetime(df["Date"])
        df = df[(df["Date"] >= "2022-01-01") & (df["Date"] <= "2024-12-31")]
        if df.empty:
            raise ValueError("No rows found in the 2022–2024 window")

        monthly = (
            df.groupby(pd.Grouper(key="Date", freq="M"))
            .agg(
                {
                    "Units Sold": "sum",
                    "Demand Forecast": "sum",
                }
            )
            .reset_index()
        )

        monthly["AbsErrorPct"] = (
            (monthly["Demand Forecast"] - monthly["Units Sold"])
            .abs()
            / monthly["Units Sold"].replace(0, pd.NA)
            * 100
        )

        overall_mape = float(monthly["AbsErrorPct"].mean())

        best_row = monthly.loc[monthly["AbsErrorPct"].idxmin()]
        worst_row = monthly.loc[monthly["AbsErrorPct"].idxmax()]

        insights = {
            "overall_mape": round(overall_mape, 1),
            "best_month": best_row["Date"].strftime("%Y-%m"),
            "best_month_error": round(float(best_row["AbsErrorPct"]), 1),
            "worst_month": worst_row["Date"].strftime("%Y-%m"),
            "worst_month_error": round(float(worst_row["AbsErrorPct"]), 1),
        }

        labels = monthly["Date"].dt.strftime("%Y-%m").tolist()
        actual = monthly["Units Sold"].astype(int).tolist()
        forecast_vals = monthly["Demand Forecast"].astype(int).tolist()
        error_pct = monthly["AbsErrorPct"].round(1).fillna(0).tolist()

        return Response(
            {
                "labels": labels,
                "actual": actual,
                "forecast": forecast_vals,
                "error_pct": error_pct,
                "insights": insights,
            }
        )

    except Exception as e:
        return Response({"error": str(e)}, status=400)


# ---------------------------------------------------------------------------
# EXTRA API: RFID IN vs OUT trend
# ---------------------------------------------------------------------------

@api_view(["GET"])
def rfid_in_out_trend(request):
    """
    GET /api/rfid-in-out/
    Returns daily IN vs OUT quantities for RFID movements (for the bottom-right chart).
    """
    qs = StockMovement.objects.order_by("scanned_at")

    if not qs.exists():
        return Response(
            {"labels": [], "in_values": [], "out_values": []}
        )

    rows = []
    for mv in qs:
        rows.append(
            {
                "date": mv.scanned_at.date(),
                "direction": mv.direction.upper(),
                "quantity": mv.quantity,
            }
        )

    df = pd.DataFrame(rows)
    g = (
        df.groupby(["date", "direction"])["quantity"]
        .sum()
        .unstack(fill_value=0)
        .sort_index()
    )

    labels = [d.strftime("%Y-%m-%d") for d in g.index]
    in_values = g.get("IN", pd.Series([0] * len(g))).tolist()
    out_values = g.get("OUT", pd.Series([0] * len(g))).tolist()

    return Response(
        {
            "labels": labels,
            "in_values": in_values,
            "out_values": out_values,
        }
    )


# ---------------------------------------------------------------------------
# EXTRA API: Category timeseries (for interactive category click)
# ---------------------------------------------------------------------------

@api_view(["GET"])
def category_timeseries(request):
    """
    GET /api/category-timeseries/?category=Furniture
    Returns daily Units Sold for a single category (2022–2024).
    Used when the user clicks a bar in 'Top Categories' chart.
    """
    category = request.GET.get("category")
    if not category:
        return Response({"error": "category query parameter is required"}, status=400)

    csv_path = settings.BASE_DIR / "data" / "retail_store_inventory.csv"

    try:
        df = pd.read_csv(csv_path)

        required_cols = ["Date", "Units Sold", "Category"]
        for col in required_cols:
            if col not in df.columns:
                raise KeyError(f"Column not found: {col}")

        df["Date"] = pd.to_datetime(df["Date"])
        df = df[
            (df["Date"] >= "2022-01-01")
            & (df["Date"] <= "2024-12-31")
            & (df["Category"] == category)
        ]

        if df.empty:
            return Response(
                {
                    "labels": [],
                    "values": [],
                    "error": f"No rows found for category '{category}'",
                }
            )

        g = (
            df.groupby("Date")["Units Sold"]
            .sum()
            .reset_index()
            .sort_values("Date")
        )

        labels = [d.strftime("%Y-%m-%d") for d in g["Date"]]
        values = [int(v) for v in g["Units Sold"]]

        return Response({"labels": labels, "values": values})

    except Exception as e:
        return Response({"error": str(e)}, status=400)


# ---------------------------------------------------------------------------
# AI ASSISTANT ENDPOINT
# ---------------------------------------------------------------------------

@api_view(["POST"])
def ai_assistant(request):
    """
    POST /api/ai-assistant/
    Simple inventory 'AI assistant' that summarises current RFID stock in plain English.
    (You can later swap this logic for a real LLM call.)
    """
    question = (request.data.get("question") or "").lower().strip()

    movements = StockMovement.objects.select_related("item").order_by("scanned_at")
    per_item = defaultdict(lambda: {"stock_in": 0, "stock_out": 0})

    for m in movements:
        name = m.item.name
        if m.direction.upper() == "IN":
            per_item[name]["stock_in"] += m.quantity
        else:
            per_item[name]["stock_out"] += m.quantity

    if not per_item:
        return Response(
            {
                "answer": (
                    "I don't see any RFID scans yet, so I can't give stock insights. "
                    "Once items start scanning in and out, I'll summarise stock levels for you."
                )
            }
        )

    LOW_THRESHOLD = 1
    low_items = []
    out_items = []

    for name, vals in per_item.items():
        current = vals["stock_in"] - vals["stock_out"]
        if current <= 0:
            out_items.append(name)
        elif current <= LOW_THRESHOLD:
            low_items.append(name)

    total_items = len(per_item)
    answer = f"We are currently tracking {total_items} item type(s). "

    if out_items:
        answer += "Out of stock: " + ", ".join(out_items) + ". "
    if low_items:
        answer += "Low stock: " + ", ".join(low_items) + ". "
    if not low_items and not out_items:
        answer += "All tracked items are above the low-stock threshold. "

    if "summary" in question or "overview" in question:
        answer = "High-level overview: " + answer
    elif "risk" in question or "stock out" in question or "out of stock" in question:
        answer += "These are the key stock-out risks at the moment."
    else:
        answer += (
            "You can ask things like 'which items are low?', "
            "'give me a summary', or 'any stock-out risks today?'."
        )

    return Response({"answer": answer})


@csrf_exempt
@require_POST
def ultrasonic_ping(request):
    """
    Pi posts: {"sensor_name": "bin_1", "distance_cm": 12.3}
    """
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    sensor_name = payload.get("sensor_name", "ultrasonic_1")
    distance_cm = payload.get("distance_cm")

    try:
        distance_cm = float(distance_cm)
    except (TypeError, ValueError):
        return JsonResponse({"error": "distance_cm required"}, status=400)

    reading = UltrasonicReading.objects.create(
        sensor_name=sensor_name,
        distance_cm=distance_cm,
    )

    return JsonResponse(
        {
            "status": "ok",
            "id": reading.id,
            "distance_cm": reading.distance_cm,
            "created_at": reading.created_at.isoformat(),
        }
    )


def ultrasonic_latest(request):
    """
    Returns latest reading + last N points for a small chart.
    """
    qs = UltrasonicReading.objects.order_by("-created_at")[:50]  # last 50
    qs = list(qs)[::-1]  # oldest → newest for chart

    if not qs:
        return JsonResponse({"has_data": False, "message": "No ultrasonic readings yet."})

    labels = [r.created_at.strftime("%H:%M:%S") for r in qs]
    values = [r.distance_cm for r in qs]
    latest = qs[-1]

    return JsonResponse(
        {
            "has_data": True,
            "latest_cm": latest.distance_cm,
            "latest_at": latest.created_at.isoformat(),
            "labels": labels,
            "values": values,
        }
    )





from django.db.models import Sum, Case, When, IntegerField
from django.db.models.functions import TruncDate
from django.utils import timezone
import datetime
import json

from .models import StockMovement


def my_data_dashboard(request):
    """
    'My Data' dashboard – uses only your StockMovement table (RFID data).
    Provides:
      - daily_units_data    : total OUT per day (all items)
      - item_units_data     : total OUT per item
      - item_daily_data     : per-item, per-day OUT (for chart interaction)
      - stock_level_data    : IN, OUT, In Stock, Reorder Qty, Status
      - forecast_data       : simple 5-day moving-average forecast vs actual
      - ml_forecast_data    : ML forecast vs actual (trained model)
    """

    # ------------------------------------------------------------------
    # 1) DAILY UNITS SOLD (all items, OUT only)
    # ------------------------------------------------------------------
    daily_qs = (
        StockMovement.objects
        .filter(direction="OUT")
        .annotate(day=TruncDate("scanned_at"))
        .values("day")
        .order_by("day")
        .annotate(total_out=Sum("quantity"))
    )

    daily_units = [
        {
            "date": row["day"].strftime("%Y-%m-%d"),
            "total_out": int(row["total_out"] or 0),
        }
        for row in daily_qs
    ]

    # ------------------------------------------------------------------
    # 2) UNITS SOLD BY ITEM (total OUT per item)
    # ------------------------------------------------------------------
    item_qs = (
        StockMovement.objects
        .filter(direction="OUT")
        .values("item__name")
        .annotate(total_out=Sum("quantity"))
        .order_by("item__name")
    )

    item_units = [
        {
            "item_name": row["item__name"],
            "total_out": int(row["total_out"] or 0),
        }
        for row in item_qs
    ]

    # ------------------------------------------------------------------
    # 3) PER-ITEM PER-DAY DATA (for chart interaction)
    #    Used when you click a bar on the right chart to filter the left.
    # ------------------------------------------------------------------
    item_daily_qs = (
        StockMovement.objects
        .filter(direction="OUT")
        .annotate(day=TruncDate("scanned_at"))
        .values("item__name", "day")
        .order_by("item__name", "day")
        .annotate(total_out=Sum("quantity"))
    )

    item_daily_data = [
        {
            "item_name": row["item__name"],
            "date": row["day"].strftime("%Y-%m-%d"),
            "total_out": int(row["total_out"] or 0),
        }
        for row in item_daily_qs
    ]

    # ------------------------------------------------------------------
    # 4) LIVE STOCK LEVEL (IN, OUT, In Stock) + REORDER LOGIC
    # ------------------------------------------------------------------
    # a) Aggregate total IN and OUT per item
    stock_qs = (
        StockMovement.objects
        .values("item__name")
        .annotate(
            total_in=Sum(
                Case(
                    When(direction="IN", then="quantity"),
                    default=0,
                    output_field=IntegerField(),
                )
            ),
            total_out=Sum(
                Case(
                    When(direction="OUT", then="quantity"),
                    default=0,
                    output_field=IntegerField(),
                )
            ),
        )
        .order_by("item__name")
    )

    # b) Weekly demand per item (last 7 days, OUT only)
    today = timezone.now().date()
    week_ago = today - datetime.timedelta(days=7)

    weekly_qs = (
        StockMovement.objects
        .filter(direction="OUT", scanned_at__date__gte=week_ago)
        .values("item__name")
        .annotate(weekly_out=Sum("quantity"))
    )

    weekly_map = {
        row["item__name"]: int(row["weekly_out"] or 0)
        for row in weekly_qs
    }

    # c) Business rules for stock + reorder
    REORDER_THRESHOLD = 50      # minimum safe stock
    SAFETY_FACTOR = 1.25        # 25% buffer on weekly demand

    stock_levels = []
    for row in stock_qs:
        item_name = row["item__name"]
        total_in = int(row["total_in"] or 0)
        total_out = int(row["total_out"] or 0)
        raw_in_stock = total_in - total_out

        # Show "in stock" as 0 if oversold (stock can't be negative physically)
        in_stock = raw_in_stock if raw_in_stock > 0 else 0

        weekly_out = weekly_map.get(item_name, 0)

        # --- Reorder logic ---
        if raw_in_stock < 0:
            # Oversold: more OUT than IN recorded
            oversold_by = abs(raw_in_stock)
            # Reorder at least enough to cover the gap plus one extra week of sales
            base_target = weekly_out * SAFETY_FACTOR + oversold_by
            target_level = max(base_target, REORDER_THRESHOLD)
            reorder_qty = int(max(target_level - in_stock, 0))
            status = f"Oversold by {oversold_by}"
        elif in_stock <= REORDER_THRESHOLD:
            # Low stock: top up based on recent demand
            base_target = weekly_out * SAFETY_FACTOR
            # Ensure we at least aim for the threshold
            target_level = max(base_target, REORDER_THRESHOLD)
            reorder_qty = int(max(target_level - in_stock, 0))

            if in_stock == 0:
                status = "Out of stock"
            else:
                status = "Low stock"
        else:
            # Healthy stock – no reorder
            reorder_qty = 0
            status = "In stock"

        stock_levels.append(
            {
                "item": item_name,
                "total_in": total_in,
                "total_out": total_out,
                "in_stock": in_stock,
                "reorder_qty": reorder_qty,
                "status": status,
            }
        )

    # ------------------------------------------------------------------
    # 5) FORECAST DATASETS (keep existing + add ML version)
    # ------------------------------------------------------------------
    # Existing simple forecast (5-day moving average helper)
    forecast_rows = forecast_vs_actual_data()

    # NEW: ML forecast vs actual (using trained model & rfid_demand_ml.csv)
    ml_forecast_rows = ml_forecast_vs_actual_data()

    # ------------------------------------------------------------------
    # 6) SEND DATA TO TEMPLATE
    # ------------------------------------------------------------------
    context = {
        "daily_units_data": json.dumps(daily_units),
        "item_units_data": json.dumps(item_units),
        "item_daily_data": json.dumps(item_daily_data),
        "stock_level_data": json.dumps(stock_levels),
        "forecast_data": json.dumps(forecast_rows),
        "ml_forecast_data": json.dumps(ml_forecast_rows),
    }

    return render(request, "inventory/my_data_dashboard.html", context)

def forecast_vs_actual_data():
    """
    Build last-30-days Actual vs Forecast data from your StockMovement table.
    Actual = OUT movements per day.
    Forecast = simple 5-day moving average over actual.
    """
    end_date = timezone.now().date()
    start_date = end_date - datetime.timedelta(days=30)

    # ----- 1) Actual OUT per day -----
    actual_qs = (
        StockMovement.objects
        .filter(direction="OUT", scanned_at__date__gte=start_date)
        .annotate(day=TruncDate("scanned_at"))
        .values("day")
        .annotate(total_out=Sum("quantity"))
        .order_by("day")
    )

    actual = [
        {
            "date": row["day"].strftime("%Y-%m-%d"),
            "actual": int(row["total_out"] or 0),
        }
        for row in actual_qs
    ]

    # If there is no data, just return empty list so the chart hides gracefully
    if not actual:
        return []

    # ----- 2) Simple forecast = rolling 5-day average -----
    window = 5  # 5-day moving average
    values = [row["actual"] for row in actual]
    forecast = []

    for i in range(len(values)):
        start_idx = max(0, i - window)
        window_slice = values[start_idx : i + 1]
        avg = sum(window_slice) / len(window_slice)
        forecast.append(round(avg))

    # ----- 3) Combine into single list for the template / JS -----
    forecast_data = []
    for i in range(len(actual)):
        forecast_data.append(
            {
                "date": actual[i]["date"],
                "actual": actual[i]["actual"],
                "forecast": forecast[i],
            }
        )

    return forecast_data


def ml_forecast_vs_actual_data():
    """
    Uses the trained ML model on rfid_demand_ml.csv to compare
    model forecast vs actual sales for the last 30 days.
    """
    # __file__ is inventory/views.py -> parent is inventory/
    base_dir = Path(__file__).resolve().parent
    csv_path = base_dir / "data" / "rfid_demand_ml.csv"
    model_path = base_dir / "models" / "rfid_forecast_model.joblib"

    if not csv_path.exists() or not model_path.exists():
        return []

    df = pd.read_csv(csv_path)

    # keep only last 30 rows
    if len(df) > 30:
        df = df.tail(30)

    # Features and target must match what you used when training
    if "date" not in df.columns or "sales" not in df.columns:
        return []

    X = df.drop(columns=["date", "sales"])
    y_actual = df["sales"].astype(int).tolist()

    model = joblib_load(model_path)
    y_pred = model.predict(X)
    y_pred = [int(round(v)) for v in y_pred]

    labels = df["date"].astype(str).tolist()

    rows = []
    for date_str, actual, forecast_val in zip(labels, y_actual, y_pred):
        rows.append(
            {
                "date": date_str,
                "actual": actual,
                "ml_forecast": forecast_val,
            }
        )
    return rows


# inventory/views.py (near your other helpers)
from joblib import load
import numpy as np
import pandas as pd
import datetime

ML_MODEL_PATH = settings.BASE_DIR / "inventory" / "models" / "rfid_forecast_model.joblib"

def ml_forecast_last_30_days_by_item():
    """
    Returns a dict:
      {
        "Android Smartphone": [
            {"date": "2025-11-01", "actual": 23, "predicted": 25},
            ...
        ],
        "Desktop PC": [...],
        ...
      }
    using the same model you trained.
    """

    if not (ML_MODEL_PATH.exists()):
        return {}

    model = load(ML_MODEL_PATH)

    end_date = timezone.now().date()
    start_date = end_date - datetime.timedelta(days=60)  # use 60 so we can build features

    # Daily OUT per item
    qs = (
        StockMovement.objects
        .filter(direction="OUT", scanned_at__date__gte=start_date)
        .annotate(day=TruncDate("scanned_at"))
        .values("item__name", "day")
        .annotate(total_out=Sum("quantity"))
        .order_by("item__name", "day")
    )

    if not qs:
        return {}

    # Put into a DataFrame
    df = pd.DataFrame.from_records(qs)
    df.rename(columns={"item__name": "item", "day": "date", "total_out": "actual"}, inplace=True)
    df["date"] = pd.to_datetime(df["date"])

    result = {}

    for item_name, g in df.groupby("item"):
        g = g.sort_values("date").reset_index(drop=True)

        # Build simple features for inference (must match how you trained!)
        g["day_of_week"] = g["date"].dt.dayofweek
        g["lag_1"] = g["actual"].shift(1)
        g["lag_7"] = g["actual"].shift(7)
        g["ma_7"]  = g["actual"].rolling(window=7, min_periods=1).mean()

        feat_cols = ["day_of_week", "lag_1", "lag_7", "ma_7"]
        X = g[feat_cols].fillna(method="bfill").fillna(0)

        y_pred = model.predict(X)

        # Only keep the last 30 days for the chart
        g_last = g.iloc[-30:].copy()
        y_last = y_pred[-30:]

        rows = []
        for row, pred in zip(g_last.itertuples(), y_last):
            rows.append({
                "date": row.date.strftime("%Y-%m-%d"),
                "actual": int(row.actual),
                "predicted": float(pred),
            })

        result[item_name] = rows

    return result

