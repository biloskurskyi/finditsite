from django.urls import path

from core.views import LandingView

app_name = "core"

urlpatterns = [
    path("", LandingView.as_view(), name="landing"),
]
