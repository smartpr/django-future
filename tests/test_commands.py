from datetime import timedelta
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from django_future.jobs import schedule_job
from django_future.models import ScheduledJob


class RunScheduledJobsCommandTest(TestCase):

    def setUp(self):
        self.schedule_at = timezone.now() - timedelta(days=1)

        self.jobs = [
            schedule_job(self.schedule_at, 'math.pow', args=(2, 3)),
            schedule_job(self.schedule_at, 'math.pow', args=(5, 2))
        ]

    def test_cmd_noargs(self):
        """
        Test invocation of command with no arguments. Ensure the scheduled jobs
        are marked as completed.
        """
        self.assertEqual(
            2,
            ScheduledJob.objects.filter(
                status=ScheduledJob.STATUS_SCHEDULED).count()
        )

        call_command('runscheduledjobs')

        self.assertEqual(
            2,
            ScheduledJob.objects.filter(
                status=ScheduledJob.STATUS_COMPLETE).count()
        )

    def test_cmd_delete_completed(self):
        """
        Test invocation of command with '-d' argument to delete completed jobs.
        Ensure the scheduled jobs are removed after.
        """
        self.assertEqual(
            2,
            ScheduledJob.objects.filter(
                status=ScheduledJob.STATUS_SCHEDULED).count()
        )

        call_command('runscheduledjobs', '-d')

        self.assertEqual(0, ScheduledJob.objects.count())

    def test_cmd_ignore_errors(self):
        """
        Test invocation of command with '-i' argument to keep processing jobs
        even if a job fails. Ensure the non-failing jobs are marked as
        completed and the error job is marked as failed.
        """
        schedule_at = self.schedule_at - timedelta(days=1)
        error_job = schedule_job(schedule_at, 'math.funky_error')

        self.assertEqual(
            3,
            ScheduledJob.objects.filter(
                status=ScheduledJob.STATUS_SCHEDULED).count()
        )

        call_command('runscheduledjobs', '-i')

        error_job.refresh_from_db()
        self.assertEqual(error_job.status, ScheduledJob.STATUS_FAILED)

        self.assertEqual(
            2,
            ScheduledJob.objects.filter(
                status=ScheduledJob.STATUS_COMPLETE).count()
        )
