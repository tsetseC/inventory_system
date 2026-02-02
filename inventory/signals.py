from math import ceil

from django.db import models          # needed for models.Sum
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UltrasonicReading, BinConfig, StockMovement


@receiver(post_save, sender=UltrasonicReading)
def auto_update_stock_from_ultrasonic(sender, instance, created, **kwargs):
    """
    When a new ultrasonic reading is saved, automatically convert
    the distance into units and create a StockMovement (IN or OUT)
    so the dashboard updates.
    We only run on 'created' to avoid double-counting on edits.
    """
    if not created:
        return

    # 1) Find the bin mapped to this sensor
    try:
        bin_cfg = BinConfig.objects.get(name=instance.sensor_name)
    except BinConfig.DoesNotExist:
        # No bin configured for this sensor -> nothing to do
        return

    distance = instance.distance_cm
    empty = bin_cfg.empty_distance_cm
    full = bin_cfg.full_distance_cm
    max_units = bin_cfg.max_units

    # 2) Clamp distance into [full, empty]
    if distance > empty:
        distance = empty
    if distance < full:
        distance = full

    # 3) Convert distance -> fill ratio -> units
    if empty == full:
        # avoid division by zero if misconfigured
        return

    fill_ratio = (empty - distance) / (empty - full)   # 0..1
    calculated_units = ceil(fill_ratio * max_units)

    # 4) Get current units from StockMovement
    stock_in = StockMovement.objects.filter(
        item=bin_cfg.item, direction="IN"
    ).aggregate(total=models.Sum("quantity"))["total"] or 0

    stock_out = StockMovement.objects.filter(
        item=bin_cfg.item, direction="OUT"
    ).aggregate(total=models.Sum("quantity"))["total"] or 0

    current_units = stock_in - stock_out

    # 5) Decide how much to adjust by
    delta = calculated_units - current_units

    if delta > 0:
        # Need to add stock
        StockMovement.objects.create(
            item=bin_cfg.item,
            direction="IN",
            quantity=delta,
            source="ultrasonic",
            location=bin_cfg.name,
        )
    elif delta < 0:
        # Need to remove stock
        StockMovement.objects.create(
            item=bin_cfg.item,
            direction="OUT",
            quantity=abs(delta),
            source="ultrasonic",
            location=bin_cfg.name,
        )
    # if delta == 0: already correct, nothing to do
