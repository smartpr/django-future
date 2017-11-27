from datetime import datetime
from django.test import TransactionTestCase

from django_future.jobs import (schedule_job, run_jobs, _expire_jobs,
                                _run_scheduled_jobs)
from django_future.models import ScheduledJob


class JobsTestCase(TransactionTestCase):

    def test_expire_jobs(self):
        job = schedule_job(datetime(1970, 1, 1), 'math.pow', args=(2, 3))
        self.assertEqual(job.status, ScheduledJob.STATUS_SCHEDULED)

        _expire_jobs(datetime(1980, 1, 1))

        self.assertEqual(
            ScheduledJob.objects.get(pk=job.pk).status,
            ScheduledJob.STATUS_EXPIRED)

    def test_run_scheduled_jobs(self):
        job1 = schedule_job(datetime(1970, 1, 1), 'math.pow', args=(2, 2))
        job2 = schedule_job(datetime(1970, 1, 2), 'math.pow', args=(2, 3))

        _run_scheduled_jobs(datetime(1970, 1, 3), False, False)

        result_job1 = ScheduledJob.objects.get(pk=job1.pk)
        self.assertEqual(result_job1.status, ScheduledJob.STATUS_COMPLETE)
        self.assertEqual(result_job1.return_value, u'4.0')

        result_job2 = ScheduledJob.objects.get(pk=job2.pk)
        self.assertEqual(result_job2.status, ScheduledJob.STATUS_COMPLETE)
        self.assertEqual(result_job2.return_value, u'8.0')

        self.assertLess(
                result_job1.execution_start,
                result_job2.execution_start)

    def test_run_jobs_complete(self):
        job = schedule_job(datetime(1970, 1, 1), 'math.pow', args=(2, 3))
        self.assertEqual(job.status, ScheduledJob.STATUS_SCHEDULED)

        run_jobs(now=datetime(1970, 1, 2))

        result_job = ScheduledJob.objects.get(pk=job.pk)
        self.assertEqual(result_job.status, ScheduledJob.STATUS_COMPLETE)
        self.assertEqual(result_job.return_value, u'8.0')

    def test_run_jobs_failed(self):
        job = schedule_job(datetime(1970, 1, 1), 'math.pow')
        self.assertEqual(job.status, ScheduledJob.STATUS_SCHEDULED)

        with self.assertRaises(TypeError):
            run_jobs(now=datetime(1970, 1, 2))

        result_job = ScheduledJob.objects.get(pk=job.pk)
        self.assertEqual(result_job.status, ScheduledJob.STATUS_FAILED)
