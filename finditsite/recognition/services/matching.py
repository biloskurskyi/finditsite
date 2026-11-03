from dataclasses import dataclass

import cv2
import numpy as np
import numpy.typing as npt
from django.utils.translation import gettext_lazy as _

from recognition.services.detectors import FeatureDetector, get_detector

RATIO_THRESHOLD = 0.75
MINIMUM_GOOD_MATCHES = 4
RANSAC_REPROJECTION_THRESHOLD = 5.0

TOO_FEW_FEATURES = _("One of the images has too few distinctive features to compare.")
TOO_FEW_MATCHES = _("These two images do not have enough in common to compare.")
UNREADABLE_IMAGE = _("One of the images is damaged and could not be read.")


class RecognitionError(Exception):
    """Raised when two images cannot be compared; the message is safe to show to the user."""


@dataclass(frozen=True)
class MatchResult:
    template_keypoints: tuple[cv2.KeyPoint, ...]
    reference_keypoints: tuple[cv2.KeyPoint, ...]
    good_matches: list[cv2.DMatch]


def decode_image(uploaded_file) -> npt.NDArray[np.uint8]:
    uploaded_file.seek(0)
    image = cv2.imdecode(
        np.frombuffer(uploaded_file.read(), dtype=np.uint8), cv2.IMREAD_COLOR
    )
    if image is None:
        raise RecognitionError(UNREADABLE_IMAGE)
    return image


def normalize_dimensions(
    template_image: npt.NDArray[np.uint8], reference_image: npt.NDArray[np.uint8]
) -> tuple[npt.NDArray[np.uint8], npt.NDArray[np.uint8]]:
    size = (
        min(template_image.shape[1], reference_image.shape[1]),
        min(template_image.shape[0], reference_image.shape[0]),
    )
    return cv2.resize(template_image, size), cv2.resize(reference_image, size)


def find_matches(
    template_image: npt.NDArray[np.uint8],
    reference_image: npt.NDArray[np.uint8],
    matcher: cv2.DescriptorMatcher,
    detector: FeatureDetector | None = None,
) -> MatchResult:
    detector = detector or get_detector()
    template_keypoints, template_descriptors = detector.detect_and_compute(template_image)
    reference_keypoints, reference_descriptors = detector.detect_and_compute(reference_image)
    if template_descriptors is None or reference_descriptors is None:
        raise RecognitionError(TOO_FEW_FEATURES)

    neighbour_pairs = matcher.knnMatch(template_descriptors, reference_descriptors, k=2)
    if any(len(pair) < 2 for pair in neighbour_pairs):
        raise RecognitionError(TOO_FEW_FEATURES)

    good_matches = [
        nearest
        for nearest, second in neighbour_pairs
        if nearest.distance < RATIO_THRESHOLD * second.distance
    ]
    if len(good_matches) < MINIMUM_GOOD_MATCHES:
        raise RecognitionError(TOO_FEW_MATCHES)

    return MatchResult(template_keypoints, reference_keypoints, good_matches)


def find_homography(
    template_keypoints: tuple[cv2.KeyPoint, ...],
    reference_keypoints: tuple[cv2.KeyPoint, ...],
    good_matches: list[cv2.DMatch],
) -> npt.NDArray[np.float64]:
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
        raise RecognitionError(TOO_FEW_MATCHES)
    return homography
