# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-08-09 07:50
from django.db import migrations


def populate_mailing_refs(apps, schema_editor):
    # Retrieve content type for Mailing model
    # Note: the ContentType table is empty when running migrations for the
    # first time, like when setting up new virtual machines or running tests.
    # In this case we cannot continue and the data migration may safely be
    # aborted: there is no data to migrate anyway.
    ContentType = apps.get_model('contenttypes', 'ContentType')
    mailing_ct = ContentType.objects.filter(app_label='communication', model='Mailing').first()
    if mailing_ct is None:
        return

    ScheduledJob = apps.get_model('django_future', 'ScheduledJob')
    Mailing = apps.get_model('communication', 'Mailing')

    for job in ScheduledJob.objects.all():
        mailing_id = job.args[0]

        try:
            mailing = Mailing.objects.get(id=mailing_id)
        except Mailing.DoesNotExist:
            # The Mailing referred to by the ScheduledJob, does not exist
            job.delete()
        else:
            # The Mailing referred to by the ScheduledJob, does not refer to
            # the same ScheduledJob
            if not mailing.scheduled_job or mailing.scheduled_job.id != job.id:
                job.delete()
            else:
                job.content_type = mailing_ct
                job.object_id = mailing_id
                job.save()


class Migration(migrations.Migration):
    dependencies = [
        ('django_future', '0001_initial'),
    ]

    operations = [
            migrations.RunPython(populate_mailing_refs),
    ]
