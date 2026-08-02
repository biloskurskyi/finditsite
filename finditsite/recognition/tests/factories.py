import shutil
import tempfile
from datetime import timedelta

import cv2
import numpy as np
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.utils import timezone

from recognition.models import RecognitionResult


def create_result(user, mode, minutes_ago=0):
    result = RecognitionResult.objects.create(
        user=user, mode=mode, image="results/2026/08/result.jpg"
    )
    RecognitionResult.objects.filter(pk=result.pk).update(
        created_at=timezone.now() - timedelta(minutes=minutes_ago)
    )
    return RecognitionResult.objects.get(pk=result.pk)


def matchable_images():
    blocks = np.random.default_rng(17).integers(0, 256, size=(60, 80, 3), dtype=np.uint8)
    reference = cv2.resize(blocks, (640, 480), interpolation=cv2.INTER_NEAREST)
    return reference[100:380, 120:520].copy(), reference


def unmatchable_images():
    square = np.full((200, 200, 3), 255, dtype=np.uint8)
    cv2.rectangle(square, (40, 40), (90, 90), (0, 0, 0), -1)
    circle = np.full((200, 200, 3), 255, dtype=np.uint8)
    cv2.circle(circle, (120, 120), 30, (0, 0, 0), -1)
    return square, circle


def featureless_image():
    gradient = np.tile(np.linspace(0, 255, 320, dtype=np.uint8), (240, 1))
    return cv2.cvtColor(gradient, cv2.COLOR_GRAY2BGR)


def image_upload(name, image, extension=".jpg"):
    encoded = cv2.imencode(extension, image)[1].tobytes()
    return SimpleUploadedFile(name, encoded, content_type="image/jpeg")


def oversized_image_upload():
    noise = np.random.default_rng(5).integers(
        0, 256, size=(2000, 2000, 3), dtype=np.uint8
    )
    encoded = cv2.imencode(".png", noise, [cv2.IMWRITE_PNG_COMPRESSION, 0])[1].tobytes()
    return SimpleUploadedFile("huge.png", encoded, content_type="image/png")


def oversized_dimensions_upload():
    flat = np.full((4200, 4200, 3), 128, dtype=np.uint8)
    encoded = cv2.imencode(".jpg", flat)[1].tobytes()
    return SimpleUploadedFile("wide.jpg", encoded, content_type="image/jpeg")


def damaged_image_upload():
    encoded = cv2.imencode(".jpg", matchable_images()[1])[1].tobytes()
    return SimpleUploadedFile(
        "damaged.jpg", encoded[: len(encoded) // 2], content_type="image/jpeg"
    )


def upload_payload(template, reference):
    return {
        "template_image": image_upload("template.jpg", template),
        "reference_image": image_upload("reference.jpg", reference),
    }


class TemporaryMediaRootMixin:
    def setUp(self):
        super().setUp()
        media_root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, media_root)
        media_settings = override_settings(MEDIA_ROOT=media_root)
        media_settings.enable()
        self.addCleanup(media_settings.disable)
