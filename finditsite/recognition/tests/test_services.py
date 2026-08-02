import cv2
import numpy as np
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import SimpleTestCase, TestCase

from recognition.models import ProcessingMode, RecognitionResult
from recognition.services.matching import find_homography
from recognition.services.recognition import create_result
from recognition.services.renderers import (QUADRILATERAL_COLORS,
                                            render_detection)
from recognition.tests.factories import (TemporaryMediaRootMixin,
                                         featureless_image, image_upload,
                                         matchable_images, unmatchable_images)


class CreateResultTests(TemporaryMediaRootMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(
            username="owner", password="an-uncommon-passphrase"
        )
        self.template, self.reference = matchable_images()

    def run_mode(self, mode, template, reference):
        return create_result(
            self.user,
            mode,
            image_upload("template.jpg", template),
            image_upload("reference.jpg", reference),
        )

    def composite_of(self, result):
        result.image.open()
        return cv2.imdecode(
            np.frombuffer(result.image.read(), dtype=np.uint8), cv2.IMREAD_COLOR
        )

    def normalized_size(self):
        template_height, template_width = self.template.shape[:2]
        reference_height, reference_width = self.reference.shape[:2]
        return (
            min(template_height, reference_height),
            min(template_width, reference_width),
        )

    def test_persists_the_result_for_the_user_and_mode(self):
        result = self.run_mode(
            ProcessingMode.COMMON_PIXELS, self.template, self.reference
        )

        self.assertEqual(result.user, self.user)
        self.assertEqual(result.mode, ProcessingMode.COMMON_PIXELS)
        self.assertTrue(result.image.name.startswith("results/"))

    def test_composes_a_half_size_side_by_side_visualization(self):
        result = self.run_mode(
            ProcessingMode.COMMON_PIXELS, self.template, self.reference
        )

        template_height, template_width = self.template.shape[:2]
        reference_height, reference_width = self.reference.shape[:2]

        self.assertEqual(
            self.composite_of(result).shape[:2],
            (
                max(template_height, reference_height) // 2,
                (template_width + reference_width) // 2,
            ),
        )

    def test_isolation_composes_a_half_size_pair_of_normalized_images(self):
        result = self.run_mode(ProcessingMode.ISOLATION, self.template, self.reference)

        height, width = self.normalized_size()
        self.assertEqual(
            self.composite_of(result).shape[:2], (height // 2, 2 * (width // 2))
        )

    def test_isolation_accepts_a_pair_of_differing_dimensions(self):
        self.assertNotEqual(self.template.shape, self.reference.shape)

        result = self.run_mode(ProcessingMode.ISOLATION, self.template, self.reference)

        self.assertEqual(result.mode, ProcessingMode.ISOLATION)

    def test_detection_composes_a_half_size_pair_of_normalized_images(self):
        result = self.run_mode(ProcessingMode.DETECTION, self.template, self.reference)

        height, width = self.normalized_size()
        self.assertEqual(
            self.composite_of(result).shape[:2],
            (round(height * 0.5), round(2 * width * 0.5)),
        )

    def test_detection_highlights_the_projected_template_location(self):
        composite = render_detection(self.template, self.reference)

        for color in QUADRILATERAL_COLORS:
            self.assertTrue(np.any(np.all(composite == color, axis=2)))

    def test_rejects_images_without_distinctive_features(self):
        featureless = featureless_image()

        with self.assertRaises(ValidationError):
            self.run_mode(ProcessingMode.COMMON_PIXELS, featureless, featureless)

        self.assertEqual(RecognitionResult.objects.count(), 0)

    def test_rejects_images_with_too_few_shared_features_in_every_mode(self):
        square, circle = unmatchable_images()

        for mode in ProcessingMode:
            with self.subTest(mode=mode):
                with self.assertRaises(ValidationError):
                    self.run_mode(mode, square, circle)

        self.assertEqual(RecognitionResult.objects.count(), 0)


class FindHomographyTests(SimpleTestCase):
    def test_rejects_matches_that_describe_no_transform(self):
        keypoints = [cv2.KeyPoint(10.0, 10.0, 1.0) for _ in range(6)]
        matches = [cv2.DMatch(index, index, 0.0) for index in range(6)]

        with self.assertRaises(ValidationError):
            find_homography(keypoints, keypoints, matches)
