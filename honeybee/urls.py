from django.urls import path
from orderform import views

urlpatterns = [
    path("", views.home, name="home"),
    path("thanks/", views.thanks, name="thanks"),
    path("landing/", views.landing, name="landing"),
    path("rewards/", views.rewards, name="rewards"),
    path("rewards/thanks/", views.rewards_thanks, name="rewards_thanks"),
]
