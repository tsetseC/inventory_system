from django.db import models
from django.utils import timezone


class Item(models.Model):
    name = models.CharField(max_length=100)
    sku = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        help_text="Stock Keeping Unit or unique code for the item.",
    )

    def __str__(self):
        return self.name


class Tag(models.Model):
    uid = models.CharField(max_length=50, unique=True)
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name="tags",
    )

    def __str__(self):
        return f"{self.uid} → {self.item.name}"


class StockMovement(models.Model):
    IN_OUT = [
        ("IN", "Stock In"),
        ("OUT", "Stock Out"),
    ]

    SOURCE_CHOICES = [
        ("rfid", "RFID Scanner"),
        ("manual", "Manual Capture"),
        ("ultrasonic", "Ultrasonic Sensor"),
        ("other", "Other"),
    ]

    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name="movements",
    )
    direction = models.CharField(max_length=3, choices=IN_OUT)
    location = models.CharField(max_length=100, blank=True, null=True)
    quantity = models.IntegerField(default=1)

    # IMPORTANT: allow custom/random timestamps (no auto_now_add here)
    scanned_at = models.DateTimeField(
        default=timezone.now,
        help_text="When this movement happened (can be backdated for historical data).",
    )

    # Where this record came from (RFID, manual entry, etc.)
    source = models.CharField(
        max_length=50,
        choices=SOURCE_CHOICES,
        default="rfid",
    )

    class Meta:
        ordering = ["-scanned_at"]

    def __str__(self):
        return f"{self.item.name} {self.direction} x{self.quantity} @ {self.scanned_at:%Y-%m-%d %H:%M}"


class BinConfig(models.Model):
    """
    Calibration between distance (cm) and units for ONE bin/sensor.
    E.g. Bin 1 holds 'Test Box', empty at 30 cm, full at 5 cm, max 10 units.
    """
    name = models.CharField(max_length=100, default="Bin 1", unique=True)
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name="bin_configs",
    )

    # Distances in cm – tune these to match your physical setup
    empty_distance_cm = models.FloatField(
        default=30.0,
        help_text="Distance (cm) when bin is EMPTY (sensor → floor/lowest point).",
    )
    full_distance_cm = models.FloatField(
        default=5.0,
        help_text="Distance (cm) when bin is FULL (sensor → top of stock).",
    )

    # How many units this bin can hold when full
    max_units = models.PositiveIntegerField(
        default=10,
        help_text="Number of items when bin is considered FULL.",
    )

    def __str__(self):
        return f"{self.name} → {self.item.name}"


class UltrasonicReading(models.Model):
    """
    Raw readings from the Pi ultrasonic sensor.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    sensor_name = models.CharField(max_length=50, default="ultrasonic_1")
    bin_name = models.CharField(max_length=100, default="Bin 1")

    distance_cm = models.FloatField()
    raw_payload = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.sensor_name} @ {self.created_at:%Y-%m-%d %H:%M:%S} = {self.distance_cm} cm"


# ---------- Helper: map distance → units ----------

def distance_to_units(distance_cm: float, config: BinConfig) -> int:
    """
    Convert a distance reading (cm) into an integer unit count for the given bin.

    - Shorter distance = more stock (closer to 'full').
    - Longer distance  = less stock (closer to 'empty').

    Clamps distance inside [full_distance_cm, empty_distance_cm] and
    linearly maps to [0, max_units].
    """
    empty_d = config.empty_distance_cm
    full_d = config.full_distance_cm

    # Protect against misconfigured equal distances
    if empty_d == full_d:
        return 0

    # Clamp the distance into [full_d, empty_d]
    d = max(min(distance_cm, empty_d), full_d)

    # fill_ratio: 1.0 at full, 0.0 at empty
    fill_ratio = (empty_d - d) / (empty_d - full_d)

    fill_ratio = max(0.0, min(1.0, fill_ratio))

    units = round(fill_ratio * config.max_units)
    return int(units)
