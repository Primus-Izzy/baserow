from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from baserow.core.models import Workspace
from baserow.contrib.database.models import Table
import uuid
from cryptography.fernet import Fernet
from django.conf import settings
import json

User = get_user_model()


class IntegrationProvider(models.Model):
    """Defines available integration providers (Google, Microsoft, Slack, etc.)"""
    
    PROVIDER_TYPES = [
        ('google', 'Google'),
        ('microsoft', 'Microsoft'),
        ('slack', 'Slack'),
        ('teams', 'Microsoft Teams'),
        ('dropbox', 'Dropbox'),
        ('email', 'Email'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    provider_type = models.CharField(max_length=50, choices=PROVIDER_TYPES)
    display_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    icon_url = models.URLField(blank=True)
    
    # OAuth 2.0 configuration
    client_id = models.CharField(max_length=500, blank=True)
    client_secret = models.TextField(blank=True)  # Encrypted
    authorization_url = models.URLField()
    token_url = models.URLField()
    scope = models.TextField()  # Space-separated scopes
    
    # API configuration
    api_base_url = models.URLField()
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "baserow_integration_provider"
    
    def encrypt_client_secret(self, secret):
        """Encrypt client secret for secure storage"""
        if not secret:
            return ""
        
        key = settings.SECRET_KEY.encode()[:32].ljust(32, b'0')
        f = Fernet(Fernet.generate_key())
        return f.encrypt(secret.encode()).decode()
    
    def decrypt_client_secret(self):
        """Decrypt client secret for use"""
        if not self.client_secret:
            return ""
        
        key = settings.SECRET_KEY.encode()[:32].ljust(32, b'0')
        f = Fernet(key)
        return f.decrypt(self.client_secret.encode()).decode()


class IntegrationConnection(models.Model):
    """User's connection to an integration provider"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('revoked', 'Revoked'),
        ('error', 'Error'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='integration_connections')
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='integration_connections')
    provider = models.ForeignKey(IntegrationProvider, on_delete=models.CASCADE)
    
    # OAuth tokens (encrypted)
    access_token = models.TextField()
    refresh_token = models.TextField(blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)
    
    # Connection metadata
    external_user_id = models.CharField(max_length=200, blank=True)
    external_user_email = models.EmailField(blank=True)
    external_user_name = models.CharField(max_length=200, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    last_sync_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "baserow_integration_connection"
        unique_together = ['user', 'workspace', 'provider']
    
    def encrypt_token(self, token):
        """Encrypt token for secure storage"""
        if not token:
            return ""
        
        key = settings.SECRET_KEY.encode()[:32].ljust(32, b'0')
        f = Fernet(Fernet.generate_key())
        return f.encrypt(token.encode()).decode()
    
    def decrypt_access_token(self):
        """Decrypt access token for use"""
        if not self.access_token:
            return ""
        
        key = settings.SECRET_KEY.encode()[:32].ljust(32, b'0')
        f = Fernet(key)
        return f.decrypt(self.access_token.encode()).decode()


class IntegrationSync(models.Model):
    """Configuration for syncing data between Baserow and external services"""
    
    SYNC_TYPES = [
        ('calendar', 'Calendar Sync'),
        ('file_storage', 'File Storage'),
        ('notifications', 'Notifications'),
        ('data_import', 'Data Import'),
        ('data_export', 'Data Export'),
    ]
    
    SYNC_DIRECTIONS = [
        ('bidirectional', 'Bidirectional'),
        ('import_only', 'Import Only'),
        ('export_only', 'Export Only'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    connection = models.ForeignKey(IntegrationConnection, on_delete=models.CASCADE, related_name='syncs')
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='integration_syncs')
    
    sync_type = models.CharField(max_length=50, choices=SYNC_TYPES)
    sync_direction = models.CharField(max_length=20, choices=SYNC_DIRECTIONS, default='bidirectional')
    
    # Sync configuration
    external_resource_id = models.CharField(max_length=500)  # External calendar ID, folder ID, etc.
    field_mappings = models.JSONField(default=dict)  # Map Baserow fields to external fields
    sync_filters = models.JSONField(default=dict)  # Filters for what data to sync
    
    # Sync settings
    auto_sync_enabled = models.BooleanField(default=True)
    sync_interval_minutes = models.PositiveIntegerField(default=15)  # How often to sync
    
    # Status tracking
    is_active = models.BooleanField(default=True)
    last_sync_at = models.DateTimeField(null=True, blank=True)
    last_sync_status = models.CharField(max_length=20, default='pending')
    sync_error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "baserow_integration_sync"


class IntegrationWebhook(models.Model):
    """Webhook endpoints for receiving updates from external services"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    connection = models.ForeignKey(IntegrationConnection, on_delete=models.CASCADE, related_name='webhooks')
    
    webhook_url = models.URLField()  # The URL external service will call
    webhook_secret = models.CharField(max_length=100)  # For verifying webhook authenticity
    
    event_types = models.JSONField(default=list)  # What events to listen for
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "baserow_integration_webhook"


class IntegrationLog(models.Model):
    """Log of integration activities for debugging and monitoring"""
    
    LOG_LEVELS = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    ]
    
    connection = models.ForeignKey(IntegrationConnection, on_delete=models.CASCADE, related_name='logs')
    level = models.CharField(max_length=10, choices=LOG_LEVELS)
    message = models.TextField()
    details = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "baserow_integration_log"
        ordering = ['-created_at']