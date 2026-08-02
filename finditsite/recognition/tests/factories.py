from datetime import timedelta

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
