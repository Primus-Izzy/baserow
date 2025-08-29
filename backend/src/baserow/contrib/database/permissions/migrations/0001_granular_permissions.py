"""
Migration for granular permission system models.
"""

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import baserow.core.mixins


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('database', '0195_initial_enhanced_grid_view'),  # Adjust based on latest database migration
        ('core', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(help_text='Name of the custom role', max_length=255)),
                ('description', models.TextField(blank=True, help_text='Optional description of the role')),
                ('can_create_tables', models.BooleanField(default=False, help_text='Can create new tables')),
                ('can_delete_tables', models.BooleanField(default=False, help_text='Can delete tables')),
                ('can_create_views', models.BooleanField(default=True, help_text='Can create new views')),
                ('can_manage_workspace', models.BooleanField(default=False, help_text='Can manage workspace settings and users')),
                ('created_by', models.ForeignKey(help_text='User who created this role', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('workspace', models.ForeignKey(help_text='Workspace this role belongs to', on_delete=django.db.models.deletion.CASCADE, related_name='custom_roles', to='core.workspace')),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(baserow.core.mixins.CreatedAndUpdatedOnMixin, models.Model),
        ),
        migrations.CreateModel(
            name='UserRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assigned_at', models.DateTimeField(auto_now_add=True)),
                ('assigned_by', models.ForeignKey(help_text='User who assigned this role', on_delete=django.db.models.deletion.CASCADE, related_name='assigned_roles', to=settings.AUTH_USER_MODEL)),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='permissions.customrole')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('workspace', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.workspace')),
            ],
            options={
                'ordering': ['assigned_at'],
            },
        ),
        migrations.CreateModel(
            name='TablePermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('permission_level', models.CharField(choices=[('NONE', 'No access'), ('READ', 'Read only'), ('UPDATE', 'Read and update'), ('CREATE', 'Read, update, and create'), ('DELETE', 'Full access including delete')], default='READ', help_text='Permission level for this table', max_length=10)),
                ('can_create_rows', models.BooleanField(default=True)),
                ('can_update_rows', models.BooleanField(default=True)),
                ('can_delete_rows', models.BooleanField(default=False)),
                ('can_create_fields', models.BooleanField(default=False)),
                ('can_update_fields', models.BooleanField(default=False)),
                ('can_delete_fields', models.BooleanField(default=False)),
                ('can_create_views', models.BooleanField(default=True)),
                ('can_update_views', models.BooleanField(default=True)),
                ('can_delete_views', models.BooleanField(default=False)),
                ('role', models.ForeignKey(blank=True, help_text='Custom role (if null, applies to user)', null=True, on_delete=django.db.models.deletion.CASCADE, to='permissions.customrole')),
                ('table', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='table_permissions', to='database.table')),
                ('user', models.ForeignKey(blank=True, help_text='Specific user (if null, applies to role)', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            bases=(baserow.core.mixins.CreatedAndUpdatedOnMixin, models.Model),
        ),
        migrations.CreateModel(
            name='FieldPermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('permission_level', models.CharField(choices=[('NONE', 'No access'), ('READ', 'Read only'), ('UPDATE', 'Read and update'), ('CREATE', 'Read, update, and create'), ('DELETE', 'Full access including delete')], default='READ', help_text='Permission level for this field', max_length=10)),
                ('can_read', models.BooleanField(default=True)),
                ('can_update', models.BooleanField(default=True)),
                ('is_hidden', models.BooleanField(default=False, help_text='Hide field from user interface')),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='field_permissions', to='database.field')),
                ('role', models.ForeignKey(blank=True, help_text='Custom role (if null, applies to user)', null=True, on_delete=django.db.models.deletion.CASCADE, to='permissions.customrole')),
                ('user', models.ForeignKey(blank=True, help_text='Specific user (if null, applies to role)', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            bases=(baserow.core.mixins.CreatedAndUpdatedOnMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ViewPermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('permission_level', models.CharField(choices=[('NONE', 'No access'), ('READ', 'Read only'), ('UPDATE', 'Read and update'), ('CREATE', 'Read, update, and create'), ('DELETE', 'Full access including delete')], default='READ', help_text='Permission level for this view', max_length=10)),
                ('can_read', models.BooleanField(default=True)),
                ('can_update', models.BooleanField(default=False)),
                ('can_delete', models.BooleanField(default=False)),
                ('is_hidden', models.BooleanField(default=False, help_text='Hide view from user interface')),
                ('role', models.ForeignKey(blank=True, help_text='Custom role (if null, applies to user)', null=True, on_delete=django.db.models.deletion.CASCADE, to='permissions.customrole')),
                ('user', models.ForeignKey(blank=True, help_text='Specific user (if null, applies to role)', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('view', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='view_permissions', to='database.view')),
            ],
            bases=(baserow.core.mixins.CreatedAndUpdatedOnMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ConditionalPermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(help_text='Descriptive name for this conditional permission', max_length=255)),
                ('condition_operator', models.CharField(choices=[('equals', 'Equals'), ('not_equals', 'Not equals'), ('contains', 'Contains'), ('not_contains', 'Does not contain'), ('greater_than', 'Greater than'), ('less_than', 'Less than'), ('is_empty', 'Is empty'), ('is_not_empty', 'Is not empty')], help_text='Operator for condition evaluation', max_length=20)),
                ('condition_value', models.TextField(blank=True, help_text='Value to compare against (JSON for complex values)')),
                ('user_attribute_field', models.CharField(blank=True, choices=[('email', 'Email'), ('username', 'Username'), ('first_name', 'First name'), ('last_name', 'Last name'), ('is_staff', 'Is staff'), ('date_joined', 'Date joined')], help_text='User attribute to check (optional)', max_length=50)),
                ('user_attribute_operator', models.CharField(blank=True, choices=[('equals', 'Equals'), ('contains', 'Contains'), ('starts_with', 'Starts with'), ('ends_with', 'Ends with')], help_text='Operator for user attribute condition', max_length=20)),
                ('user_attribute_value', models.TextField(blank=True, help_text='Value to compare user attribute against')),
                ('granted_permission_level', models.CharField(choices=[('NONE', 'No access'), ('READ', 'Read only'), ('UPDATE', 'Read and update'), ('CREATE', 'Read, update, and create'), ('DELETE', 'Full access including delete')], default='READ', help_text='Permission level granted when condition is met', max_length=10)),
                ('can_read', models.BooleanField(default=True)),
                ('can_update', models.BooleanField(default=False)),
                ('can_delete', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True, help_text='Whether this conditional permission is active')),
                ('condition_field', models.ForeignKey(help_text='Field to evaluate for condition', on_delete=django.db.models.deletion.CASCADE, to='database.field')),
                ('role', models.ForeignKey(blank=True, help_text='Custom role (if null, applies to user)', null=True, on_delete=django.db.models.deletion.CASCADE, to='permissions.customrole')),
                ('table', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conditional_permissions', to='database.table')),
                ('user', models.ForeignKey(blank=True, help_text='Specific user (if null, applies to role)', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            bases=(baserow.core.mixins.CreatedAndUpdatedOnMixin, models.Model),
        ),
        migrations.CreateModel(
            name='RowPermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('row_id', models.PositiveIntegerField(help_text='ID of the specific row')),
                ('permission_level', models.CharField(choices=[('NONE', 'No access'), ('READ', 'Read only'), ('UPDATE', 'Read and update'), ('CREATE', 'Read, update, and create'), ('DELETE', 'Full access including delete')], default='READ', help_text='Permission level for this row', max_length=10)),
                ('can_read', models.BooleanField(default=True)),
                ('can_update', models.BooleanField(default=False)),
                ('can_delete', models.BooleanField(default=False)),
                ('is_hidden', models.BooleanField(default=False, help_text='Hide row from user interface')),
                ('role', models.ForeignKey(blank=True, help_text='Custom role (if null, applies to user)', null=True, on_delete=django.db.models.deletion.CASCADE, to='permissions.customrole')),
                ('table', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='row_permissions', to='database.table')),
                ('user', models.ForeignKey(blank=True, help_text='Specific user (if null, applies to role)', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            bases=(baserow.core.mixins.CreatedAndUpdatedOnMixin, models.Model),
        ),
        migrations.CreateModel(
            name='APIKey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(help_text='Descriptive name for this API key', max_length=255)),
                ('key', models.CharField(help_text='The actual API key', max_length=255, unique=True)),
                ('can_read', models.BooleanField(default=True)),
                ('can_create', models.BooleanField(default=False)),
                ('can_update', models.BooleanField(default=False)),
                ('can_delete', models.BooleanField(default=False)),
                ('rate_limit_per_minute', models.PositiveIntegerField(default=60, help_text='Maximum requests per minute')),
                ('allowed_ip_addresses', models.TextField(blank=True, help_text='Comma-separated list of allowed IP addresses (empty = all IPs)')),
                ('is_active', models.BooleanField(default=True, help_text='Whether this API key is active')),
                ('expires_at', models.DateTimeField(blank=True, help_text='Optional expiration date for this API key', null=True)),
                ('last_used_at', models.DateTimeField(blank=True, help_text='Last time this API key was used', null=True)),
                ('created_by', models.ForeignKey(help_text='User who created this API key', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('scope_tables', models.ManyToManyField(blank=True, help_text='Tables this API key has access to (empty = all tables)', to='database.table')),
                ('scope_views', models.ManyToManyField(blank=True, help_text='Views this API key has access to (empty = all views)', to='database.view')),
                ('workspace', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='api_keys', to='core.workspace')),
            ],
            options={
                'ordering': ['-created_on'],
            },
            bases=(baserow.core.mixins.CreatedAndUpdatedOnMixin, models.Model),
        ),
        # Add constraints
        migrations.AddConstraint(
            model_name='customrole',
            constraint=models.UniqueConstraint(fields=('workspace', 'name'), name='unique_role_per_workspace'),
        ),
        migrations.AddConstraint(
            model_name='userrole',
            constraint=models.UniqueConstraint(fields=('user', 'role', 'workspace'), name='unique_user_role_workspace'),
        ),
        migrations.AddConstraint(
            model_name='tablepermission',
            constraint=models.UniqueConstraint(fields=('table', 'user', 'role'), name='unique_table_permission'),
        ),
        migrations.AddConstraint(
            model_name='tablepermission',
            constraint=models.CheckConstraint(
                check=models.Q(user__isnull=False) | models.Q(role__isnull=False),
                name='table_permission_user_or_role'
            ),
        ),
        migrations.AddConstraint(
            model_name='tablepermission',
            constraint=models.CheckConstraint(
                check=~(models.Q(user__isnull=False) & models.Q(role__isnull=False)),
                name='table_permission_not_both_user_and_role'
            ),
        ),
        migrations.AddConstraint(
            model_name='fieldpermission',
            constraint=models.UniqueConstraint(fields=('field', 'user', 'role'), name='unique_field_permission'),
        ),
        migrations.AddConstraint(
            model_name='fieldpermission',
            constraint=models.CheckConstraint(
                check=models.Q(user__isnull=False) | models.Q(role__isnull=False),
                name='field_permission_user_or_role'
            ),
        ),
        migrations.AddConstraint(
            model_name='fieldpermission',
            constraint=models.CheckConstraint(
                check=~(models.Q(user__isnull=False) & models.Q(role__isnull=False)),
                name='field_permission_not_both_user_and_role'
            ),
        ),
        migrations.AddConstraint(
            model_name='viewpermission',
            constraint=models.UniqueConstraint(fields=('view', 'user', 'role'), name='unique_view_permission'),
        ),
        migrations.AddConstraint(
            model_name='viewpermission',
            constraint=models.CheckConstraint(
                check=models.Q(user__isnull=False) | models.Q(role__isnull=False),
                name='view_permission_user_or_role'
            ),
        ),
        migrations.AddConstraint(
            model_name='viewpermission',
            constraint=models.CheckConstraint(
                check=~(models.Q(user__isnull=False) & models.Q(role__isnull=False)),
                name='view_permission_not_both_user_and_role'
            ),
        ),
        migrations.AddConstraint(
            model_name='conditionalpermission',
            constraint=models.UniqueConstraint(fields=('table', 'name'), name='unique_conditional_permission_name'),
        ),
        migrations.AddConstraint(
            model_name='conditionalpermission',
            constraint=models.CheckConstraint(
                check=models.Q(user__isnull=False) | models.Q(role__isnull=False),
                name='conditional_permission_user_or_role'
            ),
        ),
        migrations.AddConstraint(
            model_name='conditionalpermission',
            constraint=models.CheckConstraint(
                check=~(models.Q(user__isnull=False) & models.Q(role__isnull=False)),
                name='conditional_permission_not_both_user_and_role'
            ),
        ),
        migrations.AddConstraint(
            model_name='rowpermission',
            constraint=models.UniqueConstraint(fields=('table', 'row_id', 'user', 'role'), name='unique_row_permission'),
        ),
        migrations.AddConstraint(
            model_name='rowpermission',
            constraint=models.CheckConstraint(
                check=models.Q(user__isnull=False) | models.Q(role__isnull=False),
                name='row_permission_user_or_role'
            ),
        ),
        migrations.AddConstraint(
            model_name='rowpermission',
            constraint=models.CheckConstraint(
                check=~(models.Q(user__isnull=False) & models.Q(role__isnull=False)),
                name='row_permission_not_both_user_and_role'
            ),
        ),
        migrations.AddConstraint(
            model_name='apikey',
            constraint=models.UniqueConstraint(fields=('workspace', 'name'), name='unique_api_key_name'),
        ),
    ]