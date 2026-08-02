import cv2
import numpy as np
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

RATIO_THRESHOLD = 0.75
MINIMUM_GOOD_MATCHES = 4
RANSAC_REPROJECTION_THRESHOLD = 5.0

TOO_FEW_FEATURES = _("One of the images has too few distinctive features to compare.")
TOO_FEW_MATCHES = _("These two images do not have enough in common to compare.")
UNREADABLE_IMAGE = _("One of the images is damaged and could not be read.")


def decode_image(uploaded_file):
    uploaded_file.seek(0)
    image = cv2.imdecode(
        np.frombuffer(uploaded_file.read(), dtype=np.uint8), cv2.IMREAD_COLOR
    )
    if image is None:
        raise ValidationError(UNREADABLE_IMAGE)
    return image


def normalize_dimensions(template_image, reference_image):
    size = (
        min(template_image.shape[1], reference_image.shape[1]),
        min(template_image.shape[0], reference_image.shape[0]),
    )
    return cv2.resize(template_image, size), cv2.resize(reference_image, size)


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


def find_homography(template_keypoints, reference_keypoints, good_matches):
    source_points = np.float32(
        [template_keypoints[match.queryIdx].pt for match in good_matches]
    ).reshape(-1, 1, 2)
    destination_points = np.float32(
        [reference_keypoints[match.trainIdx].pt for match in good_matches]
    ).reshape(-1, 1, 2)
    homography = cv2.findHomography(
        source_points, destination_points, cv2.RANSAC, RANSAC_REPROJECTION_THRESHOLD
    )[0]
    if homography is None:
        raise ValidationError(TOO_FEW_MATCHES)
    return homography
