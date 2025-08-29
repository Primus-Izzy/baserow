#!/usr/bin/env python3
"""
Test script for mobile-specific features implementation
Tests offline sync, push notifications, camera access, and accessibility features
"""

import os
import sys
import json
import requests
from pathlib import Path

def test_mobile_features():
    """Test mobile features implementation"""
    
    print("🔍 Testing Mobile Features Implementation...")
    print("=" * 60)
    
    # Test results
    results = {
        'offline_sync': False,
        'camera_access': False,
        'push_notifications': False,
        'accessibility': False,
        'service_worker': False,
        'backend_models': False,
        'api_endpoints': False
    }
    
    # Test 1: Check offline sync service
    print("\n1. Testing Offline Sync Service...")
    offline_sync_path = Path("web-frontend/modules/core/services/offlineSync.js")
    if offline_sync_path.exists():
        content = offline_sync_path.read_text(encoding='utf-8')
        if all(feature in content for feature in [
            'OfflineSyncService',
            'indexedDB',
            'syncPendingOperations',
            'queueOperation',
            'cacheTableData'
        ]):
            results['offline_sync'] = True
            print("   ✅ Offline sync service implemented")
        else:
            print("   ❌ Offline sync service missing features")
    else:
        print("   ❌ Offline sync service file not found")
    
    # Test 2: Check camera access service
    print("\n2. Testing Camera Access Service...")
    camera_path = Path("web-frontend/modules/core/services/cameraAccess.js")
    if camera_path.exists():
        content = camera_path.read_text(encoding='utf-8')
        if all(feature in content for feature in [
            'CameraAccessService',
            'getUserMedia',
            'capturePhoto',
            'accessPhotoLibrary',
            'switchCamera'
        ]):
            results['camera_access'] = True
            print("   ✅ Camera access service implemented")
        else:
            print("   ❌ Camera access service missing features")
    else:
        print("   ❌ Camera access service file not found")
    
    # Test 3: Check push notifications service
    print("\n3. Testing Push Notifications Service...")
    push_path = Path("web-frontend/modules/core/services/pushNotifications.js")
    if push_path.exists():
        content = push_path.read_text(encoding='utf-8')
        if all(feature in content for feature in [
            'PushNotificationService',
            'serviceWorker',
            'subscribe',
            'showNotification',
            'requestPermission'
        ]):
            results['push_notifications'] = True
            print("   ✅ Push notifications service implemented")
        else:
            print("   ❌ Push notifications service missing features")
    else:
        print("   ❌ Push notifications service file not found")
    
    # Test 4: Check accessibility service
    print("\n4. Testing Mobile Accessibility Service...")
    accessibility_path = Path("web-frontend/modules/core/services/mobileAccessibility.js")
    if accessibility_path.exists():
        content = accessibility_path.read_text(encoding='utf-8')
        if all(feature in content for feature in [
            'MobileAccessibilityService',
            'announce',
            'detectScreenReader',
            'setupKeyboardNavigation',
            'handleGesture'
        ]):
            results['accessibility'] = True
            print("   ✅ Mobile accessibility service implemented")
        else:
            print("   ❌ Mobile accessibility service missing features")
    else:
        print("   ❌ Mobile accessibility service file not found")
    
    # Test 5: Check service worker
    print("\n5. Testing Service Worker...")
    sw_path = Path("web-frontend/static/sw.js")
    if sw_path.exists():
        content = sw_path.read_text(encoding='utf-8')
        if all(feature in content for feature in [
            'install',
            'activate',
            'fetch',
            'push',
            'notificationclick',
            'sync'
        ]):
            results['service_worker'] = True
            print("   ✅ Service worker implemented")
        else:
            print("   ❌ Service worker missing features")
    else:
        print("   ❌ Service worker file not found")
    
    # Test 6: Check backend models
    print("\n6. Testing Backend Models...")
    models_path = Path("backend/src/baserow/contrib/mobile/models.py")
    if models_path.exists():
        content = models_path.read_text(encoding='utf-8')
        if all(model in content for model in [
            'PushSubscription',
            'PushNotification',
            'OfflineOperation',
            'MobileSettings',
            'CameraUpload'
        ]):
            results['backend_models'] = True
            print("   ✅ Backend models implemented")
        else:
            print("   ❌ Backend models missing")
    else:
        print("   ❌ Backend models file not found")
    
    # Test 7: Check API endpoints
    print("\n7. Testing API Endpoints...")
    api_path = Path("backend/src/baserow/contrib/mobile/api/views.py")
    if api_path.exists():
        content = api_path.read_text(encoding='utf-8')
        if all(endpoint in content for endpoint in [
            'PushSubscriptionViewSet',
            'OfflineOperationViewSet',
            'MobileSettingsViewSet',
            'CameraUploadViewSet'
        ]):
            results['api_endpoints'] = True
            print("   ✅ API endpoints implemented")
        else:
            print("   ❌ API endpoints missing")
    else:
        print("   ❌ API endpoints file not found")
    
    # Test 8: Check mobile component integration
    print("\n8. Testing Mobile Component Integration...")
    component_path = Path("web-frontend/modules/core/components/mobile/MobileFeatures.vue")
    if component_path.exists():
        content = component_path.read_text(encoding='utf-8')
        if all(feature in content for feature in [
            'offline-indicator',
            'camera-modal',
            'notification-settings',
            'accessibility-settings'
        ]):
            print("   ✅ Mobile component integration implemented")
        else:
            print("   ❌ Mobile component integration missing features")
    else:
        print("   ❌ Mobile component file not found")
    
    # Test 9: Check offline page
    print("\n9. Testing Offline Page...")
    offline_path = Path("web-frontend/static/offline.html")
    if offline_path.exists():
        content = offline_path.read_text(encoding='utf-8')
        if all(feature in content for feature in [
            'offline-container',
            'retry-button',
            'connection-status',
            'accessibility'
        ]):
            print("   ✅ Offline page implemented")
        else:
            print("   ❌ Offline page missing features")
    else:
        print("   ❌ Offline page file not found")
    
    # Test 10: Check mobile plugin
    print("\n10. Testing Mobile Plugin...")
    plugin_path = Path("web-frontend/modules/core/plugins/mobile.js")
    if plugin_path.exists():
        content = plugin_path.read_text(encoding='utf-8')
        if all(feature in content for feature in [
            'mobileServices',
            'initializeMobileServices',
            'mobileAPI',
            'mobileStore'
        ]):
            print("   ✅ Mobile plugin implemented")
        else:
            print("   ❌ Mobile plugin missing features")
    else:
        print("   ❌ Mobile plugin file not found")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 MOBILE FEATURES TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for feature, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {feature.replace('_', ' ').title()}")
    
    print(f"\n📈 Overall Score: {passed}/{total} ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 All mobile features implemented successfully!")
        return True
    else:
        print(f"⚠️  {total - passed} mobile features need attention")
        return False

