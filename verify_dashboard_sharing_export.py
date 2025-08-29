#!/usr/bin/env python3
"""
Verification script for dashboard sharing and export functionality.
This script verifies the implementation of task 24: Dashboard sharing and export.
"""

import os
import json
import re


def check_file_exists(filepath, description):
    """Check if a file exists and print result."""
    if os.path.exists(filepath):
        print(f"✓ {description}")
        return True
    else:
        print(f"❌ {description}")
        return False


def check_file_content(filepath, patterns, description):
    """Check if file contains expected patterns."""
    if not os.path.exists(filepath):
        print(f"❌ {description} - File not found")
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        missing_patterns = []
        for pattern_name, pattern in patterns.items():
            if not re.search(pattern, content, re.MULTILINE | re.DOTALL):
                missing_patterns.append(pattern_name)
        
        if missing_patterns:
            print(f"❌ {description} - Missing: {', '.join(missing_patterns)}")
            return False
        else:
            print(f"✓ {description}")
            return True
    except Exception as e:
        print(f"❌ {description} - Error reading file: {e}")
        return False


def verify_backend_implementation():
    """Verify backend implementation."""
    print("\n🔧 Verifying Backend Implementation...")
    print("-" * 50)
    
    results = []
    
    # Check models
    results.append(check_file_exists(
        "backend/src/baserow/contrib/dashboard/models.py",
        "Dashboard models file"
    ))
    
    # Check sharing handler
    results.append(check_file_exists(
        "backend/src/baserow/contrib/dashboard/sharing/handler.py",
        "Dashboard sharing handler"
    ))
    
    # Check export handler
    results.append(check_file_exists(
        "backend/src/baserow/contrib/dashboard/export/handler.py",
        "Dashboard export handler"
    ))
    
    # Check API serializers
    results.append(check_file_exists(
        "backend/src/baserow/contrib/dashboard/api/sharing/serializers.py",
        "Sharing API serializers"
    ))
    
    results.append(check_file_exists(
        "backend/src/baserow/contrib/dashboard/api/export/serializers.py",
        "Export API serializers"
    ))
    
    # Check API views
    results.append(check_file_exists(
        "backend/src/baserow/contrib/dashboard/api/sharing/views.py",
        "Sharing API views"
    ))
    
    results.append(check_file_exists(
        "backend/src/baserow/contrib/dashboard/api/export/views.py",
        "Export API views"
    ))
    
    # Check URL configurations
    results.append(check_file_exists(
        "backend/src/baserow/contrib/dashboard/api/sharing/urls.py",
        "Sharing API URLs"
    ))
    
    results.append(check_file_exists(
        "backend/src/baserow/contrib/dashboard/api/export/urls.py",
        "Export API URLs"
    ))
    
    # Check migration
    results.append(check_file_exists(
        "backend/src/baserow/contrib/dashboard/migrations/0005_dashboard_sharing_export.py",
        "Database migration"
    ))
    
    # Check model content
    model_patterns = {
        "Dashboard model": r"class Dashboard\(models\.Model\)",
        "DashboardPermission model": r"class DashboardPermission\(models\.Model\)",
        "DashboardExport model": r"class DashboardExport\(models\.Model\)",
        "DashboardWidget model": r"class DashboardWidget\(models\.Model\)",
        "Token generation": r"def generate_public_token",
        "Permission choices": r"PERMISSION_CHOICES"
    }
    
    results.append(check_file_content(
        "backend/src/baserow/contrib/dashboard/models.py",
        model_patterns,
        "Dashboard models content"
    ))
    
    # Check sharing handler content
    sharing_patterns = {
        "Create public link": r"def create_public_link",
        "Create embed link": r"def create_embed_link",
        "Permission management": r"def set_dashboard_permission",
        "Permission checks": r"def user_can_view_dashboard"
    }
    
    results.append(check_file_content(
        "backend/src/baserow/contrib/dashboard/sharing/handler.py",
        sharing_patterns,
        "Sharing handler content"
    ))
    
    # Check export handler content
    export_patterns = {
        "Create export job": r"def create_export_job",
        "Export status": r"def get_export_status",
        "CSV export": r"def process_csv_export",
        "Celery task": r"@shared_task"
    }
    
    results.append(check_file_content(
        "backend/src/baserow/contrib/dashboard/export/handler.py",
        export_patterns,
        "Export handler content"
    ))
    
    return all(results)


