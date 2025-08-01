from django.contrib import admin
from .models import Category, Product, ProductVariant

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "parent")
    search_fields = ("name",)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "sku", "barcode", "category", "unit_price")
    search_fields = ("name", "sku", "barcode")
    list_filter = ("category",)

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "name", "value")
    search_fields = ("name", "value")
