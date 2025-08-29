"""
Migration for enhanced automation trigger system.

This migration adds new trigger types including date-based triggers,
linked record change triggers, webhook triggers, conditional triggers,
and trigger templates.
"""

from django.db import migrations, models
import django.db.models.deletion
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('automation', '0013_apply_previous_node_ids'),
        ('database', '0200_calendar_view'),  # Ensure database migrations are applied
    ]

    operations = [
        # Create DateBasedTriggerNode
        migrations.CreateModel(
            name='DateBasedTriggerNode',
            fields=[
                ('automationnode_ptr', models.OneToOneField(
                    auto_created=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    parent_link=True,
                    primary_key=True,
                    serialize=False,
                    to='automation.automationnode'
                )),
                ('condition_type', models.CharField(
                    choices=[
                        ('date_reached', 'Date Reached'),
                        ('days_before', 'Days Before Date'),
                        ('days_after', 'Days After Date'),
                        ('recurring', 'Recurring Pattern'),
                        ('overdue', 'Overdue Items'),
                    ],
                    default='date_reached',
                    help_text='Type of date condition to trigger on',
                    max_length=20
                )),
                ('days_offset', models.IntegerField(
                    default=0,
                    help_text='Number of days before/after the date field value'
                )),
                ('recurring_pattern', models.JSONField(
                    blank=True,
                    default=dict,
                    help_text='Configuration for recurring triggers (daily, weekly, monthly, etc.)'
                )),
                ('check_time', models.TimeField(
                    blank=True,
                    help_text='Time of day to check the trigger condition',
                    null=True
                )),
                ('additional_conditions', models.JSONField(
                    blank=True,
                    default=dict,
                    help_text='Additional field-based conditions that must be met'
                )),
                ('date_field', models.ForeignKey(
                    help_text='The date field to monitor for trigger conditions',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='date_trigger_nodes',
                    to='database.field'
                )),
            ],
            options={
                'abstract': False,
            },
            bases=('automation.automationnode',),
        ),

        # Create LinkedRecordChangeTriggerNode
        migrations.CreateModel(
            name='LinkedRecordChangeTriggerNode',
            fields=[
                ('automationnode_ptr', models.OneToOneField(
                    auto_created=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    parent_link=True,
                    primary_key=True,
                    serialize=False,
                    to='automation.automationnode'
                )),
                ('change_type', models.CharField(
                    choices=[
                        ('linked_record_created', 'Linked Record Created'),
                        ('linked_record_updated', 'Linked Record Updated'),
                        ('linked_record_deleted', 'Linked Record Deleted'),
                        ('link_added', 'Link Added'),
                        ('link_removed', 'Link Removed'),
                        ('any_change', 'Any Change in Linked Records'),
                    ],
                    default='any_change',
                    help_text='Type of change to monitor in linked records',
                    max_length=25
                )),
                ('monitored_fields', models.JSONField(
                    blank=True,
                    default=list,
                    help_text='Specific fields in the linked table to monitor for changes'
                )),
                ('linked_record_conditions', models.JSONField(
                    blank=True,
                    default=dict,
                    help_text='Conditions that linked records must meet to trigger'
                )),
                ('link_field', models.ForeignKey(
                    help_text='The link row field to monitor for changes',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='link_trigger_nodes',
                    to='database.field'
                )),
            ],
            options={
                'abstract': False,
            },
            bases=('automation.automationnode',),
        ),

        # Create WebhookTriggerNode
        migrations.CreateModel(
            name='WebhookTriggerNode',
            fields=[
                ('automationnode_ptr', models.OneToOneField(
                    auto_created=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    parent_link=True,
                    primary_key=True,
                    serialize=False,
                    to='automation.automationnode'
                )),
                ('webhook_url_path', models.CharField(
                    help_text='Unique URL path for this webhook trigger',
                    max_length=255,
                    unique=True
                )),
                ('auth_type', models.CharField(
                    choices=[
                        ('none', 'No Authentication'),
                        ('api_key', 'API Key'),
                        ('bearer_token', 'Bearer Token'),
                        ('signature', 'Signature Verification'),
                    ],
                    default='api_key',
                    help_text='Authentication method for webhook requests',
                    max_length=15
                )),
                ('auth_token', models.CharField(
                    blank=True,
                    help_text='Authentication token for webhook requests',
                    max_length=255
                )),
                ('signature_secret', models.CharField(
                    blank=True,
                    help_text='Secret key for signature verification',
                    max_length=255
                )),
                ('allowed_methods', models.JSONField(
                    default=list,
                    help_text='HTTP methods allowed for this webhook (GET, POST, PUT, etc.)'
                )),
                ('payload_mapping', models.JSONField(
                    blank=True,
                    default=dict,
                    help_text='Mapping of webhook payload fields to automation context'
                )),
                ('validation_rules', models.JSONField(
                    blank=True,
                    default=dict,
                    help_text='Rules to validate incoming webhook requests'
                )),
            ],
            options={
                'abstract': False,
            },
            bases=('automation.automationnode',),
        ),

        # Create ConditionalTriggerNode
        migrations.CreateModel(
            name='ConditionalTriggerNode',
            fields=[
                ('automationnode_ptr', models.OneToOneField(
                    auto_created=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    parent_link=True,
                    primary_key=True,
                    serialize=False,
                    to='automation.automationnode'
                )),
                ('condition_groups', models.JSONField(
                    default=list,
                    help_text='Groups of conditions with AND/OR logic'
                )),
                ('evaluation_mode', models.CharField(
                    choices=[
                        ('all_must_match', 'All Conditions Must Match (AND)'),
                        ('any_can_match', 'Any Condition Can Match (OR)'),
                        ('custom_logic', 'Custom Logic Expression'),
                    ],
                    default='all_must_match',
                    help_text='How to evaluate multiple condition groups',
                    max_length=20
                )),
                ('custom_logic', models.TextField(
                    blank=True,
                    help_text='Custom logic expression using condition group IDs'
                )),
                ('time_conditions', models.JSONField(
                    blank=True,
                    default=dict,
                    help_text='Time-based conditions (business hours, weekdays, etc.)'
                )),
                ('base_trigger', models.ForeignKey(
                    help_text='Base trigger node to add conditions to',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='conditional_extensions',
                    to='automation.automationnode'
                )),
            ],
            options={
                'abstract': False,
            },
            bases=('automation.automationnode',),
        ),

        # Create TriggerTemplate
        migrations.CreateModel(
            name='TriggerTemplate',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID'
                )),
                ('name', models.CharField(
                    help_text='Display name for the trigger template',
                    max_length=255
                )),
                ('description', models.TextField(
                    help_text='Description of what this template does'
                )),
                ('category', models.CharField(
                    choices=[
                        ('project_management', 'Project Management'),
                        ('notifications', 'Notifications'),
                        ('data_sync', 'Data Synchronization'),
                        ('reporting', 'Reporting'),
                        ('approval_workflows', 'Approval Workflows'),
                        ('maintenance', 'Maintenance Tasks'),
                        ('custom', 'Custom'),
                    ],
                    default='custom',
                    help_text='Category for organizing templates',
                    max_length=25
                )),
                ('trigger_config', models.JSONField(
                    help_text='Configuration template for the trigger'
                )),
                ('action_templates', models.JSONField(
                    default=list,
                    help_text='Templates for actions that commonly go with this trigger'
                )),
                ('required_field_types', models.JSONField(
                    default=list,
                    help_text='Field types required in the table to use this template'
                )),
                ('is_active', models.BooleanField(
                    default=True,
                    help_text='Whether this template is available for use'
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('usage_count', models.IntegerField(
                    default=0,
                    help_text='Number of times this template has been used'
                )),
            ],
            options={
                'ordering': ['category', 'name'],
            },
        ),

        # Create WebhookRequestLog for tracking webhook requests (optional)
        migrations.CreateModel(
            name='WebhookRequestLog',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID'
                )),
                ('webhook_path', models.CharField(max_length=255)),
                ('method', models.CharField(max_length=10)),
                ('headers', models.JSONField(default=dict)),
                ('payload', models.JSONField(default=dict)),
                ('response_status', models.IntegerField()),
                ('response_data', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('webhook_trigger', models.ForeignKey(
                    null=True,
                    blank=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='request_logs',
                    to='automation.webhooktriggernode'
                )),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),

        # Add indexes for performance
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_date_trigger_date_field ON automation_datebasedtriggernode (date_field_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_date_trigger_date_field;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_link_trigger_link_field ON automation_linkedrecordchangetriggernode (link_field_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_link_trigger_link_field;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_webhook_trigger_path ON automation_webhooktriggernode (webhook_url_path);",
            reverse_sql="DROP INDEX IF EXISTS idx_webhook_trigger_path;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_trigger_template_category ON automation_triggertemplate (category);",
            reverse_sql="DROP INDEX IF EXISTS idx_trigger_template_category;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_webhook_log_created ON automation_webhookrequestlog (created_at);",
            reverse_sql="DROP INDEX IF EXISTS idx_webhook_log_created;"
        ),
    ]