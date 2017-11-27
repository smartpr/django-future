from datetime import datetime

from django.test import TestCase

from django_future.models import ScheduledJob


class ModelTestCase(TestCase):

    def test_default_status(self):
        job = ScheduledJob.objects.create(
                time_slot_start=datetime(1970, 1, 1),
                time_slot_end=datetime(1970, 1, 2))
        self.assertEqual(job.status, ScheduledJob.STATUS_SCHEDULED)
