from django.contrib import admin
from django.urls import path

# ✅ Correct imports
from inventory import views as inventory_views
from inventory.views import (
    ScanView,
    dashboard,
    stock_history,
    stock_history_filter,
    items_summary,
    movements_list,
    predict_inventory,
    forecast_form,
    tag_info,
    forecast_vs_actual,
    rfid_in_out_trend,
    category_timeseries,
    ultrasonic_ping,
    ultrasonic_latest,
    ai_assistant,
)

urlpatterns = [
    path("admin/", admin.site.urls),

    # ---------------- Web Dashboards ----------------
    path("", dashboard, name="dashboard"),
    path("history/", stock_history, name="stock_history"),
    path("history/filter/", stock_history_filter, name="stock_history_filter"),
    path("predict/", forecast_form, name="forecast_form"),

    # ✅ NEW: My Data Dashboard (Ultrasonic + RFID only)
    path("my-data/", inventory_views.my_data_dashboard, name="my_data_dashboard"),

    # ---------------- API Endpoints ----------------
    path("api/scan/", ScanView.as_view(), name="scan"),
    path("api/items-summary/", items_summary, name="items_summary"),
    path("api/movements/", movements_list, name="movements_list"),
    path("api/tag-info/<str:uid>/", tag_info, name="tag_info"),
    path("api/predict-inventory/", predict_inventory, name="predict_inventory"),

    # ---------------- Analytics APIs ----------------
    path("api/forecast-vs-actual/", forecast_vs_actual, name="forecast_vs_actual"),
    path("api/rfid-in-out/", rfid_in_out_trend, name="rfid_in_out_trend"),
    path("api/category-timeseries/", category_timeseries, name="category_timeseries"),
    path("api/ai-assistant/", ai_assistant, name="ai_assistant"),

    # ---------------- Ultrasonic APIs ----------------
    path("api/ultrasonic-ping/", ultrasonic_ping, name="ultrasonic_ping"),
    path("api/ultrasonic-latest/", ultrasonic_latest, name="ultrasonic_latest"),
]
