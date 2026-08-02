from django.urls import path

from core.views import LandingView, MenuView

app_name = "core"

urlpatterns = [
    path("", LandingView.as_view(), name="landing"),
    path("menu/", MenuView.as_view(), name="menu"),
]
