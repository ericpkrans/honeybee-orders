from django.contrib import admin
from django.urls import path
from orderform.views import home, order_success

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("success/", order_success, name="order_success"),
]
