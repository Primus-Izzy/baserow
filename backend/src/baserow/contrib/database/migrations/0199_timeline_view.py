# Generated migration for Timeline/Gantt view with dependency management

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0198_kanban_view'),
    ]

    operations = [
        migrations.CreateModel(
            name='TimelineView',
            fields=[
                ('view_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='database.view')),
                ('timescale', models.CharField(choices=[('day', 'Day'), ('week', 'Week'), ('month', 'Month'), ('year', 'Year')], default='month', help_text='The timescale that the timeline should be displayed in', max_length=32)),
                ('enable_dependencies', models.BooleanField(default=False, help_text='Whether dependency tracking is enabled for this timeline view')),
                ('auto_reschedule', models.BooleanField(default=True, help_text='Whether dependent tasks should be automatically rescheduled when dependencies change')),
                ('enable_milestones', models.BooleanField(default=False, help_text='Whether milestone management is enabled for this timeline view')),
                ('end_date_field', models.ForeignKey(blank=True, help_text='Date field used as end date for timeline items', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='timeline_views_end_date_field', to='database.field')),
                ('start_date_field', models.ForeignKey(blank=True, help_text='Date field used as start date for timeline items', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='timeline_views_start_date_field', to='database.field')),
            ],
            options={
                'abstract': False,
            },
            bases=('database.view',),
        ),
        migrations.CreateModel(
            name='TimelineViewFieldOptions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hidden', models.BooleanField(default=True, help_text='Whether or not the field should be hidden in the timeline item')),
                ('order', models.SmallIntegerField(default=32767, help_text='The order that the field has in the timeline item')),
                ('show_in_timeline', models.BooleanField(default=True, help_text='Whether the field should be displayed in the timeline bar')),
                ('color_field', models.BooleanField(default=False, help_text='Whether this field should be used for color coding timeline items')),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.field')),
                ('timeline_view', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.timelineview')),
            ],
            options={
                'ordering': ('order', 'field_id'),
            },
        ),
        migrations.CreateModel(
            name='TimelineMilestone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of the milestone', max_length=255)),
                ('row_id', models.PositiveIntegerField(blank=True, help_text='Optional row ID if milestone is tied to a specific row', null=True)),
                ('color', models.CharField(default='#FF0000', help_text='Color for the milestone indicator in hex format', max_length=7)),
                ('icon', models.CharField(blank=True, help_text='Icon name for the milestone indicator', max_length=50)),
                ('description', models.TextField(blank=True, help_text='Optional description for the milestone')),
                ('is_active', models.BooleanField(default=True, help_text='Whether this milestone is currently active')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('date_field', models.ForeignKey(help_text='Date field that determines the milestone date', on_delete=django.db.models.deletion.CASCADE, to='database.field')),
                ('timeline_view', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='milestones', to='database.timelineview')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='TimelineDependency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('predecessor_row_id', models.PositiveIntegerField(help_text='ID of the row that must be completed first')),
                ('successor_row_id', models.PositiveIntegerField(help_text='ID of the row that depends on the predecessor')),
                ('dependency_type', models.CharField(choices=[('finish_to_start', 'Finish To Start'), ('start_to_start', 'Start To Start'), ('finish_to_finish', 'Finish To Finish'), ('start_to_finish', 'Start To Finish')], default='finish_to_start', help_text='Type of dependency relationship', max_length=20)),
                ('lag_days', models.IntegerField(default=0, help_text='Number of days to wait after dependency is met (can be negative for overlap)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('timeline_view', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dependencies', to='database.timelineview')),
            ],
        ),
        migrations.AddField(
            model_name='timelineview',
            name='field_options',
            field=models.ManyToManyField(through='database.TimelineViewFieldOptions', to='database.field'),
        ),
        migrations.AlterUniqueTogether(
            name='timelineviewfieldoptions',
            unique_together={('timeline_view', 'field')},
        ),
        migrations.AlterUniqueTogether(
            name='timelinemilestone',
            unique_together={('timeline_view', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='timelinedependency',
            unique_together={('timeline_view', 'predecessor_row_id', 'successor_row_id')},
        ),
        migrations.AddIndex(
            model_name='timelinedependency',
            index=models.Index(fields=['timeline_view', 'predecessor_row_id'], name='database_ti_timelin_b8e7c8_idx'),
        ),
        migrations.AddIndex(
            model_name='timelinedependency',
            index=models.Index(fields=['timeline_view', 'successor_row_id'], name='database_ti_timelin_4a9b2f_idx'),
        ),
    ]