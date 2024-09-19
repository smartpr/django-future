from django.db import models, migrations
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScheduledJob',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time_slot_start', models.DateTimeField(verbose_name='time slot start')),
                ('time_slot_end', models.DateTimeField(verbose_name='time slot end')),
                ('execution_start', models.DateTimeField(null=True, verbose_name='execution start', blank=True)),
                ('status', models.CharField(default='scheduled', max_length=32, verbose_name='status', choices=[('scheduled', 'Scheduled'), ('running', 'Running'), ('failed', 'Failed'), ('complete', 'Complete'), ('expired', 'Expired')])),
                ('object_id', models.PositiveIntegerField(null=True, verbose_name='object ID', blank=True)),
                ('callable_name', models.CharField(help_text='The callable to be executed may be specified in two ways: Set the callable name to an identifier (mypackage.myapp.some_function). Or specify an instance of a model as the content object and set the callable name to a method name (do_job).', max_length=255, verbose_name='callable name')),
                ('args', picklefield.fields.PickledObjectField(verbose_name='args', editable=False)),
                ('kwargs', picklefield.fields.PickledObjectField(verbose_name='kwargs', editable=False)),
                ('error', models.TextField(null=True, verbose_name='error', blank=True)),
                ('return_value', models.TextField(null=True, verbose_name='return value', blank=True)),
                ('content_type', models.ForeignKey(on_delete=models.CASCADE, verbose_name='content type', blank=True, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'ordering': ['time_slot_start'],
                'get_latest_by': 'time_slot_start',
                'verbose_name': 'scheduled job',
                'verbose_name_plural': 'scheduled jobs',
            },
            bases=(models.Model,),
        ),
    ]
