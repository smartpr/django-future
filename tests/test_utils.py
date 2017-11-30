from datetime import timedelta

from django.test import TestCase

from django_future.utils import parse_timedelta


class UtilsTestCase(TestCase):

    def test_parse_timedelta(self):
        self.assertEqual(timedelta(minutes=60), parse_timedelta("60m"))
        self.assertEqual(timedelta(hours=24), parse_timedelta("24h"))
        self.assertEqual(timedelta(days=7), parse_timedelta("7d"))
        self.assertEqual(timedelta(weeks=52), parse_timedelta("52w"))
