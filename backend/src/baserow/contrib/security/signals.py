from django.db.models.signals import post_save, post_delete, pre_delete
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone

from baserow.core.models import Workspace
from baserow.contrib.database.models import Database, Table

from .handler import SecurityHandler

User = get_user_model()


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """
    Log successful user login.
    """
    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    SecurityHandler.log_security_event(
        event_type='login',
        user=user,
        ip_address=ip_address,
        user_agent=user_agent,
        details={'login_method': 'password'},
        severity='low'
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """
    Log user logout.
    """
    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    SecurityHandler.log_security_event(
        event_type='logout',
        user=user,
        ip_address=ip_address,
        user_agent=user_agent,
        severity='low'
    )


@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    """
    Log failed login attempts.
    """
    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    SecurityHandler.log_security_event(
        event_type='failed_login',
        ip_address=ip_address,
        user_agent=user_agent,
        details={
            'attempted_username': credentials.get('username', ''),
            'failure_reason': 'invalid_credentials'
        },
        severity='medium',
        success=False
    )


@receiver(post_save, sender=User)
def log_user_changes(sender, instance, created, **kwargs):
    """
    Log user account changes.
    """
    if created:
        SecurityHandler.log_security_event(
            event_type='user_created',
            user=instance,
            details={
                'username': instance.username,
                'email': instance.email
            },
            severity='low'
        )
    else:
        SecurityHandler.log_security_event(
            event_type='user_updated',
            user=instance,
            details={
                'username': instance.username,
                'email': instance.email
            },
            severity='low'
        )


@receiver(pre_delete, sender=User)
def log_user_deletion(sender, instance, **kwargs):
    """
    Log user account deletion.
    """
    SecurityHandler.log_security_event(
        event_type='user_deleted',
        user=instance,
        details={
            'username': instance.username,
            'email': instance.email
        },
        severity='high'
    )


@receiver(post_save, sender=Workspace)
def log_workspace_changes(sender, instance, created, **kwargs):
    """
    Log workspace changes.
    """
    event_type = 'workspace_created' if created else 'workspace_updated'
    
    SecurityHandler.log_security_event(
        event_type=event_type,
        details={
            'workspace_id': instance.id,
            'workspace_name': instance.name
        },
        severity='low',
        content_object=instance
    )


@receiver(pre_delete, sender=Workspace)
def log_workspace_deletion(sender, instance, **kwargs):
    """
    Log workspace deletion.
    """
    SecurityHandler.log_security_event(
        event_type='workspace_deleted',
        details={
            'workspace_id': instance.id,
            'workspace_name': instance.name
        },
        severity='medium',
        content_object=instance
    )


@receiver(post_save, sender=Database)
def log_database_changes(sender, instance, created, **kwargs):
    """
    Log database changes.
    """
    event_type = 'database_created' if created else 'database_updated'
    
    SecurityHandler.log_security_event(
        event_type=event_type,
        details={
            'database_id': instance.id,
            'database_name': instance.name,
            'workspace_id': instance.workspace.id
        },
        severity='low',
        content_object=instance
    )


@receiver(pre_delete, sender=Database)
def log_database_deletion(sender, instance, **kwargs):
    """
    Log database deletion.
    """
    SecurityHandler.log_security_event(
        event_type='database_deleted',
        details={
            'database_id': instance.id,
            'database_name': instance.name,
            'workspace_id': instance.workspace.id
        },
        severity='medium',
        content_object=instance
    )


@receiver(post_save, sender=Table)
def log_table_changes(sender, instance, created, **kwargs):
    """
    Log table changes.
    """
    event_type = 'table_created' if created else 'table_updated'
    
    SecurityHandler.log_security_event(
        event_type=event_type,
        details={
            'table_id': instance.id,
            'table_name': instance.name,
            'database_id': instance.database.id
        },
        severity='low',
        content_object=instance
    )


@receiver(pre_delete, sender=Table)
def log_table_deletion(sender, instance, **kwargs):
    """
    Log table deletion.
    """
    SecurityHandler.log_security_event(
        event_type='table_deleted',
        details={
            'table_id': instance.id,
            'table_name': instance.name,
            'database_id': instance.database.id
        },
        severity='medium',
        content_object=instance
    )


def get_client_ip(request):
    """
    Get the client's IP address from the request.
    """
    if not request:
        return None
        
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip