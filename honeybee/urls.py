# honeybee/urls.py
from django.contrib import admin
from django.urls import path
from orderform.views import home, thanks  # <- import 'thanks', not 'order_success'

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("thanks/", thanks, name="thanks"),  # <- route name used by views.py redirect
]
