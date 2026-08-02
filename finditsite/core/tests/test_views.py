from django.contrib.auth.models import User
from django.templatetags.static import static
from django.test import TestCase
from django.urls import reverse


class LandingViewTests(TestCase):
    def test_renders_the_landing_template(self):
        response = self.client.get(reverse("core:landing"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/landing.html")

    def test_supplies_the_page_title(self):
        response = self.client.get(reverse("core:landing"))

        self.assertEqual(response.context["title"], "FindIt")

    def test_renders_the_shared_chrome(self):
        response = self.client.get(reverse("core:landing"))

        self.assertTemplateUsed(response, "core/partials/header.html")
        self.assertTemplateUsed(response, "core/partials/footer.html")
        self.assertContains(response, static("core/css/styles.css"))
        self.assertContains(response, static("core/images/logo.webp"))


class MenuViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="regular", password="an-uncommon-passphrase"
        )

    def test_redirects_an_anonymous_visitor_to_login(self):
        response = self.client.get(reverse("core:menu"))

        self.assertRedirects(
            response, f"{reverse('accounts:login')}?next={reverse('core:menu')}"
        )

    def test_renders_the_menu_for_an_authenticated_visitor(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("core:menu"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/menu.html")

    def test_drops_the_unfounded_pixel_match_claim(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("core:menu"))

        self.assertNotContains(response, "90%")


class HeaderVariantTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="regular", password="an-uncommon-passphrase"
        )

    def test_offers_login_and_registration_to_an_anonymous_visitor(self):
        response = self.client.get(reverse("core:landing"))

        self.assertTemplateUsed(response, "core/partials/user_area_anonymous.html")
        self.assertEqual(response.context["home_url"], reverse("core:landing"))

    def test_offers_a_logout_form_to_an_authenticated_visitor(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("core:menu"))

        self.assertTemplateUsed(response, "core/partials/user_area_authenticated.html")
        self.assertEqual(response.context["home_url"], reverse("core:menu"))
        self.assertContains(response, f'action="{reverse("accounts:logout")}"')
