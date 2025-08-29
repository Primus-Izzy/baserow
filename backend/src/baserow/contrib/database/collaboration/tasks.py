from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from baserow.contrib.database.collaboration.handler import CollaborationHandler


@shared_task
def cleanup_stale_collaboration_data():
    """
    Periodic task to clean up stale collaboration data.
    Should be run every 5 minutes.
    """
    handler = CollaborationHandler()
    handler.cleanup_stale_data(
        presence_minutes=10,  # Remove presence older than 10 minutes
        session_seconds=60,   # Remove sessions older than 60 seconds
    )


@shared_task
def broadcast_collaboration_stats():
    """
    Periodic task to broadcast collaboration statistics.
    Should be run every minute.
    """
    from baserow.contrib.database.table.models import Table
    from baserow.ws.tasks import broadcast_to_channel_group
    
    handler = CollaborationHandler()
    
    # Get all tables with recent activity
    tables_with_activity = Table.objects.filter(
        userpresence__last_seen__gte=timezone.now() - timedelta(minutes=15)
    ).distinct()
    
    for table in tables_with_activity:
        stats = handler.get_collaboration_stats(table)
        
        # Broadcast stats to table collaboration group
        broadcast_to_channel_group.delay(
            f"collaboration-table-{table.id}",
            {
                "type": "collaboration_stats",
                "table_id": table.id,
                "stats": stats,
            }
        )