import cv2
import numpy as np
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

RATIO_THRESHOLD = 0.75
MINIMUM_GOOD_MATCHES = 4

TOO_FEW_FEATURES = _("One of the images has too few distinctive features to compare.")
TOO_FEW_MATCHES = _("These two images do not have enough in common to compare.")


def decode_image(uploaded_file):
    uploaded_file.seek(0)
    return cv2.imdecode(
        np.frombuffer(uploaded_file.read(), dtype=np.uint8), cv2.IMREAD_COLOR
    )


def find_matches(template_image, reference_image, matcher):
    detector = cv2.SIFT_create()
    template_keypoints, template_descriptors = detector.detectAndCompute(
        template_image, None
    )
    reference_keypoints, reference_descriptors = detector.detectAndCompute(
        reference_image, None
    )
    if template_descriptors is None or reference_descriptors is None:
        raise ValidationError(TOO_FEW_FEATURES)

    neighbour_pairs = matcher.knnMatch(template_descriptors, reference_descriptors, k=2)
    if any(len(pair) < 2 for pair in neighbour_pairs):
        raise ValidationError(TOO_FEW_FEATURES)

    good_matches = [
        nearest
        for nearest, second in neighbour_pairs
        if nearest.distance < RATIO_THRESHOLD * second.distance
    ]
    if len(good_matches) < MINIMUM_GOOD_MATCHES:
        raise ValidationError(TOO_FEW_MATCHES)

    return template_keypoints, reference_keypoints, good_matches
