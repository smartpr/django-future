from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from django_future.models import ScheduledJob


@admin.register(ScheduledJob)
class ScheduledJobAdmin(admin.ModelAdmin):
    """Admin customization for ScheduledJob model."""

    status_colors = {
        'default': '#000',
        'running': '#356AA0',
        'failed': '#B02B2C',
        'complete': '#006E2E',
        'expired': '#888'
    }

    def colorful_status(self, obj):
        if obj.status in self.status_colors:
            color = self.status_colors[obj.status]
        else:
            color = self.status_colors['default']
        return format_html(
            '<strong style="color: {0}">{1}</strong>',
            color, obj.get_status_display()
        )
    colorful_status.short_description = 'Status'

    list_display = (
        'time_slot_start',
        'colorful_status',
        'object_id',
        'content_object',
    )

    list_filter = ('status',)

    date_hierarchy = 'time_slot_start'

    fieldsets = (
        (None, {
            'fields': ('status',)
        }),
        (_('Schedule'), {
            'fields': ('time_slot_start', 'time_slot_end', 'execution_start')
        }),
        (_('Job'), {
            'fields': (
                'callable_name',
                ('content_type', 'object_id'),
                'error',
                'return_value'
            ),
        }),
    )
