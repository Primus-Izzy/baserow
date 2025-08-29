from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
from cryptography.fernet import Fernet
from django.conf import settings
import json

User = get_user_model()


class SecurityAuditLog(models.Model):
    """
    Comprehensive audit logging for security events
    """
    EVENT_TYPES = [
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('failed_login', 'Failed Login Attempt'),
        ('password_change', 'Password Change'),
        ('permission_change', 'Permission Change'),
        ('data_access', 'Data Access'),
        ('data_export', 'Data Export'),
        ('data_deletion', 'Data Deletion'),
        ('api_access', 'API Access'),
        ('admin_action', 'Admin Action'),
        ('security_violation', 'Security Violation'),
    ]

    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='low')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    
    # Generic foreign key for related objects
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    details = models.JSONField(default=dict)
    success = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'baserow_security_audit_log'
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['event_type', 'timestamp']),
            models.Index(fields=['severity', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.event_type} - {self.user} - {self.timestamp}"


class EncryptedField(models.Model):
    """
    Model to store encrypted field data
    """
    table_id = models.PositiveIntegerField()
    field_id = models.PositiveIntegerField()
    row_id = models.PositiveIntegerField()
    encrypted_value = models.BinaryField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'baserow_encrypted_fields'
        unique_together = ['table_id', 'field_id', 'row_id']
        indexes = [
            models.Index(fields=['table_id', 'row_id']),
            models.Index(fields=['field_id']),
        ]

    @classmethod
    def get_encryption_key(cls):
        """Get or create encryption key"""
        key = getattr(settings, 'BASEROW_ENCRYPTION_KEY', None)
        if not key:
            key = Fernet.generate_key()
        return key

    def encrypt_value(self, value):
        """Encrypt a value"""
        if value is None:
            return None
        
        key = self.get_encryption_key()
        fernet = Fernet(key)
        
        # Convert value to string if it's not already
        if not isinstance(value, str):
            value = json.dumps(value)
        
        encrypted_value = fernet.encrypt(value.encode())
        self.encrypted_value = encrypted_value
        return encrypted_value

    def decrypt_value(self):
        """Decrypt the stored value"""
        if not self.encrypted_value:
            return None
        
        key = self.get_encryption_key()
        fernet = Fernet(key)
        
        try:
            decrypted_value = fernet.decrypt(self.encrypted_value).decode()
            # Try to parse as JSON, fallback to string
            try:
                return json.loads(decrypted_value)
            except json.JSONDecodeError:
                return decrypted_value
        except Exception:
            return None


class GDPRRequest(models.Model):
    """
    GDPR compliance requests for data export, deletion, etc.
    """
    REQUEST_TYPES = [
        ('export', 'Data Export'),
        ('deletion', 'Data Deletion'),
        ('rectification', 'Data Rectification'),
        ('portability', 'Data Portability'),
        ('consent_withdrawal', 'Consent Withdrawal'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    request_type = models.CharField(max_length=50, choices=REQUEST_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Additional request details
    details = models.JSONField(default=dict)
    export_file_path = models.CharField(max_length=500, blank=True)
    
    class Meta:
        db_table = 'baserow_gdpr_requests'
        indexes = [
            models.Index(fields=['user', 'requested_at']),
            models.Index(fields=['status', 'requested_at']),
        ]

    def __str__(self):
        return f"{self.request_type} - {self.user} - {self.status}"


class ConsentRecord(models.Model):
    """
    Track user consent for data processing
    """
    CONSENT_TYPES = [
        ('data_processing', 'Data Processing'),
        ('marketing', 'Marketing Communications'),
        ('analytics', 'Analytics'),
        ('third_party_sharing', 'Third Party Data Sharing'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    consent_type = models.CharField(max_length=50, choices=CONSENT_TYPES)
    granted = models.BooleanField(default=False)
    granted_at = models.DateTimeField(null=True, blank=True)
    withdrawn_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        db_table = 'baserow_consent_records'
        unique_together = ['user', 'consent_type']
        indexes = [
            models.Index(fields=['user', 'consent_type']),
            models.Index(fields=['granted_at']),
        ]

    def grant_consent(self, ip_address=None, user_agent=None):
        """Grant consent"""
        self.granted = True
        self.granted_at = timezone.now()
        self.withdrawn_at = None
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.save()

    def withdraw_consent(self):
        """Withdraw consent"""
        self.granted = False
        self.withdrawn_at = timezone.now()
        self.save()


class RateLimitRule(models.Model):
    """
    Rate limiting rules for API access
    """
    name = models.CharField(max_length=255)
    endpoint_pattern = models.CharField(max_length=500)  # Regex pattern for endpoints
    method = models.CharField(max_length=10, blank=True)  # HTTP method (GET, POST, etc.)
    
    # Rate limiting parameters
    requests_per_minute = models.PositiveIntegerField(default=60)
    requests_per_hour = models.PositiveIntegerField(default=1000)
    requests_per_day = models.PositiveIntegerField(default=10000)
    
    # User-specific limits
    user_specific = models.BooleanField(default=True)
    ip_specific = models.BooleanField(default=True)
    
    # Burst allowance
    burst_allowance = models.PositiveIntegerField(default=10)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'baserow_rate_limit_rules'
        indexes = [
            models.Index(fields=['endpoint_pattern']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} - {self.requests_per_minute}/min"


class RateLimitViolation(models.Model):
    """
    Track rate limit violations
    """
    rule = models.ForeignKey(RateLimitRule, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    endpoint = models.CharField(max_length=500)
    method = models.CharField(max_length=10)
    timestamp = models.DateTimeField(auto_now_add=True)
    requests_count = models.PositiveIntegerField()
    
    class Meta:
        db_table = 'baserow_rate_limit_violations'
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
        ]