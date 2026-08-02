from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from recognition.models import ProcessingMode, RecognitionResult
from recognition.tests.factories import (TemporaryMediaRootMixin,
                                         create_result, damaged_image_upload,
                                         matchable_images, unmatchable_images,
                                         upload_payload)


class ModeRoutingTests(TestCase):
    def test_every_mode_has_a_slug_route(self):
        for mode in ProcessingMode:
            response = self.client.get(reverse("recognition:mode", args=[mode]))

            self.assertEqual(response.status_code, 200)

    def test_an_unknown_slug_is_not_found(self):
        response = self.client.get("/modes/telepathy/")

        self.assertEqual(response.status_code, 404)

    def test_a_positional_index_is_not_a_slug(self):
        response = self.client.get("/modes/1/")

        self.assertEqual(response.status_code, 404)


class ModeTeaserTests(TestCase):
    def test_an_anonymous_visitor_gets_the_teaser(self):
        response = self.client.get(
            reverse("recognition:mode", args=[ProcessingMode.COMMON_PIXELS])
        )

        self.assertTemplateUsed(response, "recognition/mode_teaser.html")
        self.assertTemplateNotUsed(response, "recognition/mode_detail.html")

    def test_the_teaser_invites_the_visitor_to_log_in(self):
        response = self.client.get(
            reverse("recognition:mode", args=[ProcessingMode.ISOLATION])
        )

        self.assertContains(response, reverse("accounts:login"))


class ModeDetailTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner", password="an-uncommon-passphrase"
        )
        self.stranger = User.objects.create_user(
            username="stranger", password="an-uncommon-passphrase"
        )
        self.url = reverse("recognition:mode", args=[ProcessingMode.COMMON_PIXELS])

    def test_an_authenticated_visitor_gets_the_workspace(self):
        self.client.force_login(self.owner)

        response = self.client.get(self.url)

        self.assertTemplateUsed(response, "recognition/mode_detail.html")
        self.assertTemplateNotUsed(response, "recognition/mode_teaser.html")

    def test_titles_the_page_with_the_mode_label(self):
        self.client.force_login(self.owner)

        response = self.client.get(self.url)

        self.assertEqual(response.context["title"], "FindIt - Common Pixels")

    def test_renders_the_result_and_history_partials(self):
        self.client.force_login(self.owner)

        response = self.client.get(self.url)

        self.assertTemplateUsed(response, "recognition/partials/result_panel.html")
        self.assertTemplateUsed(response, "recognition/partials/history_list.html")

    def test_shows_the_empty_state_without_results(self):
        self.client.force_login(self.owner)

        response = self.client.get(self.url)

        self.assertIsNone(response.context["latest_result"])
        self.assertEqual(len(response.context["result_dates"]), 0)

    def test_shows_the_owners_result_for_the_requested_mode(self):
        result = create_result(self.owner, ProcessingMode.COMMON_PIXELS)
        self.client.force_login(self.owner)

        response = self.client.get(self.url)

        self.assertEqual(response.context["latest_result"], result)
        self.assertContains(response, result.image.url)

    def test_hides_the_result_from_another_user(self):
        result = create_result(self.owner, ProcessingMode.COMMON_PIXELS)
        self.client.force_login(self.stranger)

        response = self.client.get(self.url)

        self.assertIsNone(response.context["latest_result"])
        self.assertNotContains(response, result.image.url)

    def test_hides_the_result_from_the_other_mode_pages(self):
        create_result(self.owner, ProcessingMode.COMMON_PIXELS)
        self.client.force_login(self.owner)

        response = self.client.get(
            reverse("recognition:mode", args=[ProcessingMode.DETECTION])
        )

        self.assertIsNone(response.context["latest_result"])

    def test_lists_the_recent_run_timestamps(self):
        for minutes_ago in range(2):
            create_result(
                self.owner, ProcessingMode.COMMON_PIXELS, minutes_ago=minutes_ago
            )
        self.client.force_login(self.owner)

        response = self.client.get(self.url)

        self.assertEqual(len(response.context["result_dates"]), 2)
        self.assertContains(response, "History")


