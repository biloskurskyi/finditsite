import cv2
from django.core.files.base import ContentFile

from recognition.models import RecognitionResult
from recognition.services.matching import decode_image
from recognition.services.renderers import render


def create_result(user, mode, template_image, reference_image):
    composite = render(
        mode, decode_image(template_image), decode_image(reference_image)
    )
    encoded = cv2.imencode(".jpg", composite)[1]
    return RecognitionResult.objects.create(
        user=user,
        mode=mode,
        image=ContentFile(encoded.tobytes(), name="result.jpg"),
    )
