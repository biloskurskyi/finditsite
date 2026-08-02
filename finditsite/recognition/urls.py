from django.urls import path, register_converter

from recognition.converters import ProcessingModeConverter
from recognition.views import ModeDetailView

register_converter(ProcessingModeConverter, "mode")

app_name = "recognition"

urlpatterns = [
    path("modes/<mode:mode>/", ModeDetailView.as_view(), name="mode"),
]
