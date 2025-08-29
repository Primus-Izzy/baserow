"""
Granular permission system models for Baserow database.

This module implements field-level, row-level, and conditional permissions
that extend the existing workspace-level permission system.
"""

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _

from baserow.contrib.database.fields.models import Field
from baserow.contrib.database.table.models import Table
from baserow.contrib.database.views.models import View
from baserow.core.mixins import CreatedAndUpdatedOnMixin, HierarchicalModelMixin
from baserow.core.models import Workspace

User = get_user_model()


class PermissionLevel(models.TextChoices):
    """Permission levels for granular access control."""
    NONE = "NONE", _("No access")
    READ = "READ", _("Read only")
    UPDATE = "UPDATE", _("Read and update")
    CREATE = "CREATE", _("Read, update, and create")
    DELETE = "DELETE", _("Full access including delete")


class CustomRole(CreatedAndUpdatedOnMixin, models.Model):
    """
    Custom roles that can be created with specific permission sets.
    Extends the basic ADMIN/MEMBER workspace roles.
    """
    name = models.CharField(max_length=255, help_text="Name of the custom role")
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="custom_roles",
        help_text="Workspace this role belongs to"
    )
    description = models.TextField(
        blank=True,
        help_text="Optional description of the role"
    )
    
    # Base permissions
    can_create_tables = models.BooleanField(
        default=False,
        help_text="Can create new tables"
    )
    can_delete_tables = models.BooleanField(
        default=False,
        help_text="Can delete tables"
    )
    can_create_views = models.BooleanField(
        default=True,
        help_text="Can create new views"
    )
    can_manage_workspace = models.BooleanField(
        default=False,
        help_text="Can manage workspace settings and users"
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="User who created this role"
    )

    class Meta:
        unique_together = [["workspace", "name"]]
        ordering = ["name"]

    def __str__(self):
        return f"{self.workspace.name} - {self.name}"


