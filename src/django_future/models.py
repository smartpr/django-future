from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from django.utils.translation import gettext_lazy as _

from picklefield import PickledObjectField


class ScheduledJob(models.Model):

    STATUS_SCHEDULED = 'scheduled'
    STATUS_RUNNING = 'running'
    STATUS_FAILED = 'failed'
    STATUS_COMPLETE = 'complete'
    STATUS_EXPIRED = 'expired'

    STATUSES = (
        (STATUS_SCHEDULED, _('Scheduled')),
        (STATUS_RUNNING, _('Running')),
        (STATUS_FAILED, _('Failed')),
        (STATUS_COMPLETE, _('Complete')),
        (STATUS_EXPIRED, _('Expired')),
    )

    time_slot_start = models.DateTimeField(_('time slot start'))
    time_slot_end = models.DateTimeField(_('time slot end'))

    execution_start = models.DateTimeField(
            _('execution start'), blank=True, null=True)

    status = models.CharField(
            _('status'), choices=STATUSES, max_length=32,
            default=STATUS_SCHEDULED)

    content_type = models.ForeignKey(
            ContentType, on_delete=models.CASCADE, blank=True, null=True,
            verbose_name=_('content type'))

    object_id = models.PositiveIntegerField(
            _('object ID'), blank=True, null=True)

    content_object = GenericForeignKey()

    callable_name = models.CharField(
            _('callable name'), max_length=255,
            help_text=_(
                'The callable to be executed may be specified in two ways: '
                'Set the callable name to an identifier '
                '(mypackage.myapp.some_function). Or specify an instance of a '
                'model as the content object and set the callable name to a '
                'method name (do_job).'))

    args = PickledObjectField(_('args'))

    kwargs = PickledObjectField(_('kwargs'))

    error = models.TextField(_('error'), blank=True, null=True)

    return_value = models.TextField(_('return value'), blank=True, null=True)

    class Meta:
        verbose_name = _('scheduled job')
        verbose_name_plural = _('scheduled jobs')
        get_latest_by = 'time_slot_start'
        ordering = ['time_slot_start']

        unique_together = [
            ('content_type', 'object_id'),
        ]

    def __repr__(self):
        return str(
                '<{} ({}) callable={!r}>'.format(
                    type(self).__name__, self.status, self.callable_name))

    def __str__(self):
        return str(self.callable_name)

    def run(self):
        """
        Invoke job
        """
        args = self.args or []
        kwargs = self.kwargs or {}

        if '.' in self.callable_name:
            module_name, function_name = self.callable_name.rsplit('.', 1)
            module = __import__(module_name, fromlist=[function_name])
            callable_func = getattr(module, function_name)
            if self.content_object is not None:
                args = [self.content_object] + list(args)
        else:
            callable_func = getattr(self.content_object, self.callable_name)

        if hasattr(callable_func, 'job_as_parameter'):
            args = [self] + list(args)

        return callable_func(*args, **kwargs)
