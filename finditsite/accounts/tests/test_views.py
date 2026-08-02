from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class RegistrationViewTests(TestCase):
    def test_creates_the_user_and_redirects_to_login(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newcomer",
                "email": "newcomer@example.com",
                "password1": "an-uncommon-passphrase",
                "password2": "an-uncommon-passphrase",
            },
        )

        self.assertRedirects(response, reverse("accounts:login"))
        self.assertTrue(User.objects.filter(username="newcomer").exists())

    def test_carries_the_success_message_to_the_login_page(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newcomer",
                "email": "newcomer@example.com",
                "password1": "an-uncommon-passphrase",
                "password2": "an-uncommon-passphrase",
            },
            follow=True,
        )

        self.assertContains(response, "Registration is successfully done!")

    def test_rejects_mismatched_passwords(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newcomer",
                "email": "newcomer@example.com",
                "password1": "an-uncommon-passphrase",
                "password2": "a-different-passphrase",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="newcomer").exists())


class LoginViewTests(TestCase):
    def setUp(self):
        User.objects.create_user(username="regular", password="an-uncommon-passphrase")

    def test_lands_on_the_menu_in_one_redirect(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "regular", "password": "an-uncommon-passphrase"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("core:menu"))

    def test_renders_the_login_template_for_a_visitor(self):
        response = self.client.get(reverse("accounts:login"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")
        self.assertTemplateUsed(response, "accounts/partials/auth_form.html")


class LogoutViewTests(TestCase):
    def setUp(self):
        User.objects.create_user(username="regular", password="an-uncommon-passphrase")
        self.client.force_login(User.objects.get(username="regular"))

    def test_rejects_a_get_request(self):
        response = self.client.get(reverse("accounts:logout"))

        self.assertEqual(response.status_code, 405)

    def test_ends_the_session_and_returns_to_the_landing_page(self):
        response = self.client.post(reverse("accounts:logout"))

        self.assertRedirects(response, reverse("core:landing"))
        self.assertNotIn("_auth_user_id", self.client.session)
