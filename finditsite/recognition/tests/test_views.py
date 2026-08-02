from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from recognition.models import ProcessingMode
from recognition.tests.factories import create_result


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
