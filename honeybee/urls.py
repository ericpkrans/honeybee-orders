from django.contrib import admin
from django.urls import path
from orderform.views import OrderCreate, thanks

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", OrderCreate.as_view(), name="order_form"),
    path("thanks/", thanks, name="thanks"),
]
