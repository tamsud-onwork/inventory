from django.contrib import admin
from .models import PurchaseOrder, PurchaseOrderItem, SalesOrder, SalesOrderItem

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ("id", "supplier", "created_by", "status", "order_date", "expected_date")
    search_fields = ("supplier__name", "status")

@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "purchase_order", "product", "quantity", "unit_price")
    search_fields = ("purchase_order__id", "product__name")

@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "created_by", "status", "order_date", "shipped_date")
    search_fields = ("customer__name", "status")

@admin.register(SalesOrderItem)
class SalesOrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "sales_order", "product", "quantity", "unit_price")
    search_fields = ("sales_order__id", "product__name")
