"""
Comprehensive Security Testing Suite

Tests for permission system, data protection, authentication, authorization,
and security compliance features across the entire Baserow platform.
"""

import pytest
import json
import time
from unittest.mock import patch, MagicMock
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db import transaction
from rest_framework.test import APITestCase
from rest_framework import status

from baserow.contrib.database.models import Database, Table
from baserow.contrib.database.permissions.models import (
    GranularPermission, ConditionalPermission, CustomRole
)
from baserow.contrib.database.permissions.handler import PermissionHandler
from baserow.contrib.security.models import (
    SecurityAuditLog, DataEncryption, APIKeyPermission
)
from baserow.contrib.security.handler import SecurityHandler
from baserow.core.models import Workspace

User = get_user_model()


class SecurityPermissionSystemTest(TestCase):
    """Test comprehensive permission system security."""
    
    def setUp(self):
        """Set up test data."""
        self.user1 = User.objects.create_user(
            email='user1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            email='user2@test.com', 
            password='testpass123'
        )
        self.admin_user = User.objects.create_user(
            email='admin@test.com',
            password='testpass123',
            is_staff=True
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
        
        self.permission_handler = PermissionHandler()
        self.security_handler = SecurityHandler()
    
    def test_workspace_level_permissions(self):
        """Test workspace-level permission enforcement."""
        # Grant workspace access to user1
        permission = GranularPermission.objects.create(
            user=self.user1,
            workspace=self.workspace,
            permission_level='editor'
        )
        
        # Test user1 can access workspace
        self.assertTrue(
            self.permission_handler.check_workspace_permission(
                self.user1, self.workspace, 'read'
            )
        )
        
        # Test user2 cannot access workspace
        self.assertFalse(
            self.permission_handler.check_workspace_permission(
                self.user2, self.workspace, 'read'
            )
        )
        
        # Test permission inheritance to database
        self.assertTrue(
            self.permission_handler.check_database_permission(
                self.user1, self.database, 'read'
            )
        )
    
    def test_table_level_permissions(self):
        """Test table-level permission enforcement."""
        # Grant table-specific permission
        permission = GranularPermission.objects.create(
            user=self.user1,
            table=self.table,
            permission_level='viewer'
        )
        
        # Test read access granted
        self.assertTrue(
            self.permission_handler.check_table_permission(
                self.user1, self.table, 'read'
            )
        )
        
        # Test write access denied
        self.assertFalse(
            self.permission_handler.check_table_permission(
                self.user1, self.table, 'write'
            )
        )
    
    def test_field_level_permissions(self):
        """Test field-level permission enforcement."""
        from baserow.contrib.database.fields.models import TextField
        
        field = TextField.objects.create(
            table=self.table,
            name='Test Field'
        )
        
        # Grant field-specific permission
        permission = GranularPermission.objects.create(
            user=self.user1,
            field=field,
            permission_level='read_only'
        )
        
        # Test field access
        self.assertTrue(
            self.permission_handler.check_field_permission(
                self.user1, field, 'read'
            )
        )
        
        self.assertFalse(
            self.permission_handler.check_field_permission(
                self.user1, field, 'write'
            )
        )
    
    def test_row_level_permissions(self):
        """Test row-level permission enforcement."""
        from baserow.contrib.database.rows.handler import RowHandler
        
        row_handler = RowHandler()
        
        # Create test row
        row = row_handler.create_row_for_table(
            user=self.admin_user,
            table=self.table,
            values={}
        )
        
        # Create conditional permission based on row data
        conditional_permission = ConditionalPermission.objects.create(
            user=self.user1,
            table=self.table,
            condition={'field_name': 'owner', 'operator': 'equals', 'value': 'user1'},
            permission_level='editor'
        )
        
        # Test row access with condition
        self.assertTrue(
            self.permission_handler.check_row_permission(
                self.user1, self.table, row.id, 'read'
            )
        )
    
    def test_custom_role_permissions(self):
        """Test custom role creation and assignment."""
        # Create custom role
        custom_role = CustomRole.objects.create(
            name='Data Analyst',
            workspace=self.workspace,
            permissions={
                'database': ['read'],
                'table': ['read', 'filter'],
                'view': ['read', 'create'],
                'field': ['read']
            }
        )
        
        # Assign role to user
        permission = GranularPermission.objects.create(
            user=self.user1,
            workspace=self.workspace,
            custom_role=custom_role
        )
        
        # Test role-based permissions
        self.assertTrue(
            self.permission_handler.check_permission_with_role(
                self.user1, self.workspace, 'database', 'read'
            )
        )
        
        self.assertFalse(
            self.permission_handler.check_permission_with_role(
                self.user1, self.workspace, 'database', 'write'
            )
        )
    
    def test_permission_escalation_prevention(self):
        """Test prevention of privilege escalation attacks."""
        # User with limited permissions
        limited_permission = GranularPermission.objects.create(
            user=self.user1,
            workspace=self.workspace,
            permission_level='viewer'
        )
        
        # Attempt to escalate permissions
        with self.assertRaises(PermissionDenied):
            self.permission_handler.grant_permission(
                granting_user=self.user1,
                target_user=self.user2,
                workspace=self.workspace,
                permission_level='admin'
            )
    
    def test_api_key_permissions(self):
        """Test API key permission system."""
        # Create API key with limited scope
        api_key_permission = APIKeyPermission.objects.create(
            user=self.user1,
            key_name='Test API Key',
            scopes=['database:read', 'table:read'],
            workspace=self.workspace
        )
        
        # Test API key validation
        self.assertTrue(
            self.security_handler.validate_api_key_permission(
                api_key_permission, 'database', 'read'
            )
        )
        
        self.assertFalse(
            self.security_handler.validate_api_key_permission(
                api_key_permission, 'database', 'write'
            )
        )


class DataProtectionSecurityTest(TestCase):
    """Test data protection and encryption features."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@test.com',
            password='testpass123'
        )
        self.security_handler = SecurityHandler()
    
    def test_data_encryption_at_rest(self):
        """Test data encryption at rest."""
        sensitive_data = "This is sensitive information"
        
        # Encrypt data
        encrypted_data = self.security_handler.encrypt_data(sensitive_data)
        
        # Verify data is encrypted
        self.assertNotEqual(sensitive_data, encrypted_data.encrypted_value)
        self.assertIsNotNone(encrypted_data.encryption_key_id)
        
        # Decrypt data
        decrypted_data = self.security_handler.decrypt_data(encrypted_data)
        self.assertEqual(sensitive_data, decrypted_data)
    
    def test_data_encryption_in_transit(self):
        """Test data encryption in transit."""
        # This would typically be tested at the HTTP/TLS level
        # Here we test the application-level encryption
        
        payload = {"sensitive": "data", "user_id": self.user.id}
        
        # Encrypt payload for transmission
        encrypted_payload = self.security_handler.encrypt_transmission_data(payload)
        
        # Verify encryption
        self.assertNotEqual(json.dumps(payload), encrypted_payload)
        
        # Decrypt payload
        decrypted_payload = self.security_handler.decrypt_transmission_data(encrypted_payload)
        self.assertEqual(payload, decrypted_payload)
    
    def test_pii_data_handling(self):
        """Test PII data handling and anonymization."""
        pii_data = {
            'email': 'user@example.com',
            'phone': '+1234567890',
            'name': 'John Doe',
            'address': '123 Main St'
        }
        
        # Anonymize PII data
        anonymized_data = self.security_handler.anonymize_pii_data(pii_data)
        
        # Verify anonymization
        self.assertNotEqual(pii_data['email'], anonymized_data['email'])
        self.assertNotEqual(pii_data['phone'], anonymized_data['phone'])
        self.assertNotEqual(pii_data['name'], anonymized_data['name'])
        self.assertNotEqual(pii_data['address'], anonymized_data['address'])
        
        # Verify format preservation
        self.assertIn('@', anonymized_data['email'])
        self.assertTrue(anonymized_data['phone'].startswith('+'))
    
    def test_gdpr_compliance_data_export(self):
        """Test GDPR compliance data export."""
        # Create user data across multiple tables
        workspace = Workspace.objects.create(name='Test Workspace')
        database = Database.objects.create(workspace=workspace, name='Test DB')
        table = Table.objects.create(database=database, name='Test Table')
        
        # Export user data
        exported_data = self.security_handler.export_user_data(self.user)
        
        # Verify export completeness
        self.assertIn('user_profile', exported_data)
        self.assertIn('workspaces', exported_data)
        self.assertIn('permissions', exported_data)
        self.assertIn('activity_logs', exported_data)
    
    def test_gdpr_compliance_data_deletion(self):
        """Test GDPR compliance data deletion."""
        # Create user data
        workspace = Workspace.objects.create(name='Test Workspace')
        
        # Request data deletion
        deletion_result = self.security_handler.delete_user_data(
            self.user, 
            anonymize=True
        )
        
        # Verify deletion/anonymization
        self.assertTrue(deletion_result['success'])
        self.assertGreater(deletion_result['records_processed'], 0)
        
        # Verify user data is anonymized
        self.user.refresh_from_db()
        self.assertTrue(self.user.email.startswith('anonymized_'))


class SecurityAuditTest(TestCase):
    """Test security audit logging and monitoring."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@test.com',
            password='testpass123'
        )
        self.security_handler = SecurityHandler()
    
    def test_security_audit_logging(self):
        """Test comprehensive security audit logging."""
        # Perform security-sensitive action
        self.security_handler.log_security_event(
            user=self.user,
            event_type='permission_granted',
            details={
                'target_user': 'user2@test.com',
                'permission': 'database:read',
                'resource': 'test_database'
            },
            ip_address='192.168.1.1',
            user_agent='Test Agent'
        )
        
        # Verify audit log creation
        audit_log = SecurityAuditLog.objects.filter(user=self.user).first()
        self.assertIsNotNone(audit_log)
        self.assertEqual(audit_log.event_type, 'permission_granted')
        self.assertEqual(audit_log.ip_address, '192.168.1.1')
    
    def test_failed_authentication_logging(self):
        """Test failed authentication attempt logging."""
        # Simulate failed login
        self.security_handler.log_failed_authentication(
            email='test@test.com',
            ip_address='192.168.1.100',
            failure_reason='invalid_password'
        )
        
        # Verify logging
        audit_log = SecurityAuditLog.objects.filter(
            event_type='authentication_failed'
        ).first()
        self.assertIsNotNone(audit_log)
        self.assertEqual(audit_log.details['failure_reason'], 'invalid_password')
    
    def test_suspicious_activity_detection(self):
        """Test suspicious activity detection and alerting."""
        # Simulate multiple failed login attempts
        for i in range(5):
            self.security_handler.log_failed_authentication(
                email='test@test.com',
                ip_address='192.168.1.100',
                failure_reason='invalid_password'
            )
        
        # Check if suspicious activity is detected
        is_suspicious = self.security_handler.detect_suspicious_activity(
            email='test@test.com',
            time_window_minutes=5
        )
        
        self.assertTrue(is_suspicious)
    
    def test_rate_limiting_enforcement(self):
        """Test rate limiting for API endpoints."""
        # Simulate rapid API requests
        for i in range(10):
            result = self.security_handler.check_rate_limit(
                user=self.user,
                endpoint='/api/database/tables/',
                limit=5,
                window_seconds=60
            )
            
            if i < 5:
                self.assertTrue(result['allowed'])
            else:
                self.assertFalse(result['allowed'])


