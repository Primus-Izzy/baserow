# Generated migration for dashboard sharing and export functionality

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
        ('dashboard', '0004_enhanced_dashboard_widgets'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dashboard',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('layout', models.JSONField(default=dict)),
                ('permission_level', models.CharField(choices=[('private', 'Private'), ('workspace', 'Workspace Members'), ('public', 'Public')], default='private', max_length=20)),
                ('public_token', models.CharField(blank=True, max_length=64, null=True, unique=True)),
                ('embed_token', models.CharField(blank=True, max_length=64, null=True, unique=True)),
                ('export_settings', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_dashboards', to=settings.AUTH_USER_MODEL)),
                ('workspace', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dashboards', to='core.workspace')),
            ],
            options={
                'db_table': 'dashboard_dashboard',
            },
        ),
        migrations.CreateModel(
            name='DashboardWidget',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('widget_type', models.CharField(max_length=50)),
                ('configuration', models.JSONField(default=dict)),
                ('position', models.JSONField(default=dict)),
                ('embed_token', models.CharField(blank=True, max_length=64, null=True, unique=True)),
                ('is_embeddable', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('dashboard', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='widgets', to='dashboard.dashboard')),
            ],
            options={
                'db_table': 'dashboard_widget',
            },
        ),
        migrations.CreateModel(
            name='DashboardPermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('permission_type', models.CharField(choices=[('view', 'View'), ('edit', 'Edit'), ('admin', 'Admin')], max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('dashboard', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='permissions', to='dashboard.dashboard')),
                ('granted_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='granted_permissions', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'dashboard_permission',
            },
        ),
        migrations.CreateModel(
            name='DashboardExport',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('export_format', models.CharField(choices=[('pdf', 'PDF'), ('png', 'PNG'), ('csv', 'CSV')], max_length=10)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('configuration', models.JSONField(default=dict)),
                ('file_path', models.CharField(blank=True, max_length=500, null=True)),
                ('file_size', models.PositiveIntegerField(blank=True, null=True)),
                ('is_scheduled', models.BooleanField(default=False)),
                ('schedule_config', models.JSONField(default=dict)),
                ('next_run', models.DateTimeField(blank=True, null=True)),
                ('delivery_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('error_message', models.TextField(blank=True, null=True)),
                ('dashboard', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exports', to='dashboard.dashboard')),
                ('requested_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'dashboard_export',
            },
        ),
        migrations.AddConstraint(
            model_name='dashboardpermission',
            constraint=models.UniqueConstraint(fields=('dashboard', 'user'), name='unique_dashboard_user_permission'),
        ),
    ]