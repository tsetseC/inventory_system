from django.contrib import admin
from .models import Item, Tag, StockMovement, BinConfig, UltrasonicReading


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "sku")
    search_fields = ("name", "sku")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("uid", "item")
    search_fields = ("uid", "item__name")


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("item", "direction", "location", "quantity", "scanned_at")
    list_filter = ("direction", "location", "scanned_at")
    search_fields = ("item__name",)


@admin.register(BinConfig)
class BinConfigAdmin(admin.ModelAdmin):
    list_display = ("name", "item", "max_units", "empty_distance_cm", "full_distance_cm")
    list_filter = ("name", "item")


@admin.register(UltrasonicReading)
class UltrasonicReadingAdmin(admin.ModelAdmin):
    list_display = ("sensor_name", "distance_cm", "created_at")
    list_filter = ("sensor_name", "created_at")