class VulnerabilitySecurityTest(TestCase):
    """Test protection against common security vulnerabilities."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@test.com',
            password='testpass123'
        )
        self.security_handler = SecurityHandler()
    
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention."""
        # Attempt SQL injection in search query
        malicious_query = "'; DROP TABLE users; --"
        
        # Test query sanitization
        sanitized_query = self.security_handler.sanitize_search_query(malicious_query)
        
        # Verify malicious SQL is neutralized
        self.assertNotIn('DROP TABLE', sanitized_query)
        self.assertNotIn(';', sanitized_query)
    
    def test_xss_prevention(self):
        """Test XSS prevention in user input."""
        # Malicious script input
        malicious_input = "<script>alert('XSS')</script>"
        
        # Test input sanitization
        sanitized_input = self.security_handler.sanitize_user_input(malicious_input)
        
        # Verify script tags are removed/escaped
        self.assertNotIn('<script>', sanitized_input)
        self.assertNotIn('alert(', sanitized_input)
    
    def test_csrf_protection(self):
        """Test CSRF protection mechanisms."""
        # Generate CSRF token
        csrf_token = self.security_handler.generate_csrf_token(self.user)
        
        # Validate CSRF token
        is_valid = self.security_handler.validate_csrf_token(
            self.user, csrf_token
        )
        self.assertTrue(is_valid)
        
        # Test invalid token
        is_valid = self.security_handler.validate_csrf_token(
            self.user, 'invalid_token'
        )
        self.assertFalse(is_valid)
    
    def test_directory_traversal_prevention(self):
        """Test directory traversal attack prevention."""
        # Malicious file path
        malicious_path = "../../../etc/passwd"
        
        # Test path sanitization
        safe_path = self.security_handler.sanitize_file_path(malicious_path)
        
        # Verify path traversal is prevented
        self.assertNotIn('..', safe_path)
        self.assertNotIn('/etc/', safe_path)
    
    def test_file_upload_security(self):
        """Test file upload security measures."""
        # Test various file types
        test_files = [
            ('test.jpg', b'fake_image_data', True),
            ('test.exe', b'fake_executable', False),
            ('test.php', b'<?php echo "test"; ?>', False),
            ('test.txt', b'safe text content', True)
        ]
        
        for filename, content, should_allow in test_files:
            is_safe = self.security_handler.validate_file_upload(filename, content)
            self.assertEqual(is_safe, should_allow, f"File {filename} validation failed")


