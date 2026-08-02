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
