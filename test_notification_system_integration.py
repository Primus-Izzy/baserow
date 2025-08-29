#!/usr/bin/env python3
"""
Test script to verify the notification system integration is working properly.
"""

import os
import sys
import django

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'baserow.config.settings.test')
django.setup()

from django.contrib.auth import get_user_model
from django.test import TestCase
from baserow.contrib.database.notifications.handler import notification_handler
from baserow.contrib.database.notifications.models import (
    NotificationType, 
    Notification,
    UserNotificationPreference
)

User = get_user_model()

def test_notification_system():
    """Test the basic notification system functionality."""
    
    print("🔔 Testing Baserow Notification System Integration")
    print("=" * 50)
    
    # Test 1: Check if notification types exist
    print("1. Checking notification types...")
    notification_types = NotificationType.objects.all()
    print(f"   Found {notification_types.count()} notification types:")
    for nt in notification_types:
        print(f"   - {nt.name} ({nt.category})")
    
    if notification_types.count() == 0:
        print("   ❌ No notification types found. Run: python manage.py init_notification_system")
        return False
    
    # Test 2: Create a test user
    print("\n2. Creating test user...")
    try:
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        print(f"   ✅ Created user: {user.email}")
    except Exception as e:
        print(f"   ❌ Failed to create user: {e}")
        return False
    
    # Test 3: Create a notification
    print("\n3. Creating test notification...")
    try:
        notifications = notification_handler.create_notification(
            notification_type='comment_mention',
            recipient=user,
            title='Test notification',
            message='This is a test notification to verify the system is working',
            data={
                'commenter_name': 'John Doe',
                'table_name': 'Test Table',
                'comment_text': 'Hello @test!'
            }
        )
        print(f"   ✅ Created {len(notifications)} notification(s)")
        
        for notification in notifications:
            print(f"   - ID: {notification.id}, Method: {notification.delivery_method}, Status: {notification.status}")
    
    except Exception as e:
        print(f"   ❌ Failed to create notification: {e}")
        return False
    
    # Test 4: Check user preferences
    print("\n4. Checking user preferences...")
    try:
        comment_type = NotificationType.objects.get(name='comment_mention')
        preferences = notification_handler.get_user_preferences(user, comment_type)
        print(f"   ✅ User preferences: in_app={preferences.in_app_enabled}, email={preferences.email_enabled}")
    except Exception as e:
        print(f"   ❌ Failed to get preferences: {e}")
        return False
    
    # Test 5: Get unread notifications
    print("\n5. Getting unread notifications...")
    try:
        unread = notification_handler.get_unread_notifications(user)
        print(f"   ✅ Found {len(unread)} unread notification(s)")
        
        for notification in unread:
            print(f"   - {notification.title}: {notification.message}")
    except Exception as e:
        print(f"   ❌ Failed to get unread notifications: {e}")
        return False
    
    # Test 6: Mark as read
    print("\n6. Marking notifications as read...")
    try:
        if unread:
            count = notification_handler.mark_notifications_as_read(
                user, 
                [n.id for n in unread]
            )
            print(f"   ✅ Marked {count} notification(s) as read")
        else:
            print("   ℹ️  No notifications to mark as read")
    except Exception as e:
        print(f"   ❌ Failed to mark notifications as read: {e}")
        return False
    
    # Cleanup
    print("\n7. Cleaning up...")
    try:
        Notification.objects.filter(recipient=user).delete()
        UserNotificationPreference.objects.filter(user=user).delete()
        user.delete()
        print("   ✅ Cleanup completed")
    except Exception as e:
        print(f"   ❌ Cleanup failed: {e}")
    
    print("\n🎉 All tests passed! Notification system is working properly.")
    return True

if __name__ == '__main__':
    success = test_notification_system()
    sys.exit(0 if success else 1)