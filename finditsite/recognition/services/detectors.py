from typing import Protocol

import cv2
import numpy as np
import numpy.typing as npt
from django.conf import settings

Keypoints = tuple[cv2.KeyPoint, ...]
Descriptors = npt.NDArray[np.generic] | None


class FeatureDetector(Protocol):
    norm_type: int

    def detect_and_compute(self, image: npt.NDArray[np.uint8]) -> tuple[Keypoints, Descriptors]: ...


class SiftDetector:
    norm_type = cv2.NORM_L2

    def __init__(self) -> None:
        self._detector = cv2.SIFT_create()

    def detect_and_compute(self, image: npt.NDArray[np.uint8]) -> tuple[Keypoints, Descriptors]:
        return self._detector.detectAndCompute(image, None)


class OrbDetector:
    norm_type = cv2.NORM_HAMMING

    def __init__(self) -> None:
        self._detector = cv2.ORB_create()

    def detect_and_compute(self, image: npt.NDArray[np.uint8]) -> tuple[Keypoints, Descriptors]:
        return self._detector.detectAndCompute(image, None)


DETECTORS: dict[str, type[SiftDetector] | type[OrbDetector]] = {
    "sift": SiftDetector,
    "orb": OrbDetector,
}


def get_detector(name: str | None = None) -> FeatureDetector:
    name = name or getattr(settings, "RECOGNITION_DETECTOR", "sift")
    try:
        return DETECTORS[name.lower()]()
    except KeyError:
        raise ValueError(f"Unknown feature detector: {name!r}") from None


FLANN_INDEX_KDTREE = 1
FLANN_TREES = 5
FLANN_CHECKS = 50


def build_matcher(detector: FeatureDetector, use_flann: bool = False) -> cv2.DescriptorMatcher:
    """Matcher suited to the detector's descriptors (FLANN k-d tree only works on float descriptors)."""
    if use_flann and detector.norm_type == cv2.NORM_L2:
        return cv2.FlannBasedMatcher(
            {"algorithm": FLANN_INDEX_KDTREE, "trees": FLANN_TREES},
            {"checks": FLANN_CHECKS},
        )
    return cv2.BFMatcher(detector.norm_type)
