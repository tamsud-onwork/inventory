from django.contrib import admin
from .models import Warehouse, Location

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "capacity", "address")
    search_fields = ("name",)

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("id", "warehouse", "name", "type")
    search_fields = ("name", "warehouse__name")
