
from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse
from .models import Stock, StockMovement, StockAdjustment

# Branding
admin.site.site_header = "Inventory"
admin.site.site_title = "Inventory Admin"
admin.site.index_title = "Inventory Dashboard"


# Override the admin index view to show the dashboard as landing page
def inventory_dashboard(request):
    return TemplateResponse(request, "admin/inventory_dashboard.html", {})
admin.site.index = inventory_dashboard

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
