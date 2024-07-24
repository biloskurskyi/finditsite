import sys

sys.path.append('D:/work/project1/finditsite')

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finditsite.settings')

import django

django.setup()

from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from blocks.views import \
    IndexView  # Assuming your views module is named 'blocks.views'


class IndexViewTestCase(TestCase):
    def test_view(self):
        path = reverse('blocks:home')
        response = self.client.get(path)

        self.assertEqual(response.status_code, HTTPStatus.OK)

        self.assertEqual(response.context_data['title'], 'FindIt')


class MianViewTestCase(TestCase):
    def test_try_get_view(self):
        path = reverse('blocks:log_home')
        response = self.client.get(path)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        redirected_path = response.url
        redirected_response = self.client.get(redirected_path)

        self.assertEqual(redirected_response.status_code, HTTPStatus.OK)
        self.assertEqual(redirected_response.context_data['title'], 'FindIt - LogIn')

    def setUp(self):
        self.test_user = User.objects.create_user(username='testuser', password='testpassword')

    def test_login_required(self):
        path = reverse('blocks:log_home')
        response = self.client.get(path)

        self.assertEqual(response.status_code, 302)

        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(path)

        self.assertEqual(response.status_code, 200)

        self.client.logout()
