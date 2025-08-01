from django.contrib import admin
from .models import Supplier, SupplierProduct

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "contact_name", "contact_email", "contact_phone")
    search_fields = ("name", "contact_name")

@admin.register(SupplierProduct)
class SupplierProductAdmin(admin.ModelAdmin):
    list_display = ("id", "supplier", "product")
    search_fields = ("supplier__name", "product__name")

# Register your models here.
