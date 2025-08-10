from django.contrib import admin
from django.urls import path
from orderform import views as of_views

urlpatterns = [
    path("admin/", admin.site.urls),

    # NEW: Landing page is now the homepage
    path("", of_views.landing_page, name="landing"),

    # Order flow
    path("order/", of_views.home, name="home"),
    path("thanks/", of_views.thanks, name="thanks"),

    # Southern Sweets Club
    path("rewards/", of_views.rewards, name="rewards"),
    path("rewards/thanks/", of_views.rewards_thanks, name="rewards_thanks"),
]
