from django.contrib import admin
from django.urls import path
from orderform.views import landing, home, thanks

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", landing, name="landing"),        # new landing page at /
    path("order/", home, name="home"),        # order form moved here
    path("thanks/", thanks, name="thanks"),
]
