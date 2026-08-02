from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from recognition.forms import ResultUploadForm
from recognition.tests.factories import (image_upload, matchable_images,
                                         oversized_image_upload,
                                         upload_payload)


class ResultUploadFormTests(TestCase):
    def setUp(self):
        self.template, self.reference = matchable_images()

    def test_accepts_two_images(self):
        form = ResultUploadForm({}, upload_payload(self.template, self.reference))

        self.assertTrue(form.is_valid())

    def test_requires_both_images(self):
        form = ResultUploadForm(
            {}, {"template_image": image_upload("template.jpg", self.template)}
        )

        self.assertFalse(form.is_valid())
        self.assertIn("reference_image", form.errors)

    def test_rejects_a_file_that_is_not_an_image(self):
        files = upload_payload(self.template, self.reference)
        files["reference_image"] = SimpleUploadedFile(
            "notes.txt", b"not an image at all", content_type="text/plain"
        )

        form = ResultUploadForm({}, files)

        self.assertFalse(form.is_valid())
        self.assertIn("reference_image", form.errors)

    def test_rejects_an_image_format_outside_the_allow_list(self):
        files = upload_payload(self.template, self.reference)
        files["template_image"] = image_upload(
            "template.bmp", self.template, extension=".bmp"
        )

        form = ResultUploadForm({}, files)

        self.assertFalse(form.is_valid())
        self.assertIn("Upload a JPEG, PNG, or WebP image.", form.errors["template_image"])

    def test_rejects_an_oversized_image(self):
        files = upload_payload(self.template, self.reference)
        files["reference_image"] = oversized_image_upload()

        form = ResultUploadForm({}, files)

        self.assertFalse(form.is_valid())
        self.assertIn(
            "Each image must be 10 MB or smaller.", form.errors["reference_image"]
        )