class ResultCreateTests(TemporaryMediaRootMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.owner = User.objects.create_user(
            username="owner", password="an-uncommon-passphrase"
        )
        self.stranger = User.objects.create_user(
            username="stranger", password="an-uncommon-passphrase"
        )
        self.url = reverse("recognition:results", args=[ProcessingMode.COMMON_PIXELS])
        self.template, self.reference = matchable_images()

    def post_pair(self, template, reference):
        return self.client.post(self.url, upload_payload(template, reference))

    def test_an_anonymous_visitor_is_sent_to_the_login_page(self):
        response = self.post_pair(self.template, self.reference)

        self.assertRedirects(
            response, f"{reverse('accounts:login')}?next={self.url}"
        )
        self.assertEqual(RecognitionResult.objects.count(), 0)

    def test_redirects_to_the_mode_page_after_a_successful_run(self):
        self.client.force_login(self.owner)

        response = self.post_pair(self.template, self.reference)

        self.assertRedirects(
            response,
            reverse("recognition:mode", args=[ProcessingMode.COMMON_PIXELS]),
        )

    def test_renders_the_new_result_with_its_timestamp(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url, upload_payload(self.template, self.reference), follow=True
        )

        result = RecognitionResult.objects.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recognition/mode_detail.html")
        self.assertEqual(response.context["latest_result"], result)
        self.assertContains(response, result.image.url)
        self.assertEqual(len(response.context["result_dates"]), 1)

    def test_does_not_answer_a_get(self):
        self.client.force_login(self.owner)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 405)

    def test_reports_a_damaged_image_on_the_form(self):
        self.client.force_login(self.owner)
        files = upload_payload(self.template, self.reference)
        files["reference_image"] = damaged_image_upload()

        response = self.client.post(self.url, files)

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "One of the images is damaged and could not be read."
        )
        self.assertEqual(RecognitionResult.objects.count(), 0)

    def test_records_the_result_against_its_owner_and_mode(self):
        self.client.force_login(self.owner)

        self.post_pair(self.template, self.reference)

        result = RecognitionResult.objects.get()
        self.assertEqual(result.user, self.owner)
        self.assertEqual(result.mode, ProcessingMode.COMMON_PIXELS)

    def test_another_user_does_not_see_the_result(self):
        self.client.force_login(self.owner)
        self.post_pair(self.template, self.reference)
        self.client.force_login(self.stranger)

        response = self.client.get(
            reverse("recognition:mode", args=[ProcessingMode.COMMON_PIXELS])
        )

        self.assertIsNone(response.context["latest_result"])

    def test_reports_an_invalid_upload_on_the_form(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            {
                "template_image": SimpleUploadedFile(
                    "notes.txt", b"not an image", content_type="text/plain"
                ),
                "reference_image": upload_payload(self.template, self.reference)[
                    "reference_image"
                ],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
        self.assertEqual(RecognitionResult.objects.count(), 0)

    def test_reports_images_that_cannot_be_compared_on_the_form(self):
        self.client.force_login(self.owner)
        square, circle = unmatchable_images()

        response = self.post_pair(square, circle)

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "These two images do not have enough in common to compare."
        )
        self.assertEqual(RecognitionResult.objects.count(), 0)


class ModeNavigationTests(TestCase):
    def test_the_header_links_every_mode(self):
        response = self.client.get(reverse("core:landing"))

        self.assertTemplateUsed(response, "core/partials/mode_nav.html")
        for mode in ProcessingMode:
            self.assertContains(response, reverse("recognition:mode", args=[mode]))

    def test_the_menu_cards_link_their_modes(self):
        user = User.objects.create_user(
            username="owner", password="an-uncommon-passphrase"
        )
        self.client.force_login(user)

        response = self.client.get(reverse("core:menu"))

        for mode in ProcessingMode:
            self.assertContains(response, reverse("recognition:mode", args=[mode]))
