"""
Comprehensive Security Testing Suite for Baserow Monday.com Expansion

This module provides comprehensive security testing for the permission system,
data protection, and security compliance features.
"""

import pytest
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch, MagicMock
import json
import time
from datetime import datetime, timedelta

from baserow.contrib.database.models import Database, Table
from baserow.contrib.database.permissions.models import (
    GranularPermission, 
    ConditionalPermission,
    CustomRole
)
from baserow.contrib.security.models import (
    SecurityAuditLog,
    DataEncryption,
    APIKeyPermission
)
from baserow.contrib.security.handler import SecurityHandler
from baserow.core.models import Workspace, User


User = get_user_model()


class SecurityPermissionSystemTest(TestCase):
    """Test comprehensive permission system security."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='adminpass123'
        )
        self.workspace = Workspace.objects.create(name='Test Workspace')
        self.database = Database.objects.create(
            workspace=self.workspace,
            name='Test Database'
        )
        self.table = Table.objects.create(
            database=self.database,
            name='Test Table'
        )
        
    def test_hierarchical_permission_enforcement(self):
        """Test that hierarchical permissions are properly enforced."""
        # Create workspace-level permission
        workspace_permission = GranularPermission.objects.create(
            user=self.user,
            workspace=self.workspace,
            permission_type='read',
            level='workspace'
        )
        
        # Test workspace access
        handler = SecurityHandler()
        self.assertTrue(
            handler.check_permission(self.user, 'read', workspace=self.workspace)
        )
        
        # Test that workspace permission doesn't grant table write access
        self.assertFalse(
            handler.check_permission(self.user, 'write', table=self.table)
        )
        
    def test_row_level_security(self):
        """Test row-level security implementation."""
        # Create conditional permission based on field value
        conditional_perm = ConditionalPermission.objects.create(
            user=self.user,
            table=self.table,
            permission_type='read',
            condition={'field_name': 'owner', 'operator': 'equals', 'value': self.user.id}
        )
        
        handler = SecurityHandler()
        
        # Test row access with matching condition
        row_data = {'owner': self.user.id, 'title': 'Test Row'}
        self.assertTrue(
            handler.check_row_permission(self.user, 'read', self.table, row_data)
        )
        
        # Test row access with non-matching condition
        row_data = {'owner': 999, 'title': 'Other User Row'}
        self.assertFalse(
            handler.check_row_permission(self.user, 'read', self.table, row_data)
        )
        
    def test_field_level_permissions(self):
        """Test field-level permission enforcement."""
        # Create field-level permission
        field_permission = GranularPermission.objects.create(
            user=self.user,
            table=self.table,
            permission_type='read',
            level='field',
            field_name='sensitive_data'
        )
        
        handler = SecurityHandler()
        
        # Test field access
        self.assertTrue(
            handler.check_field_permission(self.user, 'read', self.table, 'sensitive_data')
        )
        
        # Test access to non-permitted field
        self.assertFalse(
            handler.check_field_permission(self.user, 'read', self.table, 'other_field')
        )
        
    def test_custom_role_security(self):
        """Test custom role creation and assignment security."""
        # Create custom role
        custom_role = CustomRole.objects.create(
            name='Data Analyst',
            workspace=self.workspace,
            permissions={
                'database': ['read'],
                'table': ['read', 'create'],
                'view': ['read', 'update']
            }
        )
        
        # Assign role to user
        custom_role.users.add(self.user)
        
        handler = SecurityHandler()
        
        # Test role-based permissions
        self.assertTrue(
            handler.check_role_permission(self.user, 'read', 'database', self.workspace)
        )
        self.assertTrue(
            handler.check_role_permission(self.user, 'create', 'table', self.workspace)
        )
        self.assertFalse(
            handler.check_role_permission(self.user, 'delete', 'table', self.workspace)
        )


class DataProtectionSecurityTest(TestCase):
    """Test data protection and encryption security."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
    def test_data_encryption_at_rest(self):
        """Test data encryption at rest functionality."""
        sensitive_data = "This is sensitive information"
        
        # Test encryption
        encrypted_data = DataEncryption.encrypt_field_data(sensitive_data)
        self.assertNotEqual(encrypted_data, sensitive_data)
        self.assertIsInstance(encrypted_data, str)
        
        # Test decryption
        decrypted_data = DataEncryption.decrypt_field_data(encrypted_data)
        self.assertEqual(decrypted_data, sensitive_data)
        
    def test_sensitive_field_masking(self):
        """Test sensitive field masking for unauthorized users."""
        handler = SecurityHandler()
        
        # Test field masking
        sensitive_value = "123-45-6789"
        masked_value = handler.mask_sensitive_field(sensitive_value, 'ssn')
        self.assertEqual(masked_value, "***-**-****")
        
        # Test email masking
        email_value = "user@example.com"
        masked_email = handler.mask_sensitive_field(email_value, 'email')
        self.assertEqual(masked_email, "u***@e******.com")
        
    def test_audit_log_security(self):
        """Test security audit logging."""
        handler = SecurityHandler()
        
        # Test audit log creation
        audit_log = handler.create_audit_log(
            user=self.user,
            action='data_access',
            resource_type='table',
            resource_id=1,
            details={'field': 'sensitive_data', 'access_type': 'read'}
        )
        
        self.assertIsInstance(audit_log, SecurityAuditLog)
        self.assertEqual(audit_log.user, self.user)
        self.assertEqual(audit_log.action, 'data_access')
        
    def test_gdpr_compliance_tools(self):
        """Test GDPR compliance functionality."""
        handler = SecurityHandler()
        
        # Test data export for user
        export_data = handler.export_user_data(self.user)
        self.assertIsInstance(export_data, dict)
        self.assertIn('personal_data', export_data)
        self.assertIn('activity_logs', export_data)
        
        # Test data anonymization
        anonymized_data = handler.anonymize_user_data(self.user.id)
        self.assertTrue(anonymized_data['success'])
        self.assertIn('anonymized_fields', anonymized_data)


