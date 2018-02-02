"""Run scheduled jobs."""

from django.core.management.base import BaseCommand, CommandError

from django_future.jobs import run_jobs


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '-d', '--delete-completed',
            action='store_true',
            dest='delete_completed',
            help='Do not keep entries for completed jobs in the database.'
        )

        parser.add_argument(
            '-i', '--ignore-errors',
            action='store_true',
            dest='ignore_errors',
            help='Do not abort if a job handler raises an error.'
        )

    def handle(self, **options):
        delete_completed = bool(options.get('delete_completed', False))
        ignore_errors = bool(options.get('ignore_errors', False))
        try:
            run_jobs(delete_completed=delete_completed,
                     ignore_errors=ignore_errors)
        except ValueError as e:
            raise CommandError(e)
