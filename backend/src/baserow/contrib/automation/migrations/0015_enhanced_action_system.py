# Generated migration for enhanced automation action system

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('automation', '0014_enhanced_trigger_system'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationActionNode',
            fields=[
                ('automationnode_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='automation.automationnode')),
                ('notification_type', models.CharField(choices=[('email', 'Email'), ('in_app', 'In-App Notification'), ('slack', 'Slack'), ('teams', 'Microsoft Teams'), ('webhook', 'Webhook')], default='email', max_length=50)),
                ('recipient_roles', models.JSONField(default=list, help_text="Roles to notify (e.g., ['admin', 'editor'])")),
                ('subject_template', models.TextField(blank=True, help_text='Template for notification subject/title')),
                ('message_template', models.TextField(help_text='Template for notification message body')),
                ('external_config', models.JSONField(default=dict, help_text='Configuration for external notification services')),
                ('recipient_users', models.ManyToManyField(blank=True, help_text='Specific users to notify', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=('automation.automationnode',),
        ),
        migrations.CreateModel(
            name='WebhookActionNode',
            fields=[
                ('automationnode_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='automation.automationnode')),
                ('url', models.URLField(help_text='Webhook URL to send the request to')),
                ('method', models.CharField(choices=[('GET', 'GET'), ('POST', 'POST'), ('PUT', 'PUT'), ('PATCH', 'PATCH'), ('DELETE', 'DELETE')], default='POST', max_length=10)),
                ('headers', models.JSONField(default=dict, help_text='HTTP headers to include in the request')),
                ('payload_template', models.TextField(blank=True, help_text='JSON template for the webhook payload')),
                ('authentication', models.JSONField(default=dict, help_text='Authentication configuration (API keys, OAuth, etc.)')),
                ('retry_config', models.JSONField(default=dict, help_text='Retry configuration for failed webhook calls')),
            ],
            options={
                'abstract': False,
            },
            bases=('automation.automationnode',),
        ),
        migrations.CreateModel(
            name='StatusChangeActionNode',
            fields=[
                ('automationnode_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='automation.automationnode')),
                ('target_field_id', models.PositiveIntegerField(help_text='ID of the field to update')),
                ('new_value_template', models.TextField(help_text='Template for the new field value')),
                ('condition_template', models.TextField(blank=True, help_text='Optional condition template to check before updating')),
            ],
            options={
                'abstract': False,
            },
            bases=('automation.automationnode',),
        ),
        migrations.CreateModel(
            name='ConditionalBranchNode',
            fields=[
                ('automationnode_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='automation.automationnode')),
                ('condition_template', models.TextField(help_text='Template for the condition to evaluate')),
                ('condition_type', models.CharField(choices=[('equals', 'Equals'), ('not_equals', 'Not Equals'), ('greater_than', 'Greater Than'), ('less_than', 'Less Than'), ('contains', 'Contains'), ('starts_with', 'Starts With'), ('ends_with', 'Ends With'), ('is_empty', 'Is Empty'), ('is_not_empty', 'Is Not Empty'), ('custom', 'Custom Expression')], default='equals', max_length=50)),
                ('comparison_value_template', models.TextField(blank=True, help_text='Template for the value to compare against')),
            ],
            options={
                'abstract': False,
            },
            bases=('automation.automationnode',),
        ),
        migrations.CreateModel(
            name='DelayActionNode',
            fields=[
                ('automationnode_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='automation.automationnode')),
                ('delay_type', models.CharField(choices=[('fixed', 'Fixed Duration'), ('until_date', 'Until Specific Date'), ('until_condition', 'Until Condition Met')], default='fixed', max_length=20)),
                ('delay_duration', models.DurationField(blank=True, help_text='Fixed delay duration', null=True)),
                ('delay_until_template', models.TextField(blank=True, help_text='Template for date/time to delay until')),
                ('condition_template', models.TextField(blank=True, help_text='Template for condition to wait for')),
                ('max_wait_duration', models.DurationField(blank=True, help_text='Maximum time to wait for condition', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('automation.automationnode',),
        ),
        migrations.CreateModel(
            name='WorkflowExecutionLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('execution_id', models.UUIDField(help_text='Unique identifier for this workflow execution')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('running', 'Running'), ('success', 'Success'), ('failed', 'Failed'), ('skipped', 'Skipped'), ('timeout', 'Timeout')], default='pending', max_length=20)),
                ('input_data', models.JSONField(default=dict, help_text='Input data for this execution step')),
                ('output_data', models.JSONField(default=dict, help_text='Output data from this execution step')),
                ('error_message', models.TextField(blank=True, help_text='Error message if execution failed')),
                ('execution_time_ms', models.PositiveIntegerField(blank=True, help_text='Execution time in milliseconds', null=True)),
                ('retry_count', models.PositiveIntegerField(default=0, help_text='Number of retry attempts')),
                ('node', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='execution_logs', to='automation.automationnode')),
                ('workflow', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='execution_logs', to='automation.automationworkflow')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ActionTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(help_text='Display name for the template', max_length=255)),
                ('description', models.TextField(help_text='Description of what this template does')),
                ('category', models.CharField(choices=[('notification', 'Notifications'), ('data_management', 'Data Management'), ('integration', 'Integrations'), ('workflow_control', 'Workflow Control'), ('reporting', 'Reporting')], default='notification', max_length=100)),
                ('template_config', models.JSONField(help_text='Configuration template for the action')),
                ('required_fields', models.JSONField(default=list, help_text='List of required field configurations')),
                ('is_system_template', models.BooleanField(default=False, help_text='Whether this is a built-in system template')),
                ('usage_count', models.PositiveIntegerField(default=0, help_text='Number of times this template has been used')),
                ('created_by', models.ForeignKey(blank=True, help_text='User who created this template', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-usage_count', 'name'],
            },
        ),
        migrations.AddIndex(
            model_name='workflowexecutionlog',
            index=models.Index(fields=['workflow', 'created_at'], name='automation_w_workflo_b8c123_idx'),
        ),
        migrations.AddIndex(
            model_name='workflowexecutionlog',
            index=models.Index(fields=['execution_id'], name='automation_w_executi_f8a456_idx'),
        ),
        migrations.AddIndex(
            model_name='workflowexecutionlog',
            index=models.Index(fields=['status', 'created_at'], name='automation_w_status_c9d789_idx'),
        ),
        migrations.AddIndex(
            model_name='actiontemplate',
            index=models.Index(fields=['category', 'usage_count'], name='automation_a_categor_e1f012_idx'),
        ),
        migrations.AddIndex(
            model_name='actiontemplate',
            index=models.Index(fields=['is_system_template'], name='automation_a_is_syst_a2b345_idx'),
        ),
    ]