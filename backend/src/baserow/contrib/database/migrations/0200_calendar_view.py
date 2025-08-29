# Generated migration for Calendar view implementation

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0199_timeline_view'),
    ]

    operations = [
        migrations.CreateModel(
            name='CalendarView',
            fields=[
                ('view_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='database.view')),
                ('display_mode', models.CharField(choices=[('month', 'Monthly'), ('week', 'Weekly'), ('day', 'Daily')], default='month', help_text='Default display mode for the calendar view', max_length=20)),
                ('enable_recurring_events', models.BooleanField(default=False, help_text='Whether recurring event patterns are enabled')),
                ('external_calendar_config', models.JSONField(blank=True, default=dict, help_text='Configuration for external calendar integrations (Google Calendar, Outlook)')),
                ('enable_external_sync', models.BooleanField(default=False, help_text='Whether bi-directional sync with external calendars is enabled')),
                ('date_field', models.ForeignKey(blank=True, help_text='Date field used to position events on the calendar', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='calendar_view_date_field', to='database.field')),
                ('event_color_field', models.ForeignKey(blank=True, help_text='Field used to determine event colors', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='calendar_view_color_field', to='database.field')),
                ('event_title_field', models.ForeignKey(blank=True, help_text='Field used as the event title', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='calendar_view_title_field', to='database.field')),
                ('field_options', models.ManyToManyField(through='database.CalendarViewFieldOptions', to='database.field')),
                ('recurring_pattern_field', models.ForeignKey(blank=True, help_text='Field containing recurring event pattern configuration', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='calendar_view_recurring_pattern_field', to='database.field')),
            ],
            options={
                'abstract': False,
            },
            bases=('database.view',),
        ),
        migrations.CreateModel(
            name='CalendarViewFieldOptions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hidden', models.BooleanField(default=True, help_text='Whether or not the field should be hidden in the event display.')),
                ('order', models.SmallIntegerField(default=32767, help_text='The order that the field has in the event display. Lower value is first.')),
                ('show_in_event', models.BooleanField(default=False, help_text='Whether the field should be visible in the event popup/details.')),
                ('event_display_style', models.CharField(default='default', help_text='How the field should be displayed in the event (default, compact, badge).', max_length=50)),
                ('calendar_view', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.calendarview')),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.field')),
            ],
            options={
                'ordering': ('order', 'field_id'),
            },
        ),
        migrations.CreateModel(
            name='CalendarRecurringPattern',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('row_id', models.PositiveIntegerField(help_text='ID of the row this pattern applies to')),
                ('pattern_type', models.CharField(choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly'), ('yearly', 'Yearly'), ('custom', 'Custom')], help_text='Type of recurring pattern', max_length=20)),
                ('interval', models.PositiveIntegerField(default=1, help_text='Interval between recurrences (e.g., every 2 weeks)')),
                ('days_of_week', models.JSONField(blank=True, default=list, help_text='Days of week for weekly patterns (0=Monday, 6=Sunday)')),
                ('end_date', models.DateField(blank=True, help_text='End date for the recurring pattern', null=True)),
                ('max_occurrences', models.PositiveIntegerField(blank=True, help_text='Maximum number of occurrences', null=True)),
                ('exceptions', models.JSONField(blank=True, default=list, help_text='List of dates to exclude from the pattern')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('calendar_view', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recurring_patterns', to='database.calendarview')),
            ],
        ),
        migrations.CreateModel(
            name='CalendarExternalSync',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('provider', models.CharField(choices=[('google', 'Google Calendar'), ('outlook', 'Microsoft Outlook'), ('ical', 'iCal/CalDAV')], help_text='External calendar provider', max_length=50)),
                ('external_calendar_id', models.CharField(help_text='ID of the external calendar', max_length=255)),
                ('sync_token', models.TextField(blank=True, help_text='Token for incremental sync')),
                ('last_sync', models.DateTimeField(blank=True, help_text='Last successful sync timestamp', null=True)),
                ('sync_direction', models.CharField(choices=[('import', 'Import Only'), ('export', 'Export Only'), ('bidirectional', 'Bi-directional')], default='bidirectional', help_text='Direction of synchronization', max_length=20)),
                ('is_active', models.BooleanField(default=True, help_text='Whether this sync is active')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('calendar_view', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='external_syncs', to='database.calendarview')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='calendarviewfieldoptions',
            unique_together={('calendar_view', 'field')},
        ),
        migrations.AlterUniqueTogether(
            name='calendarrecurringpattern',
            unique_together={('calendar_view', 'row_id')},
        ),
        migrations.AlterUniqueTogether(
            name='calendarexternalsync',
            unique_together={('calendar_view', 'provider', 'external_calendar_id')},
        ),
    ]