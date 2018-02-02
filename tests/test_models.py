from datetime import timedelta

from django.utils import timezone
from django.test import TestCase

from django_future.models import ScheduledJob


class ModelTestCase(TestCase):

    def setUp(self):
        self.now = timezone.now()

    def test_default_status(self):
        start = self.now
        end = self.now + timedelta(days=7)
        job = ScheduledJob.objects.create(
                time_slot_start=start, time_slot_end=end)
        self.assertEqual(job.status, ScheduledJob.STATUS_SCHEDULED)
