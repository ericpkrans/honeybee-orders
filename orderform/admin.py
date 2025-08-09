from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "choice", "date_needed", "created")
    list_filter = ("choice", "date_needed", "created")
    search_fields = ("name", "email", "phone", "details")
