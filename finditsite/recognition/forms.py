from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

ALLOWED_IMAGE_TYPES = ("image/jpeg", "image/png", "image/webp")
MAX_IMAGE_SIZE = 10 * 1024 * 1024
MAX_IMAGE_PIXELS = 16 * 1024 * 1024


def validate_uploaded_image(image):
    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise ValidationError(_("Upload a JPEG, PNG, or WebP image."))
    if image.size > MAX_IMAGE_SIZE:
        raise ValidationError(
            _("Each image must be %(limit)s MB or smaller."),
            params={"limit": MAX_IMAGE_SIZE // (1024 * 1024)},
        )
    width, height = image.image.size
    if width * height > MAX_IMAGE_PIXELS:
        raise ValidationError(
            _("Each image must be %(limit)s megapixels or smaller."),
            params={"limit": MAX_IMAGE_PIXELS // (1024 * 1024)},
        )


class ResultUploadForm(forms.Form):
    template_image = forms.ImageField(
        label=_("Object to recognize"),
        validators=[validate_uploaded_image],
    )
    reference_image = forms.ImageField(
        label=_("Image to search it in"),
        validators=[validate_uploaded_image],
    )
