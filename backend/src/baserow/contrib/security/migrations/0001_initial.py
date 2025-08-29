# Generated migration for security models

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SecurityAuditLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.CharField(choices=[('login', 'User Login'), ('logout', 'User Logout'), ('failed_login', 'Failed Login Attempt'), ('password_change', 'Password Change'), ('permission_change', 'Permission Change'), ('data_access', 'Data Access'), ('data_export', 'Data Export'), ('data_deletion', 'Data Deletion'), ('api_access', 'API Access'), ('admin_action', 'Admin Action'), ('security_violation', 'Security Violation')], max_length=50)),
                ('severity', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')], default='low', max_length=20)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('details', models.JSONField(default=dict)),
                ('success', models.BooleanField(default=True)),
                ('content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'baserow_security_audit_log',
            },
        ),   
     migrations.CreateModel(
            name='EncryptedField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('table_id', models.PositiveIntegerField()),
                ('field_id', models.PositiveIntegerField()),
                ('row_id', models.PositiveIntegerField()),
                ('encrypted_value', models.BinaryField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'baserow_encrypted_fields',
            },
        ),
        migrations.CreateModel(
            name='GDPRRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_type', models.CharField(choices=[('export', 'Data Export'), ('deletion', 'Data Deletion'), ('rectification', 'Data Rectification'), ('portability', 'Data Portability'), ('consent_withdrawal', 'Consent Withdrawal')], max_length=50)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('requested_at', models.DateTimeField(auto_now_add=True)),
                ('processed_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('details', models.JSONField(default=dict)),
                ('export_file_path', models.CharField(blank=True, max_length=500)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'baserow_gdpr_requests',
            },
        ),
        migrations.CreateModel(
            name='ConsentRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('consent_type', models.CharField(choices=[('data_processing', 'Data Processing'), ('marketing', 'Marketing Communications'), ('analytics', 'Analytics'), ('third_party_sharing', 'Third Party Data Sharing')], max_length=50)),
                ('granted', models.BooleanField(default=False)),
                ('granted_at', models.DateTimeField(blank=True, null=True)),
                ('withdrawn_at', models.DateTimeField(blank=True, null=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'baserow_consent_records',
            },
        ),
        migrations.CreateModel(
            name='RateLimitRule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('endpoint_pattern', models.CharField(max_length=500)),
                ('method', models.CharField(blank=True, max_length=10)),
                ('requests_per_minute', models.PositiveIntegerField(default=60)),
                ('requests_per_hour', models.PositiveIntegerField(default=1000)),
                ('requests_per_day', models.PositiveIntegerField(default=10000)),
                ('user_specific', models.BooleanField(default=True)),
                ('ip_specific', models.BooleanField(default=True)),
                ('burst_allowance', models.PositiveIntegerField(default=10)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'baserow_rate_limit_rules',
            },
        ),
        migrations.CreateModel(
            name='RateLimitViolation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField()),
                ('endpoint', models.CharField(max_length=500)),
                ('method', models.CharField(max_length=10)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('requests_count', models.PositiveIntegerField()),
                ('rule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='baserow_security.ratelimitrule')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'baserow_rate_limit_violations',
            },
        ),
        # Add indexes
        migrations.AddIndex(
            model_name='securityauditlog',
            index=models.Index(fields=['timestamp'], name='baserow_security_audit_log_timestamp_idx'),
        ),
        migrations.AddIndex(
            model_name='securityauditlog',
            index=models.Index(fields=['user', 'timestamp'], name='baserow_security_audit_log_user_timestamp_idx'),
        ),
        migrations.AddIndex(
            model_name='securityauditlog',
            index=models.Index(fields=['event_type', 'timestamp'], name='baserow_security_audit_log_event_timestamp_idx'),
        ),
        migrations.AddIndex(
            model_name='securityauditlog',
            index=models.Index(fields=['severity', 'timestamp'], name='baserow_security_audit_log_severity_timestamp_idx'),
        ),
        migrations.AddIndex(
            model_name='encryptedfield',
            index=models.Index(fields=['table_id', 'row_id'], name='baserow_encrypted_fields_table_row_idx'),
        ),
        migrations.AddIndex(
            model_name='encryptedfield',
            index=models.Index(fields=['field_id'], name='baserow_encrypted_fields_field_idx'),
        ),
        migrations.AddIndex(
            model_name='gdprrequest',
            index=models.Index(fields=['user', 'requested_at'], name='baserow_gdpr_requests_user_requested_idx'),
        ),
        migrations.AddIndex(
            model_name='gdprrequest',
            index=models.Index(fields=['status', 'requested_at'], name='baserow_gdpr_requests_status_requested_idx'),
        ),
        migrations.AddIndex(
            model_name='consentrecord',
            index=models.Index(fields=['user', 'consent_type'], name='baserow_consent_records_user_type_idx'),
        ),
        migrations.AddIndex(
            model_name='consentrecord',
            index=models.Index(fields=['granted_at'], name='baserow_consent_records_granted_idx'),
        ),
        migrations.AddIndex(
            model_name='ratelimitrule',
            index=models.Index(fields=['endpoint_pattern'], name='baserow_rate_limit_rules_endpoint_idx'),
        ),
        migrations.AddIndex(
            model_name='ratelimitrule',
            index=models.Index(fields=['is_active'], name='baserow_rate_limit_rules_active_idx'),
        ),
        migrations.AddIndex(
            model_name='ratelimitviolation',
            index=models.Index(fields=['timestamp'], name='baserow_rate_limit_violations_timestamp_idx'),
        ),
        migrations.AddIndex(
            model_name='ratelimitviolation',
            index=models.Index(fields=['ip_address', 'timestamp'], name='baserow_rate_limit_violations_ip_timestamp_idx'),
        ),
        migrations.AddIndex(
            model_name='ratelimitviolation',
            index=models.Index(fields=['user', 'timestamp'], name='baserow_rate_limit_violations_user_timestamp_idx'),
        ),
        # Add unique constraints
        migrations.AddConstraint(
            model_name='encryptedfield',
            constraint=models.UniqueConstraint(fields=['table_id', 'field_id', 'row_id'], name='baserow_encrypted_fields_unique_table_field_row'),
        ),
        migrations.AddConstraint(
            model_name='consentrecord',
            constraint=models.UniqueConstraint(fields=['user', 'consent_type'], name='baserow_consent_records_unique_user_type'),
        ),
    ]