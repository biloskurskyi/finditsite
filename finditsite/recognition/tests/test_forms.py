from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from recognition.forms import ResultUploadForm
from recognition.tests.factories import (damaged_image_upload, image_upload,
                                         matchable_images,
                                         oversized_dimensions_upload,
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

    def test_rejects_a_small_file_holding_too_many_pixels(self):
        oversized = oversized_dimensions_upload()
        files = upload_payload(self.template, self.reference)
        files["reference_image"] = oversized

        form = ResultUploadForm({}, files)

        self.assertLess(oversized.size, 10 * 1024 * 1024)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Each image must be 16 megapixels or smaller.",
            form.errors["reference_image"],
        )

    def test_accepts_a_damaged_file_the_pipeline_has_to_reject(self):
        files = upload_payload(self.template, self.reference)
        files["reference_image"] = damaged_image_upload()

        form = ResultUploadForm({}, files)

        self.assertTrue(form.is_valid())
