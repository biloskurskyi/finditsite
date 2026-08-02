from django.urls import path, register_converter

from recognition.converters import ProcessingModeConverter
from recognition.views import ModeDetailView, ResultCreateView

register_converter(ProcessingModeConverter, "mode")

app_name = "recognition"

urlpatterns = [
    path("modes/<mode:mode>/", ModeDetailView.as_view(), name="mode"),
    path("modes/<mode:mode>/results/", ResultCreateView.as_view(), name="results"),
]
