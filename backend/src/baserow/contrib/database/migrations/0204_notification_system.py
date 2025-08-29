# Generated migration for notification system

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0203_enhanced_form_view'),
        ('core', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('category', models.CharField(choices=[('collaboration', 'Collaboration'), ('automation', 'Automation'), ('system', 'System'), ('security', 'Security'), ('integration', 'Integration')], max_length=20)),
                ('description', models.TextField()),
                ('default_enabled', models.BooleanField(default=True)),
                ('supported_delivery_methods', models.JSONField(default=list)),
                ('template_variables', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'database_notification_type',
            },
        ),
        migrations.CreateModel(
            name='NotificationTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('delivery_method', models.CharField(max_length=20)),
                ('subject_template', models.TextField(blank=True)),
                ('body_template', models.TextField()),
                ('is_default', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('notification_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.notificationtype')),
                ('workspace', models.ForeignKey(blank=True, help_text='If null, this is a system-wide template', null=True, on_delete=django.db.models.deletion.CASCADE, to='core.workspace')),
            ],
            options={
                'db_table': 'database_notification_template',
            },
        ),
        migrations.CreateModel(
            name='UserNotificationPreference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('in_app_enabled', models.BooleanField(default=True)),
                ('email_enabled', models.BooleanField(default=True)),
                ('webhook_enabled', models.BooleanField(default=False)),
                ('slack_enabled', models.BooleanField(default=False)),
                ('teams_enabled', models.BooleanField(default=False)),
                ('email_batch_frequency', models.CharField(choices=[('immediate', 'Immediate'), ('hourly', 'Hourly'), ('daily', 'Daily'), ('weekly', 'Weekly')], default='immediate', max_length=20)),
                ('quiet_hours_enabled', models.BooleanField(default=False)),
                ('quiet_hours_start', models.TimeField(blank=True, null=True)),
                ('quiet_hours_end', models.TimeField(blank=True, null=True)),
                ('quiet_hours_timezone', models.CharField(default='UTC', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('notification_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.notificationtype')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('workspace', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.workspace')),
            ],
            options={
                'db_table': 'database_user_notification_preference',
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('title', models.CharField(max_length=255)),
                ('message', models.TextField()),
                ('data', models.JSONField(default=dict)),
                ('delivery_method', models.CharField(max_length=20)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('sent', 'Sent'), ('failed', 'Failed'), ('batched', 'Batched'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
                ('read_at', models.DateTimeField(blank=True, null=True)),
                ('batch_group', models.CharField(blank=True, max_length=100, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('notification_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.notificationtype')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('workspace', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.workspace')),
            ],
            options={
                'db_table': 'database_notification',
            },
        ),
        migrations.CreateModel(
            name='NotificationBatch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('delivery_method', models.CharField(max_length=20)),
                ('batch_key', models.CharField(max_length=100)),
                ('subject', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('notification_count', models.PositiveIntegerField(default=0)),
                ('scheduled_for', models.DateTimeField()),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('notification_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.notificationtype')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'database_notification_batch',
            },
        ),
        migrations.CreateModel(
            name='NotificationDeliveryLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('delivery_method', models.CharField(max_length=20)),
                ('status', models.CharField(max_length=20)),
                ('response_data', models.JSONField(default=dict)),
                ('error_message', models.TextField(blank=True)),
                ('attempted_at', models.DateTimeField(auto_now_add=True)),
                ('notification', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.notification')),
            ],
            options={
                'db_table': 'database_notification_delivery_log',
            },
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['recipient', 'status'], name='database_no_recipie_b8b8c8_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['batch_group'], name='database_no_batch_g_4c4b4a_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['created_at'], name='database_no_created_f8f8f8_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='usernotificationpreference',
            unique_together={('user', 'notification_type', 'workspace')},
        ),
        migrations.AlterUniqueTogether(
            name='notificationtemplate',
            unique_together={('notification_type', 'delivery_method', 'workspace')},
        ),
        migrations.AlterUniqueTogether(
            name='notificationbatch',
            unique_together={('recipient', 'batch_key', 'scheduled_for')},
        ),
    ]