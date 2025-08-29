from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils import timezone
from django.conf import settings
from baserow.contrib.dashboard.models import Dashboard, DashboardPermission, DashboardExport
from baserow.core.exceptions import UserNotInWorkspace
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class DashboardSharingHandler:
    """Handler for dashboard sharing and permissions."""
    
    def create_public_link(self, dashboard, user):
        """Create a public sharing link for a dashboard."""
        if not self.user_can_share_dashboard(dashboard, user):
            raise PermissionDenied("You don't have permission to share this dashboard")
        
        dashboard.permission_level = 'public'
        token = dashboard.generate_public_token()
        dashboard.save(update_fields=['permission_level'])
        
        return {
            'public_url': f"{settings.PUBLIC_BACKEND_URL}/dashboard/public/{token}",
            'token': token
        }
    
    def create_embed_link(self, dashboard, user, widget_ids=None):
        """Create an embed link for dashboard or specific widgets."""
        if not self.user_can_share_dashboard(dashboard, user):
            raise PermissionDenied("You don't have permission to embed this dashboard")
        
        if widget_ids:
            # Generate embed tokens for specific widgets
            widgets = dashboard.widgets.filter(id__in=widget_ids)
            embed_data = []
            
            for widget in widgets:
                widget.is_embeddable = True
                token = widget.generate_embed_token()
                widget.save(update_fields=['is_embeddable'])
                
                embed_data.append({
                    'widget_id': str(widget.id),
                    'embed_url': f"{settings.PUBLIC_BACKEND_URL}/dashboard/embed/widget/{token}",
                    'token': token
                })
            
            return {'widgets': embed_data}
        else:
            # Generate embed token for entire dashboard
            token = dashboard.generate_embed_token()
            return {
                'embed_url': f"{settings.PUBLIC_BACKEND_URL}/dashboard/embed/{token}",
                'token': token
            }
    
    def revoke_public_access(self, dashboard, user):
        """Revoke public access to a dashboard."""
        if not self.user_can_share_dashboard(dashboard, user):
            raise PermissionDenied("You don't have permission to modify sharing settings")
        
        dashboard.revoke_public_access()
        
        # Also revoke widget embed tokens
        dashboard.widgets.update(is_embeddable=False, embed_token=None)
        
        return True
    
    def set_dashboard_permission(self, dashboard, target_user, permission_type, granting_user):
        """Set specific permissions for a user on a dashboard."""
        if not self.user_can_manage_permissions(dashboard, granting_user):
            raise PermissionDenied("You don't have permission to manage dashboard permissions")
        
        # Check if target user is in the same workspace
        if not dashboard.workspace.users.filter(id=target_user.id).exists():
            raise UserNotInWorkspace("User is not a member of this workspace")
        
        permission, created = DashboardPermission.objects.update_or_create(
            dashboard=dashboard,
            user=target_user,
            defaults={
                'permission_type': permission_type,
                'granted_by': granting_user
            }
        )
        
        return permission
    
    def remove_dashboard_permission(self, dashboard, target_user, granting_user):
        """Remove specific permissions for a user on a dashboard."""
        if not self.user_can_manage_permissions(dashboard, granting_user):
            raise PermissionDenied("You don't have permission to manage dashboard permissions")
        
        DashboardPermission.objects.filter(
            dashboard=dashboard,
            user=target_user
        ).delete()
        
        return True
    
    def get_dashboard_permissions(self, dashboard, user):
        """Get all permissions for a dashboard."""
        if not self.user_can_view_dashboard(dashboard, user):
            raise PermissionDenied("You don't have permission to view this dashboard")
        
        permissions = DashboardPermission.objects.filter(
            dashboard=dashboard
        ).select_related('user', 'granted_by')
        
        return [
            {
                'user_id': perm.user.id,
                'user_email': perm.user.email,
                'permission_type': perm.permission_type,
                'granted_by': perm.granted_by.email,
                'created_at': perm.created_at
            }
            for perm in permissions
        ]
    
    def user_can_view_dashboard(self, dashboard, user):
        """Check if user can view a dashboard."""
        if not user or not user.is_authenticated:
            return dashboard.permission_level == 'public'
        
        # Dashboard creator can always view
        if dashboard.created_by_id == user.id:
            return True
        
        # Check workspace membership for workspace-level permissions
        if dashboard.permission_level == 'workspace':
            return dashboard.workspace.users.filter(id=user.id).exists()
        
        # Check explicit permissions
        return DashboardPermission.objects.filter(
            dashboard=dashboard,
            user=user,
            permission_type__in=['view', 'edit', 'admin']
        ).exists()
    
    def user_can_edit_dashboard(self, dashboard, user):
        """Check if user can edit a dashboard."""
        if not user or not user.is_authenticated:
            return False
        
        # Dashboard creator can always edit
        if dashboard.created_by_id == user.id:
            return True
        
        # Check explicit permissions
        return DashboardPermission.objects.filter(
            dashboard=dashboard,
            user=user,
            permission_type__in=['edit', 'admin']
        ).exists()
    
    def user_can_share_dashboard(self, dashboard, user):
        """Check if user can share a dashboard."""
        if not user or not user.is_authenticated:
            return False
        
        # Dashboard creator can always share
        if dashboard.created_by_id == user.id:
            return True
        
        # Check admin permissions
        return DashboardPermission.objects.filter(
            dashboard=dashboard,
            user=user,
            permission_type='admin'
        ).exists()
    
    def user_can_manage_permissions(self, dashboard, user):
        """Check if user can manage dashboard permissions."""
        return self.user_can_share_dashboard(dashboard, user)
    
    def get_public_dashboard_by_token(self, token):
        """Get a dashboard by its public token."""
        try:
            dashboard = Dashboard.objects.get(
                public_token=token,
                permission_level='public'
            )
            return dashboard
        except Dashboard.DoesNotExist:
            return None
    
    def get_embeddable_dashboard_by_token(self, token):
        """Get a dashboard by its embed token."""
        try:
            dashboard = Dashboard.objects.get(embed_token=token)
            return dashboard
        except Dashboard.DoesNotExist:
            return None
    
    def get_embeddable_widget_by_token(self, token):
        """Get a widget by its embed token."""
        try:
            from baserow.contrib.dashboard.models import DashboardWidget
            widget = DashboardWidget.objects.get(
                embed_token=token,
                is_embeddable=True
            )
            return widget
        except DashboardWidget.DoesNotExist:
            return None


# Singleton instance
dashboard_sharing_handler = DashboardSharingHandler()