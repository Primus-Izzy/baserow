from django.db import models
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from baserow.core.models import Workspace
import uuid

User = get_user_model()


class Dashboard(models.Model):
    """Enhanced dashboard model with sharing and permissions."""
    
    PERMISSION_CHOICES = [
        ('private', 'Private'),
        ('workspace', 'Workspace Members'),
        ('public', 'Public'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='dashboards')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_dashboards')
    layout = models.JSONField(default=dict)
    
    # Sharing and permissions
    permission_level = models.CharField(max_length=20, choices=PERMISSION_CHOICES, default='private')
    public_token = models.CharField(max_length=64, unique=True, null=True, blank=True)
    embed_token = models.CharField(max_length=64, unique=True, null=True, blank=True)
    
    # Export settings
    export_settings = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'dashboard_dashboard'
        
    def generate_public_token(self):
        """Generate a unique public sharing token."""
        if not self.public_token:
            self.public_token = get_random_string(64)
            self.save(update_fields=['public_token'])
        return self.public_token
    
    def generate_embed_token(self):
        """Generate a unique embedding token."""
        if not self.embed_token:
            self.embed_token = get_random_string(64)
            self.save(update_fields=['embed_token'])
        return self.embed_token
    
    def revoke_public_access(self):
        """Revoke public access by clearing tokens."""
        self.public_token = None
        self.embed_token = None
        self.permission_level = 'private'
        self.save(update_fields=['public_token', 'embed_token', 'permission_level'])


class DashboardPermission(models.Model):
    """Granular dashboard permissions for users and groups."""
    
    PERMISSION_TYPES = [
        ('view', 'View'),
        ('edit', 'Edit'),
        ('admin', 'Admin'),
    ]
    
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='permissions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    permission_type = models.CharField(max_length=10, choices=PERMISSION_TYPES)
    granted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='granted_permissions')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'dashboard_permission'
        unique_together = ['dashboard', 'user']


class DashboardExport(models.Model):
    """Track dashboard export jobs and scheduled exports."""
    
    EXPORT_FORMATS = [
        ('pdf', 'PDF'),
        ('png', 'PNG'),
        ('csv', 'CSV'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='exports')
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE)
    export_format = models.CharField(max_length=10, choices=EXPORT_FORMATS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Export configuration
    configuration = models.JSONField(default=dict)
    
    # File storage
    file_path = models.CharField(max_length=500, null=True, blank=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)
    
    # Scheduling
    is_scheduled = models.BooleanField(default=False)
    schedule_config = models.JSONField(default=dict)  # cron-like configuration
    next_run = models.DateTimeField(null=True, blank=True)
    
    # Delivery
    delivery_email = models.EmailField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'dashboard_export'


class DashboardWidget(models.Model):
    """Enhanced widget model with embedding support."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='widgets')
    widget_type = models.CharField(max_length=50)
    configuration = models.JSONField(default=dict)
    position = models.JSONField(default=dict)
    
    # Embedding
    embed_token = models.CharField(max_length=64, unique=True, null=True, blank=True)
    is_embeddable = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'dashboard_widget'
        
    def generate_embed_token(self):
        """Generate a unique embedding token for this widget."""
        if not self.embed_token:
            self.embed_token = get_random_string(64)
            self.save(update_fields=['embed_token'])
        return self.embed_token