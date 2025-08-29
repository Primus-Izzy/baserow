from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from baserow.contrib.database.models import Row
from .models import IntegrationSync
from .tasks import run_integration_sync


@receiver(post_save, sender=Row)
def trigger_sync_on_row_change(sender, instance, created, **kwargs):
    """Trigger integration sync when a row is created or updated"""
    table = instance.table
    
    # Find active syncs for this table
    syncs = IntegrationSync.objects.filter(
        table=table,
        is_active=True,
        auto_sync_enabled=True,
        connection__status='active'
    )
    
    for sync in syncs:
        # Only trigger if sync direction allows export
        if sync.sync_direction in ['bidirectional', 'export_only']:
            run_integration_sync.delay(str(sync.id))


@receiver(post_delete, sender=Row)
def trigger_sync_on_row_delete(sender, instance, **kwargs):
    """Trigger integration sync when a row is deleted"""
    table = instance.table
    
    # Find active syncs for this table
    syncs = IntegrationSync.objects.filter(
        table=table,
        is_active=True,
        auto_sync_enabled=True,
        connection__status='active'
    )
    
    for sync in syncs:
        # Only trigger if sync direction allows export
        if sync.sync_direction in ['bidirectional', 'export_only']:
            run_integration_sync.delay(str(sync.id))