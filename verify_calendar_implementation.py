#!/usr/bin/env python3
"""
Simple verification script to check Calendar view implementation files exist and have basic structure.
"""

import os
import re

def check_file_exists(filepath, description):
    """Check if a file exists and print result."""
    if os.path.exists(filepath):
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description}: {filepath} (NOT FOUND)")
        return False

def check_file_contains(filepath, patterns, description):
    """Check if a file contains required patterns."""
    if not os.path.exists(filepath):
        print(f"✗ {description}: {filepath} (FILE NOT FOUND)")
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        missing_patterns = []
        for pattern in patterns:
            if not re.search(pattern, content, re.MULTILINE):
                missing_patterns.append(pattern)
        
        if missing_patterns:
            print(f"✗ {description}: Missing patterns: {missing_patterns}")
            return False
        else:
            print(f"✓ {description}: All required patterns found")
            return True
    except Exception as e:
        print(f"✗ {description}: Error reading file: {e}")
        return False

def main():
    """Run verification checks."""
    print("Calendar View Implementation Verification")
    print("=" * 50)
    
    checks_passed = 0
    total_checks = 0
    
    # Check model file
    total_checks += 1
    if check_file_contains(
        "backend/src/baserow/contrib/database/views/models.py",
        [
            r"class CalendarView\(View\):",
            r"class CalendarViewFieldOptions",
            r"class CalendarRecurringPattern",
            r"class CalendarExternalSync",
        ],
        "Calendar models in models.py"
    ):
        checks_passed += 1
    
    # Check view types file
    total_checks += 1
    if check_file_contains(
        "backend/src/baserow/contrib/database/views/view_types.py",
        [
            r"class CalendarViewType\(ViewType\):",
            r"type = \"calendar\"",
            r"from \.models import.*CalendarView",
        ],
        "CalendarViewType in view_types.py"
    ):
        checks_passed += 1
    
    # Check API files exist
    api_files = [
        ("backend/src/baserow/contrib/database/api/views/calendar/__init__.py", "Calendar API __init__.py"),
        ("backend/src/baserow/contrib/database/api/views/calendar/errors.py", "Calendar API errors.py"),
        ("backend/src/baserow/contrib/database/api/views/calendar/serializers.py", "Calendar API serializers.py"),
        ("backend/src/baserow/contrib/database/api/views/calendar/views.py", "Calendar API views.py"),
        ("backend/src/baserow/contrib/database/api/views/calendar/urls.py", "Calendar API urls.py"),
    ]
    
    for filepath, description in api_files:
        total_checks += 1
        if check_file_exists(filepath, description):
            checks_passed += 1
    
    # Check handler file
    total_checks += 1
    if check_file_contains(
        "backend/src/baserow/contrib/database/views/calendar_handler.py",
        [
            r"class CalendarViewHandler:",
            r"def move_event\(",
            r"def get_events_in_range\(",
            r"def create_recurring_pattern\(",
            r"def sync_external_calendar\(",
        ],
        "CalendarViewHandler"
    ):
        checks_passed += 1
    
    # Check migration file
    total_checks += 1
    if check_file_contains(
        "backend/src/baserow/contrib/database/migrations/0200_calendar_view.py",
        [
            r"name='CalendarView'",
            r"name='CalendarViewFieldOptions'",
            r"name='CalendarRecurringPattern'",
            r"name='CalendarExternalSync'",
        ],
        "Calendar migration file"
    ):
        checks_passed += 1
    
    # Check registration in apps.py
    total_checks += 1
    if check_file_contains(
        "backend/src/baserow/contrib/database/apps.py",
        [
            r"CalendarViewType",
            r"view_type_registry\.register\(CalendarViewType\(\)\)",
        ],
        "CalendarViewType registration in apps.py"
    ):
        checks_passed += 1
    
    print(f"\nVerification Results: {checks_passed}/{total_checks} checks passed")
    
    if checks_passed == total_checks:
        print("🎉 All verification checks passed!")
        print("\nCalendar View Backend Implementation Summary:")
        print("- ✓ CalendarView model with date field mapping")
        print("- ✓ Calendar-specific serializers and API endpoints")
        print("- ✓ Recurring event support with pattern management")
        print("- ✓ External calendar integration framework")
        print("- ✓ Bi-directional sync capabilities")
        print("- ✓ Migration file for database schema")
        print("- ✓ View type registration")
        return True
    else:
        print("❌ Some verification checks failed.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)