from recognition.models import ProcessingMode


def processing_modes(request):
    return {"processing_modes": ProcessingMode}
