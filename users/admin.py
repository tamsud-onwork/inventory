from django.contrib import admin
from .models import Employee, Customer

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "name", "role")
    search_fields = ("name", "user__username")
    list_filter = ("role",)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "name", "contact_email", "contact_phone")
    search_fields = ("name", "user__username", "contact_email")
