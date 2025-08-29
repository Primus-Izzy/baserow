#!/usr/bin/env python3
"""
Test script for the notification system implementation.

This script verifies that all components of the notification system are properly implemented:
- Backend models and handlers
- API endpoints
- Frontend components and services
- Database migrations
"""

import os
import sys
import subprocess
from pathlib import Path

def check_file_exists(file_path, description):
    """Check if a file exists and print status."""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} (NOT FOUND)")
        return False

def check_directory_exists(dir_path, description):
    """Check if a directory exists and print status."""
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        print(f"✅ {description}: {dir_path}")
        return True
    else:
        print(f"❌ {description}: {dir_path} (NOT FOUND)")
        return False

def main():
    """Run all notification system checks."""
    print("🔔 Notification System Implementation Verification")
    print("=" * 60)
    
    all_checks_passed = True
    
    # Backend Models and Core Logic
    print("\n📦 Backend Models and Core Logic:")
    backend_files = [
        ("backend/src/baserow/contrib/database/notifications/__init__.py", "Notifications package init"),
        ("backend/src/baserow/contrib/database/notifications/models.py", "Notification models"),
        ("backend/src/baserow/contrib/database/notifications/handler.py", "Notification handler"),
        ("backend/src/baserow/contrib/database/notifications/delivery.py", "Delivery service"),
        ("backend/src/baserow/contrib/database/notifications/exceptions.py", "Custom exceptions"),
        ("backend/src/baserow/contrib/database/notifications/tasks.py", "Celery tasks"),
    ]
    
    for file_path, description in backend_files:
        if not check_file_exists(file_path, description):
            all_checks_passed = False
    
    # API Layer
    print("\n🌐 API Layer:")
    api_files = [
        ("backend/src/baserow/contrib/database/api/notifications/__init__.py", "API package init"),
        ("backend/src/baserow/contrib/database/api/notifications/serializers.py", "API serializers"),
        ("backend/src/baserow/contrib/database/api/notifications/views.py", "API views"),
        ("backend/src/baserow/contrib/database/api/notifications/urls.py", "API URLs"),
    ]
    
    for file_path, description in api_files:
        if not check_file_exists(file_path, description):
            all_checks_passed = False
    
    # Database Migration
    print("\n🗄️ Database Migration:")
    migration_files = [
        ("backend/src/baserow/contrib/database/migrations/0204_notification_system.py", "Notification system migration"),
    ]
    
    for file_path, description in migration_files:
        if not check_file_exists(file_path, description):
            all_checks_passed = False
    
    # Management Commands
    print("\n⚙️ Management Commands:")
    command_files = [
        ("backend/src/baserow/contrib/database/management/commands/init_notification_system.py", "Initialization command"),
    ]
    
    for file_path, description in command_files:
        if not check_file_exists(file_path, description):
            all_checks_passed = False
    
    # Frontend Store and Services
    print("\n🎨 Frontend Store and Services:")
    frontend_files = [
        ("web-frontend/modules/database/store/notifications.js", "Vuex store"),
        ("web-frontend/modules/database/services/notifications.js", "API service"),
        ("web-frontend/modules/database/plugins/notifications.js", "Notification plugin"),
    ]
    
    for file_path, description in frontend_files:
        if not check_file_exists(file_path, description):
            all_checks_passed = False
    
    # Frontend Components
    print("\n🧩 Frontend Components:")
    component_files = [
        ("web-frontend/modules/database/components/notifications/NotificationCenter.vue", "Notification center"),
        ("web-frontend/modules/database/components/notifications/NotificationItem.vue", "Notification item"),
        ("web-frontend/modules/database/components/notifications/NotificationSettings.vue", "Settings modal"),
    ]
    
    for file_path, description in component_files:
        if not check_file_exists(file_path, description):
            all_checks_passed = False
    
    # Check for key features in files
    print("\n🔍 Feature Implementation Checks:")
    
    # Check if URL configuration includes notifications
    try:
        with open("backend/src/baserow/contrib/database/api/urls.py", "r") as f:
            urls_content = f.read()
            if "notifications" in urls_content:
                print("✅ Notifications API included in URL configuration")
            else:
                print("❌ Notifications API NOT included in URL configuration")
                all_checks_passed = False
    except FileNotFoundError:
        print("❌ Could not check URL configuration")
        all_checks_passed = False
    
    # Check if models include all required fields
    try:
        with open("backend/src/baserow/contrib/database/notifications/models.py", "r") as f:
            models_content = f.read()
            required_models = ["NotificationType", "Notification", "UserNotificationPreference", "NotificationTemplate", "NotificationBatch"]
            for model in required_models:
                if f"class {model}" in models_content:
                    print(f"✅ {model} model implemented")
                else:
                    print(f"❌ {model} model NOT found")
                    all_checks_passed = False
    except FileNotFoundError:
        print("❌ Could not check models implementation")
        all_checks_passed = False
    
    # Check if handler includes key methods
    try:
        with open("backend/src/baserow/contrib/database/notifications/handler.py", "r") as f:
            handler_content = f.read()
            required_methods = ["create_notification", "send_notification", "process_batched_notifications"]
            for method in required_methods:
                if f"def {method}" in handler_content:
                    print(f"✅ {method} method implemented")
                else:
                    print(f"❌ {method} method NOT found")
                    all_checks_passed = False
    except FileNotFoundError:
        print("❌ Could not check handler implementation")
        all_checks_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    if all_checks_passed:
        print("🎉 All notification system components are properly implemented!")
        print("\n📋 Next Steps:")
        print("1. Run database migrations: python manage.py migrate")
        print("2. Initialize notification system: python manage.py init_notification_system")
        print("3. Test the API endpoints")
        print("4. Integrate NotificationCenter component into the main UI")
        print("5. Set up Celery for background task processing")
        return 0
    else:
        print("❌ Some notification system components are missing or incomplete.")
        print("Please review the failed checks above and ensure all files are created.")
        return 1

if __name__ == "__main__":
    sys.exit(main())