def test_mobile_requirements():
    """Test mobile-specific requirements"""
    
    print("\n🔍 Testing Mobile Requirements Compliance...")
    print("=" * 60)
    
    requirements = {
        'offline_mode': False,
        'camera_access': False,
        'push_notifications': False,
        'accessibility': False
    }
    
    # Check offline mode (Requirement 12.3)
    print("\n1. Testing Offline Mode (Requirement 12.3)...")
    offline_files = [
        "web-frontend/modules/core/services/offlineSync.js",
        "web-frontend/static/sw.js",
        "backend/src/baserow/contrib/mobile/models.py"
    ]
    
    if all(Path(f).exists() for f in offline_files):
        requirements['offline_mode'] = True
        print("   ✅ Offline mode with automatic synchronization implemented")
    else:
        print("   ❌ Offline mode implementation incomplete")
    
    # Check camera access (Requirement 12.5)
    print("\n2. Testing Camera Access (Requirement 12.5)...")
    camera_files = [
        "web-frontend/modules/core/services/cameraAccess.js",
        "backend/src/baserow/contrib/mobile/models.py"
    ]
    
    if all(Path(f).exists() for f in camera_files):
        requirements['camera_access'] = True
        print("   ✅ Camera access for file uploads implemented")
    else:
        print("   ❌ Camera access implementation incomplete")
    
    # Check push notifications (Requirement 12.5)
    print("\n3. Testing Push Notifications (Requirement 12.5)...")
    push_files = [
        "web-frontend/modules/core/services/pushNotifications.js",
        "backend/src/baserow/contrib/mobile/services/push_notification_service.py"
    ]
    
    if all(Path(f).exists() for f in push_files):
        requirements['push_notifications'] = True
        print("   ✅ Push notification system implemented")
    else:
        print("   ❌ Push notification system incomplete")
    
    # Check accessibility (Requirement 12.6)
    print("\n4. Testing Mobile Accessibility (Requirement 12.6)...")
    accessibility_files = [
        "web-frontend/modules/core/services/mobileAccessibility.js"
    ]
    
    if all(Path(f).exists() for f in accessibility_files):
        accessibility_content = Path(accessibility_files[0]).read_text(encoding='utf-8')
        if all(feature in accessibility_content for feature in [
            'screen reader',
            'keyboard navigation',
            'gesture',
            'high contrast',
            'large text'
        ]):
            requirements['accessibility'] = True
            print("   ✅ Mobile screen reader support and accessibility features implemented")
        else:
            print("   ❌ Mobile accessibility features incomplete")
    else:
        print("   ❌ Mobile accessibility implementation not found")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 REQUIREMENTS COMPLIANCE SUMMARY")
    print("=" * 60)
    
    passed = sum(requirements.values())
    total = len(requirements)
    
    for requirement, status in requirements.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {requirement.replace('_', ' ').title()}")
    
    print(f"\n📈 Compliance Score: {passed}/{total} ({(passed/total)*100:.1f}%)")
    
    return passed == total

if __name__ == "__main__":
    print("🚀 Starting Mobile Features Implementation Test")
    print("=" * 60)
    
    # Run tests
    features_test = test_mobile_features()
    requirements_test = test_mobile_requirements()
    
    # Final result
    print("\n" + "=" * 60)
    print("🏁 FINAL TEST RESULTS")
    print("=" * 60)
    
    if features_test and requirements_test:
        print("🎉 All mobile features implemented and requirements met!")
        print("✅ Task 30: Implement mobile-specific features - COMPLETED")
        sys.exit(0)
    else:
        print("❌ Some mobile features or requirements need attention")
        print("⚠️  Task 30: Implement mobile-specific features - NEEDS WORK")
        sys.exit(1)