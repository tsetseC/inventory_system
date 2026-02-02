# seed_stock.py
import random
import datetime
from django.utils import timezone
from inventory.models import Item, StockMovement


def run():
    print("Rebuilding ICT stock database with RANDOM dates...")

    # How many days of history
    days_back = 90   # 3 months of data

    # ICT ITEMS ONLY
    sample_items = [
        ("Laptop Dell i5", "LAP-DELL-I5"),
        ("Laptop HP i7", "LAP-HP-I7"),
        ("Desktop PC", "DESK-PC"),
        ("Android Smartphone", "PHONE-AND"),
        ("iPhone", "PHONE-IOS"),
        ("USB-C Charger", "CHG-USB-C"),
        ("Laptop Power Adapter", "ADP-LAP"),
        ("HDMI Cable", "CBL-HDMI"),
        ("Ethernet Cable", "CBL-LAN"),
        ("Wireless Mouse", "MOU-WL"),
        ("Mechanical Keyboard", "KEY-MECH"),
        ("External Hard Drive", "HDD-EXT"),
        ("USB Flash Drive 32GB", "USB-32"),
        ("Network Switch 8-Port", "SW-08"),
        ("WiFi Router", "RTR-WIFI"),
    ]

    # Create items
    for name, sku in sample_items:
        Item.objects.create(name=name, sku=sku)

    items = list(Item.objects.all())

    today = timezone.now().date()
    start_date = today - datetime.timedelta(days=days_back)

    # Generate realistic stock movements
    for i in range(days_back):
        day = start_date + datetime.timedelta(days=i)

        for item in items:

            # ----- STOCK IN (Morning deliveries) -----
            in_qty = random.randint(5, 25)
            in_time = datetime.time(
                hour=random.randint(7, 10),
                minute=random.randint(0, 59),
                second=random.randint(0, 59)
            )

            StockMovement.objects.create(
                item=item,
                direction="IN",
                quantity=in_qty,
                location="Warehouse",
                scanned_at=timezone.make_aware(
                    datetime.datetime.combine(day, in_time)
                ),
            )

            # ----- STOCK OUT (Random daily sales) -----
            sales_events = random.randint(1, 5)

            for _ in range(sales_events):
                out_qty = random.randint(1, 8)
                out_time = datetime.time(
                    hour=random.randint(12, 20),
                    minute=random.randint(0, 59),
                    second=random.randint(0, 59)
                )

                StockMovement.objects.create(
                    item=item,
                    direction="OUT",
                    quantity=out_qty,
                    location="Store Front",
                    scanned_at=timezone.make_aware(
                        datetime.datetime.combine(day, out_time)
                    ),
                )

    print("✅ Random multi-day ICT stock data successfully generated!")
