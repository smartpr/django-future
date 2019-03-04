from datetime import timedelta

from django.utils import timezone
from django.test import TestCase

from django_future.models import ScheduledJob


class ModelTestCase(TestCase):

    def setUp(self):
        start = timezone.now()
        end = start + timedelta(days=7)

        self.job = ScheduledJob.objects.create(
            time_slot_start=start, time_slot_end=end,
            callable_name="func", args=(), kwargs={})

    def test_default_status(self):
        self.assertEqual(
            self.job.status,
            ScheduledJob.STATUS_SCHEDULED)

    def test_repr(self):
        self.assertEqual(
            "<ScheduledJob (scheduled) callable='func'>",
            repr(self.job)
        )
