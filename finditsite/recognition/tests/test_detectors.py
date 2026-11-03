import cv2
import numpy as np
from django.test import SimpleTestCase, override_settings

from recognition.services.detectors import (OrbDetector, SiftDetector,
                                            build_matcher, get_detector)
from recognition.services.matching import find_matches


def checkerboard(square=32, cells=12):
    board = (np.indices((cells, cells)).sum(axis=0) % 2) * 255
    image = np.kron(board, np.ones((square, square))).astype(np.uint8)
    noise = np.random.default_rng(3).integers(0, 40, size=image.shape, dtype=np.uint8)
    return cv2.cvtColor(cv2.add(image, noise), cv2.COLOR_GRAY2BGR)


class GetDetectorTests(SimpleTestCase):
    def test_returns_requested_class(self):
        self.assertIsInstance(get_detector("sift"), SiftDetector)
        self.assertIsInstance(get_detector("orb"), OrbDetector)

    def test_default_comes_from_settings(self):
        self.assertIsInstance(get_detector(), SiftDetector)
        with override_settings(RECOGNITION_DETECTOR="orb"):
            self.assertIsInstance(get_detector(), OrbDetector)

    def test_unknown_name_raises_value_error(self):
        with self.assertRaises(ValueError):
            get_detector("surf")


class OrbMatchingTests(SimpleTestCase):
    def test_matches_shifted_copy(self):
        board = checkerboard()
        shifted = np.roll(board, (20, 30), axis=(0, 1))
        detector = get_detector("orb")
        matcher = build_matcher(detector)
        result = find_matches(board, shifted, matcher, detector)
        self.assertGreaterEqual(len(result.good_matches), 4)
