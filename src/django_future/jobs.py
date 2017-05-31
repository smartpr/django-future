"""Django-future -- scheduled jobs in Django."""

import datetime
import traceback

from django.core import exceptions
from django.db import transaction
from django.utils import timezone

from django_future.models import ScheduledJob
from django_future.utils import parse_timedelta


__all__ = ['schedule_job', 'job_as_parameter', 'run_jobs']


def schedule_job(date, callable_name, content_object=None, expires='7d',
                 args=(), kwargs={}):
    """
    Schedule a job.

    `date` may be a datetime.datetime or a datetime.timedelta.

    The callable to be executed may be specified in two ways:
     - set `callable_name` to an identifier ('mypackage.myapp.some_function').
     - specify an instance of a model as content_object and set
       `callable_name` to a method name ('do_job')

    The scheduler will not attempt to run the job if its expiration date has
    passed.
    """
    # TODO: allow to pass in a real callable, but check that it's a global
    assert callable_name \
        and isinstance(callable_name, basestring), callable_name

    if isinstance(date, basestring):
        date = parse_timedelta(date)

    if isinstance(date, datetime.timedelta):
        date = timezone.now() + date

    job = ScheduledJob(callable_name=callable_name, time_slot_start=date)

    if expires:
        if isinstance(expires, basestring):
            expires = parse_timedelta(expires)
        if isinstance(expires, datetime.timedelta):
            expires = date + expires
        job.time_slot_end = expires

    if content_object:
        job.content_object = content_object

    job.args = args
    job.kwargs = kwargs
    job.save()
    return job


def job_as_parameter(f):
    """A decorator for job handlers that take the job as a parameter."""
    f.job_as_parameter = True
    return f


def _expire_jobs(expire_at):
    """
    Flag scheduled jobs as expired
    """
    ScheduledJob.objects.filter(
        status=ScheduledJob.STATUS_SCHEDULED,
        time_slot_end__lt=expire_at
    ).update(status=ScheduledJob.STATUS_EXPIRED)


def _run_scheduled_job(job, delete_completed, ignore_errors):
    """
    Assumes we're running with AUTOCOMMIT=True (Default)
    """
    # Mark job as running
    job.status = ScheduledJob.STATUS_RUNNING
    job.execution_start = timezone.now()
    job.save()

    # Run job
    try:
        return_value = job.run()
    except Exception:
        #  Mark job as failed on exception
        job.error = traceback.format_exc()
        job.status = ScheduledJob.STATUS_FAILED
        job.save()

        if not ignore_errors:
            raise
    else:
        # Mark job completed or delete
        if delete_completed:
            job.delete()
        else:
            job.status = ScheduledJob.STATUS_COMPLETE
            if return_value is not None:
                job.return_value = unicode(return_value)
            else:
                job.return_value = None
            job.save()


def _run_scheduled_jobs(run_at, delete_completed, ignore_errors):
    """
    The following code requires autocommit mode to be enabled. (Django's
    default)
    """
    if not transaction.get_autocommit():
        raise exceptions.ImproperlyConfigured("Expecting AUTOCOMMIT=True")

    # Issue a commit to ensure there is no open transaction
    transaction.commit()

    # Fetch scheduled jobs.
    scheduled_jobs = ScheduledJob.objects.filter(
            status=ScheduledJob.STATUS_SCHEDULED,
            time_slot_start__lte=run_at)

    for job in scheduled_jobs:
        _run_scheduled_job(job, delete_completed, ignore_errors)


def run_jobs(delete_completed=False, ignore_errors=False, now=None):
    """
    Run scheduled jobs.

    You may specify a date to be treated as the current time.
    """
    running_jobs = ScheduledJob.objects.filter(
            status=ScheduledJob.STATUS_RUNNING)
    if running_jobs.exists():
        raise ValueError('jobs in progress found; aborting')

    if now is None:
        now = timezone.now()

    _expire_jobs(now)
    _run_scheduled_jobs(now, delete_completed, ignore_errors)