class APISecurityTest(APITestCase):
    """Test API security and rate limiting."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.workspace = Workspace.objects.create(name='Test Workspace')
        
    def test_api_key_permissions(self):
        """Test API key permission system."""
        # Create API key with limited permissions
        api_key_permission = APIKeyPermission.objects.create(
            user=self.user,
            key_name='Limited Access Key',
            permissions={
                'tables': ['read'],
                'views': ['read'],
                'rows': ['read']
            },
            rate_limit=100,
            ip_restrictions=['192.168.1.0/24']
        )
        
        handler = SecurityHandler()
        
        # Test API key validation
        self.assertTrue(
            handler.validate_api_key_permission(
                api_key_permission, 'read', 'tables'
            )
        )
        
        # Test unauthorized operation
        self.assertFalse(
            handler.validate_api_key_permission(
                api_key_permission, 'write', 'tables'
            )
        )
        
    @patch('baserow.contrib.security.middleware.get_client_ip')
    def test_rate_limiting(self, mock_get_ip):
        """Test API rate limiting functionality."""
        mock_get_ip.return_value = '192.168.1.100'
        
        handler = SecurityHandler()
        
        # Test rate limit checking
        for i in range(5):
            allowed = handler.check_rate_limit(
                self.user, 'api_call', limit=3, window=60
            )
            if i < 3:
                self.assertTrue(allowed)
            else:
                self.assertFalse(allowed)
                
    def test_ip_restriction_enforcement(self):
        """Test IP address restriction enforcement."""
        handler = SecurityHandler()
        
        # Test allowed IP
        self.assertTrue(
            handler.check_ip_restriction('192.168.1.100', ['192.168.1.0/24'])
        )
        
        # Test blocked IP
        self.assertFalse(
            handler.check_ip_restriction('10.0.0.100', ['192.168.1.0/24'])
        )


class SecurityVulnerabilityTest(TestCase):
    """Test for common security vulnerabilities."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention in queries."""
        handler = SecurityHandler()
        
        # Test malicious input sanitization
        malicious_input = "'; DROP TABLE users; --"
        sanitized_input = handler.sanitize_sql_input(malicious_input)
        
        self.assertNotIn('DROP TABLE', sanitized_input)
        self.assertNotIn(';', sanitized_input)
        
    def test_xss_prevention(self):
        """Test XSS prevention in user input."""
        handler = SecurityHandler()
        
        # Test script tag removal
        malicious_script = "<script>alert('xss')</script>Hello"
        sanitized_output = handler.sanitize_html_input(malicious_script)
        
        self.assertNotIn('<script>', sanitized_output)
        self.assertIn('Hello', sanitized_output)
        
    def test_csrf_protection(self):
        """Test CSRF protection mechanisms."""
        # This would typically be tested through API calls
        # with proper CSRF token validation
        pass
        
    def test_privilege_escalation_prevention(self):
        """Test prevention of privilege escalation attacks."""
        handler = SecurityHandler()
        
        # Test that users cannot escalate their own permissions
        with self.assertRaises(PermissionDenied):
            handler.escalate_user_permissions(
                self.user, self.user, ['admin']
            )


class ComplianceSecurityTest(TestCase):
    """Test compliance and regulatory security features."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
    def test_data_retention_policies(self):
        """Test data retention policy enforcement."""
        handler = SecurityHandler()
        
        # Test data retention check
        old_date = datetime.now() - timedelta(days=400)
        should_retain = handler.check_data_retention(
            data_type='audit_logs',
            created_date=old_date,
            retention_days=365
        )
        
        self.assertFalse(should_retain)
        
    def test_consent_management(self):
        """Test user consent management for data processing."""
        handler = SecurityHandler()
        
        # Test consent recording
        consent_record = handler.record_user_consent(
            user=self.user,
            consent_type='data_processing',
            granted=True,
            purpose='analytics'
        )
        
        self.assertTrue(consent_record['success'])
        self.assertEqual(consent_record['consent_type'], 'data_processing')
        
    def test_right_to_be_forgotten(self):
        """Test implementation of right to be forgotten."""
        handler = SecurityHandler()
        
        # Test data deletion request
        deletion_result = handler.process_deletion_request(self.user.id)
        
        self.assertTrue(deletion_result['success'])
        self.assertIn('deleted_records', deletion_result)


@pytest.mark.security
class SecurityIntegrationTest(TestCase):
    """Integration tests for security features."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.workspace = Workspace.objects.create(name='Test Workspace')
        
    def test_end_to_end_permission_flow(self):
        """Test complete permission flow from creation to enforcement."""
        handler = SecurityHandler()
        
        # Create permission hierarchy
        workspace_perm = handler.create_permission(
            user=self.user,
            resource_type='workspace',
            resource_id=self.workspace.id,
            permission_type='read'
        )
        
        # Test permission inheritance
        inherited_perms = handler.get_inherited_permissions(
            self.user, self.workspace
        )
        
        self.assertIn('read', inherited_perms)
        
    def test_security_monitoring_integration(self):
        """Test security monitoring and alerting integration."""
        handler = SecurityHandler()
        
        # Simulate suspicious activity
        suspicious_activity = handler.detect_suspicious_activity(
            user=self.user,
            activity_type='multiple_failed_logins',
            count=5,
            timeframe=300  # 5 minutes
        )
        
        self.assertTrue(suspicious_activity['is_suspicious'])
        self.assertIn('recommended_actions', suspicious_activity)


if __name__ == '__main__':
    pytest.main([__file__])