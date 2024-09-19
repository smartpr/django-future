from datetime import timedelta

from django.test import TransactionTestCase
from django.utils import timezone

from django_future.jobs import (schedule_job, run_jobs, _expire_jobs,
                                _run_scheduled_jobs)
from django_future.models import ScheduledJob


class JobsTestCase(TransactionTestCase):

    def setUp(self):
        self.now = timezone.now()

    def test_expire_jobs(self):
        job = schedule_job(
                self.now - timedelta(hours=1), 'math.pow', args=(2, 3))
        self.assertEqual(job.status, ScheduledJob.STATUS_SCHEDULED)

        _expire_jobs(self.now + timedelta(days=60))

        job.refresh_from_db()
        self.assertEqual(job.status, ScheduledJob.STATUS_EXPIRED)

    def test_run_scheduled_jobs(self):
        job1 = schedule_job(
                self.now - timedelta(hours=2), 'math.pow', args=(2, 2))
        job2 = schedule_job(
                self.now - timedelta(hours=1), 'math.pow', args=(2, 3))

        _run_scheduled_jobs(self.now, False, False)

        job1.refresh_from_db()
        self.assertEqual(job1.status, ScheduledJob.STATUS_COMPLETE)
        self.assertEqual(job1.return_value, '4.0')

        job2.refresh_from_db()
        self.assertEqual(job2.status, ScheduledJob.STATUS_COMPLETE)
        self.assertEqual(job2.return_value, '8.0')

        self.assertLess(job1.execution_start, job2.execution_start)

    def test_run_jobs_complete(self):
        job = schedule_job(
                self.now - timedelta(hours=1), 'math.pow', args=(2, 3))
        self.assertEqual(job.status, ScheduledJob.STATUS_SCHEDULED)

        run_jobs(now=self.now)

        job.refresh_from_db()
        self.assertEqual(job.status, ScheduledJob.STATUS_COMPLETE)
        self.assertEqual(job.return_value, '8.0')

    def test_run_jobs_failed(self):
        job = schedule_job(
                self.now - timedelta(hours=1), 'math.pow')
        self.assertEqual(job.status, ScheduledJob.STATUS_SCHEDULED)

        with self.assertRaises(TypeError):
            run_jobs(now=self.now)

        job.refresh_from_db()
        self.assertEqual(job.status, ScheduledJob.STATUS_FAILED)
