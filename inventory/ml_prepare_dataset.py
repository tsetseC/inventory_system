# inventory/ml_prepare_dataset.py

import os
import sys
from pathlib import Path

# ---- Make sure the Django project root is on sys.path ----
BASE_DIR = Path(__file__).resolve().parent.parent  # .../inventory_system
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# ---- Point to your Django settings module ----
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django
django.setup()

import pandas as pd
from inventory.models import StockMovement


def build_training_dataset():
    qs = (
        StockMovement.objects
        .filter(direction="OUT")
        .order_by("scanned_at")
        .values("scanned_at", "quantity")
    )

    if not qs.exists():
        print("No OUT data found.")
        return

    df = pd.DataFrame(list(qs))
    df["date"] = pd.to_datetime(df["scanned_at"]).dt.date

    daily = df.groupby("date")["quantity"].sum().reset_index()
    daily.rename(columns={"quantity": "sales"}, inplace=True)

    for i in range(1, 8):
        daily[f"lag_{i}"] = daily["sales"].shift(i)

    daily["day_of_week"] = pd.to_datetime(daily["date"]).dt.dayofweek
    daily.dropna(inplace=True)

    save_path = BASE_DIR / "inventory" / "data" / "rfid_demand_ml.csv"
    save_path.parent.mkdir(exist_ok=True)

    daily.to_csv(save_path, index=False)
    print(f"Training file saved to: {save_path}")


if __name__ == "__main__":
    build_training_dataset()
