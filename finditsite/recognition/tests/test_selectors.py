from django.contrib.auth.models import User
from django.test import TestCase

from recognition.models import ProcessingMode
from recognition.selectors import latest_result_for, recent_result_dates
from recognition.tests.factories import create_result


class LatestResultForTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner", password="an-uncommon-passphrase"
        )
        self.stranger = User.objects.create_user(
            username="stranger", password="an-uncommon-passphrase"
        )

    def test_returns_the_newest_row_of_the_requested_mode(self):
        create_result(self.owner, ProcessingMode.COMMON_PIXELS, minutes_ago=10)
        newest = create_result(self.owner, ProcessingMode.COMMON_PIXELS)

        self.assertEqual(
            latest_result_for(self.owner, ProcessingMode.COMMON_PIXELS), newest
        )

    def test_ignores_the_other_modes(self):
        create_result(self.owner, ProcessingMode.ISOLATION)

        self.assertIsNone(
            latest_result_for(self.owner, ProcessingMode.COMMON_PIXELS)
        )

    def test_ignores_another_users_rows(self):
        create_result(self.stranger, ProcessingMode.COMMON_PIXELS)

        self.assertIsNone(
            latest_result_for(self.owner, ProcessingMode.COMMON_PIXELS)
        )


class RecentResultDatesTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner", password="an-uncommon-passphrase"
        )
        self.stranger = User.objects.create_user(
            username="stranger", password="an-uncommon-passphrase"
        )

    def test_returns_the_five_newest_timestamps_newest_first(self):
        for minutes_ago in range(7):
            create_result(
                self.owner, ProcessingMode.DETECTION, minutes_ago=minutes_ago
            )

        dates = list(recent_result_dates(self.owner, ProcessingMode.DETECTION))

        self.assertEqual(len(dates), 5)
        self.assertEqual(dates, sorted(dates, reverse=True))

    def test_honours_an_explicit_limit(self):
        for minutes_ago in range(3):
            create_result(
                self.owner, ProcessingMode.DETECTION, minutes_ago=minutes_ago
            )

        dates = recent_result_dates(self.owner, ProcessingMode.DETECTION, limit=2)

        self.assertEqual(len(dates), 2)

    def test_ignores_other_modes_and_other_users(self):
        create_result(self.owner, ProcessingMode.ISOLATION)
        create_result(self.stranger, ProcessingMode.DETECTION)

        dates = recent_result_dates(self.owner, ProcessingMode.DETECTION)

        self.assertEqual(len(dates), 0)
