from recognition.models import ProcessingMode


class ProcessingModeConverter:
    regex = "|".join(ProcessingMode.values)

    def to_python(self, value):
        return ProcessingMode(value)

    def to_url(self, value):
        return ProcessingMode(value).value
