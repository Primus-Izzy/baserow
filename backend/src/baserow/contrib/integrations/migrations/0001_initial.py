# Generated migration for integrations

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
        ('database', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='IntegrationProvider',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('provider_type', models.CharField(choices=[('google', 'Google'), ('microsoft', 'Microsoft'), ('slack', 'Slack'), ('teams', 'Microsoft Teams'), ('dropbox', 'Dropbox'), ('email', 'Email')], max_length=50)),
                ('display_name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('icon_url', models.URLField(blank=True)),
                ('client_id', models.CharField(blank=True, max_length=500)),
                ('client_secret', models.TextField(blank=True)),
                ('authorization_url', models.URLField()),
                ('token_url', models.URLField()),
                ('scope', models.TextField()),
                ('api_base_url', models.URLField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'baserow_integration_provider',
            },
        ),       
 migrations.CreateModel(
            name='IntegrationConnection',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('access_token', models.TextField()),
                ('refresh_token', models.TextField(blank=True)),
                ('token_expires_at', models.DateTimeField(blank=True, null=True)),
                ('external_user_id', models.CharField(blank=True, max_length=200)),
                ('external_user_email', models.EmailField(blank=True, max_length=254)),
                ('external_user_name', models.CharField(blank=True, max_length=200)),
                ('status', models.CharField(choices=[('active', 'Active'), ('expired', 'Expired'), ('revoked', 'Revoked'), ('error', 'Error')], default='active', max_length=20)),
                ('last_sync_at', models.DateTimeField(blank=True, null=True)),
                ('error_message', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='integrations.integrationprovider')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='integration_connections', to='auth.user')),
                ('workspace', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='integration_connections', to='core.workspace')),
            ],
            options={
                'db_table': 'baserow_integration_connection',
            },
        ),
        migrations.CreateModel(
            name='IntegrationSync',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('sync_type', models.CharField(choices=[('calendar', 'Calendar Sync'), ('file_storage', 'File Storage'), ('notifications', 'Notifications'), ('data_import', 'Data Import'), ('data_export', 'Data Export')], max_length=50)),
                ('sync_direction', models.CharField(choices=[('bidirectional', 'Bidirectional'), ('import_only', 'Import Only'), ('export_only', 'Export Only')], default='bidirectional', max_length=20)),
                ('external_resource_id', models.CharField(max_length=500)),
                ('field_mappings', models.JSONField(default=dict)),
                ('sync_filters', models.JSONField(default=dict)),
                ('auto_sync_enabled', models.BooleanField(default=True)),
                ('sync_interval_minutes', models.PositiveIntegerField(default=15)),
                ('is_active', models.BooleanField(default=True)),
                ('last_sync_at', models.DateTimeField(blank=True, null=True)),
                ('last_sync_status', models.CharField(default='pending', max_length=20)),
                ('sync_error_message', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('connection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='syncs', to='integrations.integrationconnection')),
                ('table', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='integration_syncs', to='database.table')),
            ],
            options={
                'db_table': 'baserow_integration_sync',
            },
        ),
        migrations.CreateModel(
            name='IntegrationWebhook',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('webhook_url', models.URLField()),
                ('webhook_secret', models.CharField(max_length=100)),
                ('event_types', models.JSONField(default=list)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('connection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='webhooks', to='integrations.integrationconnection')),
            ],
            options={
                'db_table': 'baserow_integration_webhook',
            },
        ),
        migrations.CreateModel(
            name='IntegrationLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.CharField(choices=[('info', 'Info'), ('warning', 'Warning'), ('error', 'Error')], max_length=10)),
                ('message', models.TextField()),
                ('details', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('connection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='integrations.integrationconnection')),
            ],
            options={
                'db_table': 'baserow_integration_log',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='integrationconnection',
            constraint=models.UniqueConstraint(fields=('user', 'workspace', 'provider'), name='unique_user_workspace_provider'),
        ),
    ]