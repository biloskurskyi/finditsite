import cv2
import numpy as np
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from recognition.models import ProcessingMode, RecognitionResult
from recognition.services.recognition import create_result
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

    def run_common_pixels(self, template, reference):
        return create_result(
            self.user,
            ProcessingMode.COMMON_PIXELS,
            image_upload("template.jpg", template),
            image_upload("reference.jpg", reference),
        )

    def test_persists_the_result_for_the_user_and_mode(self):
        result = self.run_common_pixels(self.template, self.reference)

        self.assertEqual(result.user, self.user)
        self.assertEqual(result.mode, ProcessingMode.COMMON_PIXELS)
        self.assertTrue(result.image.name.startswith("results/"))

    def test_composes_a_half_size_side_by_side_visualization(self):
        result = self.run_common_pixels(self.template, self.reference)

        result.image.open()
        composite = cv2.imdecode(
            np.frombuffer(result.image.read(), dtype=np.uint8), cv2.IMREAD_COLOR
        )
        template_height, template_width = self.template.shape[:2]
        reference_height, reference_width = self.reference.shape[:2]

        self.assertEqual(
            composite.shape[:2],
            (
                max(template_height, reference_height) // 2,
                (template_width + reference_width) // 2,
            ),
        )

    def test_rejects_images_without_distinctive_features(self):
        featureless = featureless_image()

        with self.assertRaises(ValidationError):
            self.run_common_pixels(featureless, featureless)

        self.assertEqual(RecognitionResult.objects.count(), 0)

    def test_rejects_images_with_too_few_shared_features(self):
        square, circle = unmatchable_images()

        with self.assertRaises(ValidationError):
            self.run_common_pixels(square, circle)

        self.assertEqual(RecognitionResult.objects.count(), 0)

    def test_rejects_a_mode_without_a_renderer(self):
        with self.assertRaises(ValidationError):
            create_result(
                self.user,
                ProcessingMode.ISOLATION,
                image_upload("template.jpg", self.template),
                image_upload("reference.jpg", self.reference),
            )

        self.assertEqual(RecognitionResult.objects.count(), 0)