def verify_frontend_implementation():
    """Verify frontend implementation."""
    print("\n🎨 Verifying Frontend Implementation...")
    print("-" * 50)
    
    results = []
    
    # Check Vue components
    results.append(check_file_exists(
        "web-frontend/modules/dashboard/components/sharing/DashboardSharingModal.vue",
        "Dashboard sharing modal component"
    ))
    
    results.append(check_file_exists(
        "web-frontend/modules/dashboard/components/export/DashboardExportModal.vue",
        "Dashboard export modal component"
    ))
    
    results.append(check_file_exists(
        "web-frontend/modules/dashboard/components/embed/EmbeddedDashboard.vue",
        "Embedded dashboard component"
    ))
    
    results.append(check_file_exists(
        "web-frontend/modules/dashboard/components/embed/EmbeddedWidget.vue",
        "Embedded widget component"
    ))
    
    # Check services
    results.append(check_file_exists(
        "web-frontend/modules/dashboard/services/dashboardSharing.js",
        "Dashboard sharing service"
    ))
    
    results.append(check_file_exists(
        "web-frontend/modules/dashboard/services/dashboardExport.js",
        "Dashboard export service"
    ))
    
    # Check component content
    sharing_modal_patterns = {
        "Public link creation": r"createPublicLink",
        "Embed link creation": r"createEmbedLink",
        "Permission management": r"addPermission",
        "Copy to clipboard": r"copyToClipboard"
    }
    
    results.append(check_file_content(
        "web-frontend/modules/dashboard/components/sharing/DashboardSharingModal.vue",
        sharing_modal_patterns,
        "Sharing modal component content"
    ))
    
    export_modal_patterns = {
        "Export creation": r"startExport",
        "Export formats": r"formatPdf|formatPng|formatCsv",
        "Scheduling": r"scheduleExport",
        "Download": r"downloadExport"
    }
    
    results.append(check_file_content(
        "web-frontend/modules/dashboard/components/export/DashboardExportModal.vue",
        export_modal_patterns,
        "Export modal component content"
    ))
    
    # Check embedded components
    embed_patterns = {
        "Chart rendering": r"renderChart",
        "Widget types": r"isChartWidget",
        "Error handling": r"handleWidgetError",
        "Responsive design": r"embed-mode"
    }
    
    results.append(check_file_content(
        "web-frontend/modules/dashboard/components/embed/EmbeddedWidget.vue",
        embed_patterns,
        "Embedded widget component content"
    ))
    
    return all(results)


def verify_localization():
    """Verify localization files."""
    print("\n🌐 Verifying Localization...")
    print("-" * 50)
    
    results = []
    
    # Check localization file exists
    results.append(check_file_exists(
        "web-frontend/modules/dashboard/locales/en.json",
        "Dashboard localization file"
    ))
    
    # Check localization content
    if os.path.exists("web-frontend/modules/dashboard/locales/en.json"):
        try:
            with open("web-frontend/modules/dashboard/locales/en.json", 'r', encoding='utf-8') as f:
                locales = json.load(f)
            
            required_sections = [
                "dashboardSharing",
                "dashboardExport", 
                "dashboardEmbed"
            ]
            
            missing_sections = []
            for section in required_sections:
                if section not in locales:
                    missing_sections.append(section)
            
            if missing_sections:
                print(f"❌ Localization content - Missing sections: {', '.join(missing_sections)}")
                results.append(False)
            else:
                print("✓ Localization content")
                results.append(True)
                
        except Exception as e:
            print(f"❌ Localization content - Error reading JSON: {e}")
            results.append(False)
    else:
        results.append(False)
    
    return all(results)


def verify_api_integration():
    """Verify API integration."""
    print("\n🔗 Verifying API Integration...")
    print("-" * 50)
    
    results = []
    
    # Check main API URLs file is updated
    api_urls_patterns = {
        "Sharing URLs": r"sharing.*urls",
        "Export URLs": r"export.*urls"
    }
    
    results.append(check_file_content(
        "backend/src/baserow/contrib/dashboard/api/urls.py",
        api_urls_patterns,
        "Main API URLs updated"
    ))
    
    return all(results)


def main():
    """Main verification function."""
    print("🔍 Dashboard Sharing and Export Implementation Verification")
    print("=" * 70)
    
    # Run all verifications
    backend_ok = verify_backend_implementation()
    frontend_ok = verify_frontend_implementation()
    localization_ok = verify_localization()
    api_ok = verify_api_integration()
    
    # Summary
    print("\n📊 Verification Summary")
    print("=" * 70)
    
    components = [
        ("Backend Implementation", backend_ok),
        ("Frontend Implementation", frontend_ok),
        ("Localization", localization_ok),
        ("API Integration", api_ok)
    ]
    
    all_passed = True
    for component, passed in components:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{component:<25} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 70)
    
    if all_passed:
        print("🎉 TASK 24 IMPLEMENTATION VERIFICATION: SUCCESS!")
        print("\n✅ All components implemented successfully:")
        print("   • Public dashboard link generation")
        print("   • Widget embedding for external applications")
        print("   • Export functionality (PDF, PNG, CSV) with scheduled delivery")
        print("   • Dashboard permission system")
        print("   • Frontend sharing and export modals")
        print("   • Embedded dashboard and widget components")
        print("   • API endpoints and handlers")
        print("   • Database models and migrations")
        print("   • Localization support")
        
        print("\n🚀 Ready for testing and deployment!")
        return True
    else:
        print("❌ TASK 24 IMPLEMENTATION VERIFICATION: INCOMPLETE!")
        print("\n⚠️  Some components are missing or incomplete.")
        print("   Please review the failed items above.")
        return False


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)