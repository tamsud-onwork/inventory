from django.contrib import admin
from .models import Stock, StockMovement, StockAdjustment

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "location", "quantity")
    search_fields = ("product__name", "location__name")

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("id", "stock", "movement_type", "quantity", "timestamp", "reference")
    search_fields = ("stock__product__name", "movement_type", "reference")

@admin.register(StockAdjustment)
class StockAdjustmentAdmin(admin.ModelAdmin):
    list_display = ("id", "stock", "adjustment_type", "quantity", "reason", "approved_by", "timestamp")
    search_fields = ("stock__product__name", "reason", "approved_by__name")
