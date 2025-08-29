"""
Tests for the granular permission system.
"""

import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase

from baserow.contrib.database.fields.models import TextField
from baserow.contrib.database.permissions.exceptions import (
    CustomRoleAlreadyExists,
    InsufficientTablePermission,
)
from baserow.contrib.database.permissions.handler import GranularPermissionHandler
from baserow.contrib.database.permissions.models import (
    CustomRole,
    FieldPermission,
    PermissionLevel,
    TablePermission,
)
from baserow.contrib.database.table.models import Table
from baserow.core.models import Database, Workspace

User = get_user_model()


class TestGranularPermissionHandler(TestCase):
    """Test cases for GranularPermissionHandler."""
    
    def setUp(self):
        """Set up test data."""
        self.handler = GranularPermissionHandler()
        
        # Create test users
        self.admin_user = User.objects.create_user(
            email="admin@test.com",
            password="password"
        )
        self.regular_user = User.objects.create_user(
            email="user@test.com", 
            password="password"
        )
        
        # Create test workspace
        self.workspace = Workspace.objects.create(name="Test Workspace")
        
        # Create test database and table
        self.database = Database.objects.create(
            workspace=self.workspace,
            name="Test Database"
        )
        self.table = Table.objects.create(
            database=self.database,
            name="Test Table"
        )
        
        # Create test field
        self.field = TextField.objects.create(
            table=self.table,
            name="Test Field",
            order=1
        )
    
    def test_create_custom_role(self):
        """Test creating a custom role."""
        role = self.handler.create_custom_role(
            workspace=self.workspace,
            name="Test Role",
            description="A test role",
            created_by=self.admin_user,
            can_create_tables=True
        )
        
        self.assertEqual(role.name, "Test Role")
        self.assertEqual(role.description, "A test role")
        self.assertTrue(role.can_create_tables)
        self.assertEqual(role.created_by, self.admin_user)
        self.assertEqual(role.workspace, self.workspace)
    
    def test_create_duplicate_role_raises_exception(self):
        """Test that creating a duplicate role raises an exception."""
        self.handler.create_custom_role(
            workspace=self.workspace,
            name="Test Role",
            created_by=self.admin_user
        )
        
        with self.assertRaises(CustomRoleAlreadyExists):
            self.handler.create_custom_role(
                workspace=self.workspace,
                name="Test Role",
                created_by=self.admin_user
            )
    
    def test_assign_role_to_user(self):
        """Test assigning a role to a user."""
        role = self.handler.create_custom_role(
            workspace=self.workspace,
            name="Test Role",
            created_by=self.admin_user
        )
        
        user_role = self.handler.assign_role_to_user(
            user=self.regular_user,
            role=role,
            workspace=self.workspace,
            assigned_by=self.admin_user
        )
        
        self.assertEqual(user_role.user, self.regular_user)
        self.assertEqual(user_role.role, role)
        self.assertEqual(user_role.workspace, self.workspace)
        self.assertEqual(user_role.assigned_by, self.admin_user)
    
    def test_set_table_permission(self):
        """Test setting table permissions."""
        permission = self.handler.set_table_permission(
            table=self.table,
            user=self.regular_user,
            permission_level=PermissionLevel.UPDATE,
            can_create_rows=True,
            can_delete_rows=False
        )
        
        self.assertEqual(permission.table, self.table)
        self.assertEqual(permission.user, self.regular_user)
        self.assertEqual(permission.permission_level, PermissionLevel.UPDATE)
        self.assertTrue(permission.can_create_rows)
        self.assertFalse(permission.can_delete_rows)
    
    def test_set_field_permission(self):
        """Test setting field permissions."""
        permission = self.handler.set_field_permission(
            field=self.field,
            user=self.regular_user,
            permission_level=PermissionLevel.READ,
            is_hidden=True
        )
        
        self.assertEqual(permission.field, self.field)
        self.assertEqual(permission.user, self.regular_user)
        self.assertEqual(permission.permission_level, PermissionLevel.READ)
        self.assertTrue(permission.is_hidden)
    
    def test_check_table_permission_with_user_permission(self):
        """Test checking table permissions with direct user permission."""
        # Set user permission
        self.handler.set_table_permission(
            table=self.table,
            user=self.regular_user,
            permission_level=PermissionLevel.UPDATE,
            can_create_rows=True
        )
        
        # Check permissions
        self.assertTrue(
            self.handler.check_table_permission(
                self.regular_user, self.table, "read"
            )
        )
        self.assertTrue(
            self.handler.check_table_permission(
                self.regular_user, self.table, "update"
            )
        )
        self.assertTrue(
            self.handler.check_table_permission(
                self.regular_user, self.table, "create"
            )
        )
        self.assertFalse(
            self.handler.check_table_permission(
                self.regular_user, self.table, "delete"
            )
        )
    
    def test_check_table_permission_with_role_permission(self):
        """Test checking table permissions with role-based permission."""
        # Create role and assign to user
        role = self.handler.create_custom_role(
            workspace=self.workspace,
            name="Test Role",
            created_by=self.admin_user
        )
        self.handler.assign_role_to_user(
            user=self.regular_user,
            role=role,
            workspace=self.workspace,
            assigned_by=self.admin_user
        )
        
        # Set role permission
        self.handler.set_table_permission(
            table=self.table,
            role=role,
            permission_level=PermissionLevel.CREATE,
            can_delete_rows=False
        )
        
        # Check permissions
        self.assertTrue(
            self.handler.check_table_permission(
                self.regular_user, self.table, "read"
            )
        )
        self.assertTrue(
            self.handler.check_table_permission(
                self.regular_user, self.table, "create"
            )
        )
        self.assertFalse(
            self.handler.check_table_permission(
                self.regular_user, self.table, "delete"
            )
        )
    
    def test_check_field_permission_hidden_field(self):
        """Test that hidden fields are not accessible."""
        # Set field as hidden
        self.handler.set_field_permission(
            field=self.field,
            user=self.regular_user,
            is_hidden=True
        )
        
        # Check permissions
        self.assertFalse(
            self.handler.check_field_permission(
                self.regular_user, self.field, "read"
            )
        )
    
    def test_create_conditional_permission(self):
        """Test creating conditional permissions."""
        conditional_permission = self.handler.create_conditional_permission(
            name="Test Conditional",
            table=self.table,
            condition_field=self.field,
            condition_operator="equals",
            condition_value="test_value",
            user=self.regular_user,
            granted_permission_level=PermissionLevel.UPDATE
        )
        
        self.assertEqual(conditional_permission.name, "Test Conditional")
        self.assertEqual(conditional_permission.table, self.table)
        self.assertEqual(conditional_permission.condition_field, self.field)
        self.assertEqual(conditional_permission.condition_operator, "equals")
        self.assertEqual(conditional_permission.condition_value, "test_value")
        self.assertEqual(conditional_permission.user, self.regular_user)
    
    def test_evaluate_conditional_permission(self):
        """Test evaluating conditional permissions."""
        conditional_permission = self.handler.create_conditional_permission(
            name="Test Conditional",
            table=self.table,
            condition_field=self.field,
            condition_operator="equals",
            condition_value="test_value",
            user=self.regular_user,
            granted_permission_level=PermissionLevel.UPDATE
        )
        
        # Test with matching condition
        row_data = {f"field_{self.field.id}": "test_value"}
        self.assertTrue(
            self.handler.evaluate_conditional_permission(
                conditional_permission, self.regular_user, row_data
            )
        )
        
        # Test with non-matching condition
        row_data = {f"field_{self.field.id}": "other_value"}
        self.assertFalse(
            self.handler.evaluate_conditional_permission(
                conditional_permission, self.regular_user, row_data
            )
        )
    
    def test_create_api_key(self):
        """Test creating API keys."""
        api_key = self.handler.create_api_key(
            workspace=self.workspace,
            name="Test API Key",
            created_by=self.admin_user,
            can_read=True,
            can_create=False,
            rate_limit_per_minute=100
        )
        
        self.assertEqual(api_key.name, "Test API Key")
        self.assertEqual(api_key.workspace, self.workspace)
        self.assertEqual(api_key.created_by, self.admin_user)
        self.assertTrue(api_key.can_read)
        self.assertFalse(api_key.can_create)
        self.assertEqual(api_key.rate_limit_per_minute, 100)
        self.assertTrue(api_key.key.startswith("brow_"))
    
    def test_validate_api_key(self):
        """Test validating API keys."""
        api_key = self.handler.create_api_key(
            workspace=self.workspace,
            name="Test API Key",
            created_by=self.admin_user
        )
        
        # Test valid key
        validated_key = self.handler.validate_api_key(api_key.key)
        self.assertEqual(validated_key, api_key)
        
        # Test invalid key
        with self.assertRaises(Exception):  # APIKeyNotFound
            self.handler.validate_api_key("invalid_key")
    
    def test_get_user_permissions_summary(self):
        """Test getting user permissions summary."""
        # Create role and assign to user
        role = self.handler.create_custom_role(
            workspace=self.workspace,
            name="Test Role",
            created_by=self.admin_user
        )
        self.handler.assign_role_to_user(
            user=self.regular_user,
            role=role,
            workspace=self.workspace,
            assigned_by=self.admin_user
        )
        
        # Set some permissions
        self.handler.set_table_permission(
            table=self.table,
            user=self.regular_user,
            permission_level=PermissionLevel.UPDATE
        )
        
        # Get summary
        summary = self.handler.get_user_permissions_summary(
            self.regular_user, self.workspace
        )
        
        self.assertEqual(summary["user_id"], self.regular_user.id)
        self.assertEqual(summary["workspace_id"], self.workspace.id)
        self.assertEqual(len(summary["roles"]), 1)
        self.assertEqual(summary["roles"][0]["name"], "Test Role")
        self.assertEqual(len(summary["table_permissions"]), 1)


@pytest.mark.django_db
class TestGranularPermissionIntegration:
    """Integration tests for granular permissions."""
    
    def test_permission_system_integration(self):
        """Test that the permission system integrates properly."""
        # This would test integration with Baserow's existing permission system
        # For now, just verify that the models can be created
        
        user = User.objects.create_user(email="test@test.com", password="password")
        workspace = Workspace.objects.create(name="Test Workspace")
        
        role = CustomRole.objects.create(
            workspace=workspace,
            name="Test Role",
            created_by=user
        )
        
        assert role.name == "Test Role"
        assert role.workspace == workspace
        assert role.created_by == user