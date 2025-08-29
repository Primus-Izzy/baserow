"""
Migration for mobile-specific features
"""

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PushSubscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('endpoint', models.URLField(max_length=500)),
                ('p256dh_key', models.CharField(max_length=255)),
                ('auth_key', models.CharField(max_length=255)),
                ('user_agent', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='push_subscriptions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'indexes': [
                    models.Index(fields=['user', 'is_active'], name='mobile_push_user_active_idx'),
                    models.Index(fields=['created_at'], name='mobile_push_created_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='PushNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_type', models.CharField(choices=[('comment', 'Comment'), ('mention', 'Mention'), ('update', 'Update'), ('reminder', 'Reminder'), ('system', 'System')], max_length=20)),
                ('title', models.CharField(max_length=255)),
                ('body', models.TextField()),
                ('data', models.JSONField(blank=True, default=dict)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('sent', 'Sent'), ('failed', 'Failed'), ('expired', 'Expired')], default='pending', max_length=20)),
                ('error_message', models.TextField(blank=True)),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('subscription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mobile.pushsubscription')),
            ],
            options={
                'indexes': [
                    models.Index(fields=['subscription', 'status'], name='mobile_notif_sub_status_idx'),
                    models.Index(fields=['created_at'], name='mobile_notif_created_idx'),
                    models.Index(fields=['notification_type'], name='mobile_notif_type_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='OfflineOperation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('operation_type', models.CharField(choices=[('create_row', 'Create Row'), ('update_row', 'Update Row'), ('delete_row', 'Delete Row'), ('update_field', 'Update Field'), ('create_view', 'Create View'), ('update_view', 'Update View')], max_length=20)),
                ('table_id', models.PositiveIntegerField(blank=True, null=True)),
                ('row_id', models.PositiveIntegerField(blank=True, null=True)),
                ('data', models.JSONField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('synced', 'Synced'), ('failed', 'Failed'), ('expired', 'Expired')], default='pending', max_length=20)),
                ('retry_count', models.PositiveIntegerField(default=0)),
                ('error_message', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('synced_at', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'indexes': [
                    models.Index(fields=['user', 'status'], name='mobile_offline_user_status_idx'),
                    models.Index(fields=['created_at'], name='mobile_offline_created_idx'),
                    models.Index(fields=['table_id'], name='mobile_offline_table_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='MobileSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notifications_enabled', models.BooleanField(default=True)),
                ('comment_notifications', models.BooleanField(default=True)),
                ('mention_notifications', models.BooleanField(default=True)),
                ('update_notifications', models.BooleanField(default=False)),
                ('high_contrast', models.BooleanField(default=False)),
                ('large_text', models.BooleanField(default=False)),
                ('reduced_motion', models.BooleanField(default=False)),
                ('screen_reader_announcements', models.BooleanField(default=True)),
                ('offline_mode_enabled', models.BooleanField(default=True)),
                ('auto_sync_enabled', models.BooleanField(default=True)),
                ('sync_on_wifi_only', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='mobile_settings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Mobile Settings',
                'verbose_name_plural': 'Mobile Settings',
            },
        ),
        migrations.CreateModel(
            name='CameraUpload',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_name', models.CharField(max_length=255)),
                ('file_size', models.PositiveIntegerField()),
                ('mime_type', models.CharField(max_length=100)),
                ('table_id', models.PositiveIntegerField(blank=True, null=True)),
                ('row_id', models.PositiveIntegerField(blank=True, null=True)),
                ('field_id', models.PositiveIntegerField(blank=True, null=True)),
                ('processed', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'indexes': [
                    models.Index(fields=['user', 'created_at'], name='mobile_camera_user_created_idx'),
                    models.Index(fields=['table_id', 'row_id'], name='mobile_camera_table_row_idx'),
                ],
            },
        ),
        migrations.AlterUniqueTogether(
            name='pushsubscription',
            unique_together={('user', 'endpoint')},
        ),
    ]