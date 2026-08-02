from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class ProcessingMode(models.TextChoices):
    COMMON_PIXELS = "common-pixels", _("Common Pixels")
    ISOLATION = "isolation", _("Isolation")
    DETECTION = "detection", _("Detection & Highlight")


class RecognitionResult(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recognition_results",
    )
    mode = models.CharField(max_length=32, choices=ProcessingMode.choices)
    image = models.ImageField(upload_to="results/%Y/%m/")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "mode", "-created_at"])]

    def __str__(self):
        return f"{self.user} - {self.get_mode_display()} - {self.created_at}"
