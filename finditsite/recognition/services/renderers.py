import cv2
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from recognition.models import ProcessingMode
from recognition.services.matching import find_matches


def render_common_pixels(template_image, reference_image):
    template_keypoints, reference_keypoints, good_matches = find_matches(
        template_image, reference_image, cv2.BFMatcher()
    )
    composite = cv2.drawMatches(
        template_image,
        template_keypoints,
        reference_image,
        reference_keypoints,
        good_matches,
        None,
        flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS,
    )
    height, width = composite.shape[:2]
    return cv2.resize(composite, (width // 2, height // 2))


RENDERERS = {
    ProcessingMode.COMMON_PIXELS: render_common_pixels,
}


def render(mode, template_image, reference_image):
    renderer = RENDERERS.get(mode)
    if renderer is None:
        raise ValidationError(_("This mode is not available yet."))
    return renderer(template_image, reference_image)