class ComplianceSecurityTest(TestCase):
    """Test compliance with security standards and regulations."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@test.com',
            password='testpass123'
        )
        self.security_handler = SecurityHandler()
    
    def test_password_policy_enforcement(self):
        """Test password policy enforcement."""
        # Test weak passwords
        weak_passwords = [
            'password',
            '123456',
            'qwerty',
            'abc123'
        ]
        
        for password in weak_passwords:
            is_valid = self.security_handler.validate_password_strength(password)
            self.assertFalse(is_valid, f"Weak password '{password}' was accepted")
        
        # Test strong password
        strong_password = 'StrongP@ssw0rd123!'
        is_valid = self.security_handler.validate_password_strength(strong_password)
        self.assertTrue(is_valid)
    
    def test_session_security(self):
        """Test session security measures."""
        # Create secure session
        session_data = self.security_handler.create_secure_session(self.user)
        
        # Verify session properties
        self.assertIsNotNone(session_data['session_id'])
        self.assertIsNotNone(session_data['csrf_token'])
        self.assertIsNotNone(session_data['expires_at'])
        
        # Test session validation
        is_valid = self.security_handler.validate_session(
            session_data['session_id'], self.user
        )
        self.assertTrue(is_valid)
    
    def test_data_retention_policies(self):
        """Test data retention policy enforcement."""
        # Create old audit logs
        old_log = SecurityAuditLog.objects.create(
            user=self.user,
            event_type='test_event',
            timestamp=timezone.now() - timedelta(days=400)  # Older than retention period
        )
        
        # Run retention cleanup
        cleanup_result = self.security_handler.cleanup_expired_data()
        
        # Verify old data is removed
        self.assertGreater(cleanup_result['records_deleted'], 0)
        
        # Verify log is deleted
        with self.assertRaises(SecurityAuditLog.DoesNotExist):
            old_log.refresh_from_db()


class APISecurityTest(APITestCase):
    """Test API security measures."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@test.com',
            password='testpass123'
        )
        self.workspace = Workspace.objects.create(name='Test Workspace')
    
    def test_api_authentication_required(self):
        """Test API endpoints require authentication."""
        # Test unauthenticated request
        response = self.client.get('/api/workspaces/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test authenticated request
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/workspaces/')
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN])
    
    def test_api_authorization_enforcement(self):
        """Test API endpoints enforce proper authorization."""
        # Create workspace user doesn't have access to
        other_workspace = Workspace.objects.create(name='Other Workspace')
        
        self.client.force_authenticate(user=self.user)
        
        # Test unauthorized access
        response = self.client.get(f'/api/workspaces/{other_workspace.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_api_input_validation(self):
        """Test API input validation and sanitization."""
        self.client.force_authenticate(user=self.user)
        
        # Test malicious input
        malicious_data = {
            'name': '<script>alert("xss")</script>',
            'description': '"; DROP TABLE workspaces; --'
        }
        
        response = self.client.post('/api/workspaces/', malicious_data)
        
        # Should either reject or sanitize input
        if response.status_code == status.HTTP_201_CREATED:
            workspace = Workspace.objects.get(id=response.data['id'])
            self.assertNotIn('<script>', workspace.name)
            self.assertNotIn('DROP TABLE', workspace.description or '')
    
    def test_api_rate_limiting(self):
        """Test API rate limiting."""
        self.client.force_authenticate(user=self.user)
        
        # Make rapid requests
        responses = []
        for i in range(20):
            response = self.client.get('/api/workspaces/')
            responses.append(response.status_code)
        
        # Should eventually hit rate limit
        rate_limited_responses = [
            status for status in responses 
            if status == status.HTTP_429_TOO_MANY_REQUESTS
        ]
        
        # At least some requests should be rate limited
        self.assertGreater(len(rate_limited_responses), 0)


if __name__ == '__main__':
    pytest.main([__file__])