class UserRole(models.Model):
    """
    Assigns custom roles to users within a workspace.
    Users can have multiple roles for fine-grained permissions.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(CustomRole, on_delete=models.CASCADE)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="assigned_roles",
        help_text="User who assigned this role"
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [["user", "role", "workspace"]]
        ordering = ["assigned_at"]

    def __str__(self):
        return f"{self.user.email} - {self.role.name}"


class TablePermission(CreatedAndUpdatedOnMixin, models.Model):
    """
    Table-level permissions that override workspace permissions.
    """
    table = models.ForeignKey(
        Table,
        on_delete=models.CASCADE,
        related_name="table_permissions"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Specific user (if null, applies to role)"
    )
    role = models.ForeignKey(
        CustomRole,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Custom role (if null, applies to user)"
    )
    
    permission_level = models.CharField(
        max_length=10,
        choices=PermissionLevel.choices,
        default=PermissionLevel.READ,
        help_text="Permission level for this table"
    )
    
    # Specific permissions
    can_create_rows = models.BooleanField(default=True)
    can_update_rows = models.BooleanField(default=True)
    can_delete_rows = models.BooleanField(default=False)
    can_create_fields = models.BooleanField(default=False)
    can_update_fields = models.BooleanField(default=False)
    can_delete_fields = models.BooleanField(default=False)
    can_create_views = models.BooleanField(default=True)
    can_update_views = models.BooleanField(default=True)
    can_delete_views = models.BooleanField(default=False)

    class Meta:
        unique_together = [["table", "user", "role"]]
        constraints = [
            models.CheckConstraint(
                check=models.Q(user__isnull=False) | models.Q(role__isnull=False),
                name="table_permission_user_or_role"
            ),
            models.CheckConstraint(
                check=~(models.Q(user__isnull=False) & models.Q(role__isnull=False)),
                name="table_permission_not_both_user_and_role"
            )
        ]

    def __str__(self):
        target = self.user.email if self.user else self.role.name
        return f"{self.table.name} - {target} - {self.permission_level}"


class FieldPermission(CreatedAndUpdatedOnMixin, models.Model):
    """
    Field-level permissions for granular access control.
    """
    field = models.ForeignKey(
        Field,
        on_delete=models.CASCADE,
        related_name="field_permissions"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Specific user (if null, applies to role)"
    )
    role = models.ForeignKey(
        CustomRole,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Custom role (if null, applies to user)"
    )
    
    permission_level = models.CharField(
        max_length=10,
        choices=PermissionLevel.choices,
        default=PermissionLevel.READ,
        help_text="Permission level for this field"
    )
    
    # Field-specific permissions
    can_read = models.BooleanField(default=True)
    can_update = models.BooleanField(default=True)
    is_hidden = models.BooleanField(
        default=False,
        help_text="Hide field from user interface"
    )

    class Meta:
        unique_together = [["field", "user", "role"]]
        constraints = [
            models.CheckConstraint(
                check=models.Q(user__isnull=False) | models.Q(role__isnull=False),
                name="field_permission_user_or_role"
            ),
            models.CheckConstraint(
                check=~(models.Q(user__isnull=False) & models.Q(role__isnull=False)),
                name="field_permission_not_both_user_and_role"
            )
        ]

    def __str__(self):
        target = self.user.email if self.user else self.role.name
        return f"{self.field.name} - {target} - {self.permission_level}"


class ViewPermission(CreatedAndUpdatedOnMixin, models.Model):
    """
    View-level permissions for controlling access to specific views.
    """
    view = models.ForeignKey(
        View,
        on_delete=models.CASCADE,
        related_name="view_permissions"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Specific user (if null, applies to role)"
    )
    role = models.ForeignKey(
        CustomRole,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Custom role (if null, applies to user)"
    )
    
    permission_level = models.CharField(
        max_length=10,
        choices=PermissionLevel.choices,
        default=PermissionLevel.READ,
        help_text="Permission level for this view"
    )
    
    # View-specific permissions
    can_read = models.BooleanField(default=True)
    can_update = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    is_hidden = models.BooleanField(
        default=False,
        help_text="Hide view from user interface"
    )

    class Meta:
        unique_together = [["view", "user", "role"]]
        constraints = [
            models.CheckConstraint(
                check=models.Q(user__isnull=False) | models.Q(role__isnull=False),
                name="view_permission_user_or_role"
            ),
            models.CheckConstraint(
                check=~(models.Q(user__isnull=False) & models.Q(role__isnull=False)),
                name="view_permission_not_both_user_and_role"
            )
        ]

    def __str__(self):
        target = self.user.email if self.user else self.role.name
        return f"{self.view.name} - {target} - {self.permission_level}"


class ConditionalPermission(CreatedAndUpdatedOnMixin, models.Model):
    """
    Conditional permissions based on field values and user attributes.
    Allows dynamic permission evaluation based on data content.
    """
    name = models.CharField(
        max_length=255,
        help_text="Descriptive name for this conditional permission"
    )
    table = models.ForeignKey(
        Table,
        on_delete=models.CASCADE,
        related_name="conditional_permissions"
    )
    
    # Target of the permission (user or role)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Specific user (if null, applies to role)"
    )
    role = models.ForeignKey(
        CustomRole,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Custom role (if null, applies to user)"
    )
    
    # Condition configuration
    condition_field = models.ForeignKey(
        Field,
        on_delete=models.CASCADE,
        help_text="Field to evaluate for condition"
    )
    condition_operator = models.CharField(
        max_length=20,
        choices=[
            ("equals", "Equals"),
            ("not_equals", "Not equals"),
            ("contains", "Contains"),
            ("not_contains", "Does not contain"),
            ("greater_than", "Greater than"),
            ("less_than", "Less than"),
            ("is_empty", "Is empty"),
            ("is_not_empty", "Is not empty"),
        ],
        help_text="Operator for condition evaluation"
    )
    condition_value = models.TextField(
        blank=True,
        help_text="Value to compare against (JSON for complex values)"
    )
    
    # User attribute conditions (optional)
    user_attribute_field = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ("email", "Email"),
            ("username", "Username"),
            ("first_name", "First name"),
            ("last_name", "Last name"),
            ("is_staff", "Is staff"),
            ("date_joined", "Date joined"),
        ],
        help_text="User attribute to check (optional)"
    )
    user_attribute_operator = models.CharField(
        max_length=20,
        blank=True,
        choices=[
            ("equals", "Equals"),
            ("contains", "Contains"),
            ("starts_with", "Starts with"),
            ("ends_with", "Ends with"),
        ],
        help_text="Operator for user attribute condition"
    )
    user_attribute_value = models.TextField(
        blank=True,
        help_text="Value to compare user attribute against"
    )
    
    # Permission to grant when condition is met
    granted_permission_level = models.CharField(
        max_length=10,
        choices=PermissionLevel.choices,
        default=PermissionLevel.READ,
        help_text="Permission level granted when condition is met"
    )
    
    # Specific permissions when condition is met
    can_read = models.BooleanField(default=True)
    can_update = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this conditional permission is active"
    )

    class Meta:
        unique_together = [["table", "name"]]
        constraints = [
            models.CheckConstraint(
                check=models.Q(user__isnull=False) | models.Q(role__isnull=False),
                name="conditional_permission_user_or_role"
            ),
            models.CheckConstraint(
                check=~(models.Q(user__isnull=False) & models.Q(role__isnull=False)),
                name="conditional_permission_not_both_user_and_role"
            )
        ]

    def __str__(self):
        target = self.user.email if self.user else self.role.name
        return f"{self.name} - {target}"


class RowPermission(CreatedAndUpdatedOnMixin, models.Model):
    """
    Row-level permissions for specific records.
    Allows fine-grained control over individual rows.
    """
    table = models.ForeignKey(
        Table,
        on_delete=models.CASCADE,
        related_name="row_permissions"
    )
    row_id = models.PositiveIntegerField(
        help_text="ID of the specific row"
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Specific user (if null, applies to role)"
    )
    role = models.ForeignKey(
        CustomRole,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Custom role (if null, applies to user)"
    )
    
    permission_level = models.CharField(
        max_length=10,
        choices=PermissionLevel.choices,
        default=PermissionLevel.READ,
        help_text="Permission level for this row"
    )
    
    # Row-specific permissions
    can_read = models.BooleanField(default=True)
    can_update = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    is_hidden = models.BooleanField(
        default=False,
        help_text="Hide row from user interface"
    )

    class Meta:
        unique_together = [["table", "row_id", "user", "role"]]
        constraints = [
            models.CheckConstraint(
                check=models.Q(user__isnull=False) | models.Q(role__isnull=False),
                name="row_permission_user_or_role"
            ),
            models.CheckConstraint(
                check=~(models.Q(user__isnull=False) & models.Q(role__isnull=False)),
                name="row_permission_not_both_user_and_role"
            )
        ]

    def __str__(self):
        target = self.user.email if self.user else self.role.name
        return f"{self.table.name} Row {self.row_id} - {target} - {self.permission_level}"


class APIKey(CreatedAndUpdatedOnMixin, models.Model):
    """
    API keys with granular scope control for external integrations.
    """
    name = models.CharField(
        max_length=255,
        help_text="Descriptive name for this API key"
    )
    key = models.CharField(
        max_length=255,
        unique=True,
        help_text="The actual API key"
    )
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="api_keys"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="User who created this API key"
    )
    
    # Scope configuration
    scope_tables = models.ManyToManyField(
        Table,
        blank=True,
        help_text="Tables this API key has access to (empty = all tables)"
    )
    scope_views = models.ManyToManyField(
        View,
        blank=True,
        help_text="Views this API key has access to (empty = all views)"
    )
    
    # Permission levels
    can_read = models.BooleanField(default=True)
    can_create = models.BooleanField(default=False)
    can_update = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    
    # Additional restrictions
    rate_limit_per_minute = models.PositiveIntegerField(
        default=60,
        help_text="Maximum requests per minute"
    )
    allowed_ip_addresses = models.TextField(
        blank=True,
        help_text="Comma-separated list of allowed IP addresses (empty = all IPs)"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this API key is active"
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Optional expiration date for this API key"
    )
    
    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time this API key was used"
    )

    class Meta:
        unique_together = [["workspace", "name"]]
        ordering = ["-created_on"]

    def __str__(self):
        return f"{self.workspace.name} - {self.name}"

    def is_expired(self):
        """Check if the API key has expired."""
        if self.expires_at is None:
            return False
        from django.utils import timezone
        return timezone.now() > self.expires_at

    def get_allowed_ip_list(self):
        """Get list of allowed IP addresses."""
        if not self.allowed_ip_addresses:
            return []
        return [ip.strip() for ip in self.allowed_ip_addresses.split(",")]