import pytest
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.utils import timezone
from unittest.mock import patch, MagicMock

from baserow.contrib.security.models import (
    SecurityAuditLog, EncryptedField, GDPRRequest, ConsentRecord, 
    RateLimitRule, RateLimitViolation
)
from baserow.contrib.security.handler import SecurityHandler
from baserow.contrib.security.middleware import SecurityMiddleware

User = get_user_model()


class SecurityHandlerTestCase(TestCase):
    """Test cases for SecurityHandler."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_log_security_event(self):
        """Test logging security events."""
        audit_log = SecurityHandler.log_security_event(
            event_type='login',
            user=self.user,
            ip_address='192.168.1.1',
            user_agent='Test Browser',
            details={'test': 'data'},
            severity='low'
        )
        
        self.assertIsInstance(audit_log, SecurityAuditLog)
        self.assertEqual(audit_log.event_type, 'login')
        self.assertEqual(audit_log.user, self.user)
        self.assertEqual(audit_log.ip_address, '192.168.1.1')
        self.assertEqual(audit_log.severity, 'low')
        self.assertEqual(audit_log.details, {'test': 'data'})

    def test_encrypt_decrypt_field_value(self):
        """Test field value encryption and decryption."""
        test_value = {'sensitive': 'data', 'number': 123}
        
        # Encrypt the value
        encrypted_field = SecurityHandler.encrypt_field_value(
            table_id=1,
            field_id=2,
            row_id=3,
            value=test_value
        )
        
        self.assertIsInstance(encrypted_field, EncryptedField)
        self.assertEqual(encrypted_field.table_id, 1)
        self.assertEqual(encrypted_field.field_id, 2)
        self.assertEqual(encrypted_field.row_id, 3)
        
        # Decrypt the value
        decrypted_value = SecurityHandler.decrypt_field_value(
            table_id=1,
            field_id=2,
            row_id=3
        )
        
        self.assertEqual(decrypted_value, test_value)

    def test_create_gdpr_request(self):
        """Test creating GDPR requests."""
        gdpr_request = SecurityHandler.create_gdpr_request(
            user=self.user,
            request_type='export',
            details={'format': 'json'}
        )
        
        self.assertIsInstance(gdpr_request, GDPRRequest)
        self.assertEqual(gdpr_request.user, self.user)
        self.assertEqual(gdpr_request.request_type, 'export')
        self.assertEqual(gdpr_request.status, 'pending')
        self.assertEqual(gdpr_request.details, {'format': 'json'})

    def test_grant_withdraw_consent(self):
        """Test granting and withdrawing consent."""
        # Grant consent
        consent = SecurityHandler.grant_consent(
            user=self.user,
            consent_type='data_processing',
            ip_address='192.168.1.1',
            user_agent='Test Browser'
        )
        
        self.assertIsInstance(consent, ConsentRecord)
        self.assertEqual(consent.user, self.user)
        self.assertEqual(consent.consent_type, 'data_processing')
        self.assertTrue(consent.granted)
        self.assertIsNotNone(consent.granted_at)
        
        # Withdraw consent
        withdrawn_consent = SecurityHandler.withdraw_consent(
            user=self.user,
            consent_type='data_processing'
        )
        
        self.assertEqual(withdrawn_consent, consent)
        self.assertFalse(withdrawn_consent.granted)
        self.assertIsNotNone(withdrawn_consent.withdrawn_at)

    def test_rate_limiting(self):
        """Test rate limiting functionality."""
        # Create a rate limit rule
        rule = RateLimitRule.objects.create(
            name='Test Rule',
            endpoint_pattern=r'/api/test/.*',
            requests_per_minute=2,
            requests_per_hour=10,
            requests_per_day=100
        )
        
        # First request should be allowed
        allowed = SecurityHandler.check_rate_limit(
            endpoint='/api/test/endpoint',
            method='GET',
            user=self.user,
            ip_address='192.168.1.1'
        )
        self.assertTrue(allowed)
        
        # Create violations to simulate rate limit exceeded
        RateLimitViolation.objects.create(
            rule=rule,
            user=self.user,
            ip_address='192.168.1.1',
            endpoint='/api/test/endpoint',
            method='GET',
            requests_count=1
        )
        RateLimitViolation.objects.create(
            rule=rule,
            user=self.user,
            ip_address='192.168.1.1',
            endpoint='/api/test/endpoint',
            method='GET',
            requests_count=1
        )
        
        # This request should be rate limited
        allowed = SecurityHandler.check_rate_limit(
            endpoint='/api/test/endpoint',
            method='GET',
            user=self.user,
            ip_address='192.168.1.1'
        )
        self.assertFalse(allowed)

    def test_security_metrics(self):
        """Test security metrics collection."""
        # Create some test data
        SecurityAuditLog.objects.create(
            event_type='failed_login',
            severity='medium',
            ip_address='192.168.1.1'
        )
        
        GDPRRequest.objects.create(
            user=self.user,
            request_type='export',
            status='pending'
        )
        
        metrics = SecurityHandler.get_security_metrics()
        
        self.assertIn('audit_events_24h', metrics)
        self.assertIn('failed_logins_24h', metrics)
        self.assertIn('gdpr_requests_pending', metrics)
        self.assertEqual(metrics['failed_logins_24h'], 1)
        self.assertEqual(metrics['gdpr_requests_pending'], 1)


class SecurityMiddlewareTestCase(TestCase):
    """Test cases for SecurityMiddleware."""

    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = SecurityMiddleware(lambda r: None)
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_rate_limit_check(self):
        """Test rate limit checking in middleware."""
        # Create a restrictive rate limit rule
        RateLimitRule.objects.create(
            name='Test Rule',
            endpoint_pattern=r'/api/test/.*',
            requests_per_minute=0,  # No requests allowed
            requests_per_hour=0,
            requests_per_day=0
        )
        
        request = self.factory.get('/api/test/endpoint')
        request.user = self.user
        
        response = self.middleware.process_request(request)
        
        # Should return 429 rate limit response
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 429)

    def test_skip_paths(self):
        """Test that certain paths are skipped."""
        request = self.factory.get('/health/')
        request.user = self.user
        
        response = self.middleware.process_request(request)
        
        # Should not process security checks for health endpoint
        self.assertIsNone(response)

    @patch('baserow.contrib.security.handler.SecurityHandler.log_security_event')
    def test_api_access_logging(self, mock_log):
        """Test API access logging."""
        request = self.factory.get('/api/database/1/')
        request.user = self.user
        request.security_context = {
            'ip_address': '192.168.1.1',
            'user_agent': 'Test Browser',
            'user': self.user,
            'timestamp': timezone.now(),
            'endpoint': '/api/database/1/',
            'method': 'GET',
        }
        
        response = MagicMock()
        response.status_code = 200
        
        self.middleware.process_response(request, response)
        
        # Should log API access
        mock_log.assert_called_once()
        call_args = mock_log.call_args
        self.assertEqual(call_args[1]['event_type'], 'api_access')
        self.assertEqual(call_args[1]['user'], self.user)


class GDPRComplianceTestCase(TestCase):
    """Test cases for GDPR compliance features."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    @patch('baserow.contrib.security.handler.SecurityHandler._collect_user_data')
    @patch('builtins.open', create=True)
    @patch('os.makedirs')
    def test_data_export_request(self, mock_makedirs, mock_open, mock_collect):
        """Test data export request processing."""
        mock_collect.return_value = {'user_data': 'test'}
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        gdpr_request = GDPRRequest.objects.create(
            user=self.user,
            request_type='export'
        )
        
        export_path = SecurityHandler.process_data_export_request(gdpr_request)
        
        # Refresh from database
        gdpr_request.refresh_from_db()
        
        self.assertEqual(gdpr_request.status, 'completed')
        self.assertIsNotNone(gdpr_request.completed_at)
        self.assertIsNotNone(export_path)
        mock_collect.assert_called_once_with(self.user)

    def test_data_collection(self):
        """Test user data collection for export."""
        data = SecurityHandler._collect_user_data(self.user)
        
        self.assertIn('user_profile', data)
        self.assertIn('workspaces', data)
        self.assertIn('databases', data)
        self.assertIn('tables', data)
        self.assertIn('audit_logs', data)
        self.assertIn('consent_records', data)
        
        self.assertEqual(data['user_profile']['email'], self.user.email)
        self.assertEqual(data['user_profile']['username'], self.user.username)