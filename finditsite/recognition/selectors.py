from recognition.models import RecognitionResult


def latest_result_for(user, mode):
    return RecognitionResult.objects.filter(user=user, mode=mode).first()


def recent_result_dates(user, mode, limit=5):
    return RecognitionResult.objects.filter(user=user, mode=mode).values_list(
        "created_at", flat=True
    )[:limit]
