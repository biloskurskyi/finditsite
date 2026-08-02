from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from recognition.models import ProcessingMode
from recognition.tests.factories import create_result


class AdminAccessTests(TestCase):
    def test_redirects_an_anonymous_visitor_to_the_admin_login(self):
        response = self.client.get(reverse("admin:index"))

        self.assertEqual(response.status_code, 302)

    def test_admits_a_staff_member(self):
        staff = User.objects.create_superuser(
            username="staff", password="an-uncommon-passphrase"
        )
        self.client.force_login(staff)

        response = self.client.get(reverse("admin:index"))

        self.assertEqual(response.status_code, 200)


class RecognitionResultAdminTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_superuser(
            username="staff", password="an-uncommon-passphrase"
        )
        self.owner = User.objects.create_user(
            username="owner", password="an-uncommon-passphrase"
        )
        self.client.force_login(self.staff)

    def test_lists_the_results(self):
        create_result(self.owner, ProcessingMode.ISOLATION)

        response = self.client.get(
            reverse("admin:recognition_recognitionresult_changelist")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "owner")

    def test_searches_by_the_owners_username(self):
        create_result(self.owner, ProcessingMode.ISOLATION)

        response = self.client.get(
            reverse("admin:recognition_recognitionresult_changelist"),
            {"q": "owner"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["cl"].result_count, 1)

    def test_cannot_add_a_result(self):
        response = self.client.get(reverse("admin:recognition_recognitionresult_add"))

        self.assertEqual(response.status_code, 403)

    def test_cannot_edit_a_result(self):
        result = create_result(self.owner, ProcessingMode.ISOLATION)

        response = self.client.get(
            reverse("admin:recognition_recognitionresult_change", args=[result.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'name="_save"')
