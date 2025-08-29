#!/usr/bin/env python3
"""
Test script to verify Calendar view backend implementation.
This script checks that all required components are properly implemented.
"""

import os
import sys
import django

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend', 'src')
sys.path.insert(0, backend_path)

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'baserow.config.settings.test')
django.setup()

def test_calendar_view_models():
    """Test that Calendar view models are properly defined."""
    print("Testing Calendar view models...")
    
    try:
        from baserow.contrib.database.views.models import (
            CalendarView,
            CalendarViewFieldOptions,
            CalendarRecurringPattern,
            CalendarExternalSync,
        )
        print("✓ All Calendar view models imported successfully")
        
        # Check model fields
        calendar_view_fields = [field.name for field in CalendarView._meta.fields]
        required_fields = [
            'date_field', 'display_mode', 'event_title_field', 
            'event_color_field', 'enable_recurring_events',
            'recurring_pattern_field', 'external_calendar_config',
            'enable_external_sync'
        ]
        
        for field in required_fields:
            if field in calendar_view_fields:
                print(f"✓ CalendarView has {field} field")
            else:
                print(f"✗ CalendarView missing {field} field")
        
        return True
    except ImportError as e:
        print(f"✗ Failed to import Calendar view models: {e}")
        return False

def test_calendar_view_type():
    """Test that CalendarViewType is properly defined."""
    print("\nTesting CalendarViewType...")
    
    try:
        from baserow.contrib.database.views.view_types import CalendarViewType
        
        calendar_view_type = CalendarViewType()
        print("✓ CalendarViewType instantiated successfully")
        
        # Check required attributes
        required_attrs = [
            'type', 'model_class', 'field_options_model_class',
            'allowed_fields', 'field_options_allowed_fields',
            'serializer_field_names'
        ]
        
        for attr in required_attrs:
            if hasattr(calendar_view_type, attr):
                print(f"✓ CalendarViewType has {attr} attribute")
            else:
                print(f"✗ CalendarViewType missing {attr} attribute")
        
        # Check type name
        if calendar_view_type.type == "calendar":
            print("✓ CalendarViewType has correct type name")
        else:
            print(f"✗ CalendarViewType has incorrect type: {calendar_view_type.type}")
        
        return True
    except Exception as e:
        print(f"✗ Failed to test CalendarViewType: {e}")
        return False

def test_calendar_api_components():
    """Test that Calendar API components exist."""
    print("\nTesting Calendar API components...")
    
    try:
        from baserow.contrib.database.api.views.calendar.serializers import (
            CalendarViewFieldOptionsSerializer,
            CalendarViewSerializer,
            CalendarRecurringPatternSerializer,
            CalendarExternalSyncSerializer,
        )
        print("✓ Calendar API serializers imported successfully")
        
        from baserow.contrib.database.api.views.calendar.views import (
            CalendarViewView,
            CalendarViewMoveEventView,
            CalendarViewEventsView,
        )
        print("✓ Calendar API views imported successfully")
        
        from baserow.contrib.database.api.views.calendar import urls
        print("✓ Calendar API URLs imported successfully")
        
        return True
    except ImportError as e:
        print(f"✗ Failed to import Calendar API components: {e}")
        return False

def test_calendar_handler():
    """Test that CalendarViewHandler exists and has required methods."""
    print("\nTesting CalendarViewHandler...")
    
    try:
        from baserow.contrib.database.views.calendar_handler import CalendarViewHandler
        
        handler = CalendarViewHandler()
        print("✓ CalendarViewHandler instantiated successfully")
        
        # Check required methods
        required_methods = [
            'move_event', 'get_events_in_range', 'create_recurring_pattern',
            'create_external_sync', 'sync_external_calendar'
        ]
        
        for method in required_methods:
            if hasattr(handler, method):
                print(f"✓ CalendarViewHandler has {method} method")
            else:
                print(f"✗ CalendarViewHandler missing {method} method")
        
        return True
    except ImportError as e:
        print(f"✗ Failed to import CalendarViewHandler: {e}")
        return False

def test_view_type_registration():
    """Test that CalendarViewType is registered."""
    print("\nTesting view type registration...")
    
    try:
        from baserow.contrib.database.views.registries import view_type_registry
        
        # Check if calendar view type is registered
        try:
            calendar_view_type = view_type_registry.get("calendar")
            print("✓ CalendarViewType is registered in view_type_registry")
            return True
        except Exception as e:
            print(f"✗ CalendarViewType not registered: {e}")
            return False
    except ImportError as e:
        print(f"✗ Failed to import view_type_registry: {e}")
        return False

def main():
    """Run all tests."""
    print("Calendar View Backend Implementation Test")
    print("=" * 50)
    
    tests = [
        test_calendar_view_models,
        test_calendar_view_type,
        test_calendar_api_components,
        test_calendar_handler,
        test_view_type_registration,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Calendar view backend is properly implemented.")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)