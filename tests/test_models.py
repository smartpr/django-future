from datetime import timedelta

from django.utils import timezone
from django.test import TestCase

from django_future.models import ScheduledJob


class ModelTestCase(TestCase):

    def setUp(self):
        self.now = timezone.now()
        self.start = self.now
        self.end = self.now + timedelta(days=7)

    def test_default_status(self):
        job = ScheduledJob.objects.create(
                time_slot_start=self.start, time_slot_end=self.end)
        self.assertEqual(job.status, ScheduledJob.STATUS_SCHEDULED)

    def test_repr(self):
        job = ScheduledJob.objects.create(
                time_slot_start=self.start,
                time_slot_end=self.end,
                callable_name="func")

        self.assertEqual(
            "<ScheduledJob (scheduled) callable='func'>",
            repr(job)
        )
