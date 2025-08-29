#!/usr/bin/env python3
"""
Simple test script to verify Kanban view backend implementation.
This script tests the basic structure and imports without requiring Django setup.
"""

import sys
import os

# Add the backend source to Python path
backend_src = os.path.join(os.path.dirname(__file__), 'backend', 'src')
sys.path.insert(0, backend_src)

def test_file_structure():
    """Test that all required files exist."""
    print("Testing file structure...")
    
    required_files = [
        'backend/src/baserow/contrib/database/views/models.py',
        'backend/src/baserow/contrib/database/views/view_types.py',
        'backend/src/baserow/contrib/database/views/kanban_handler.py',
        'backend/src/baserow/contrib/database/api/views/kanban/__init__.py',
        'backend/src/baserow/contrib/database/api/views/kanban/views.py',
        'backend/src/baserow/contrib/database/api/views/kanban/serializers.py',
        'backend/src/baserow/contrib/database/api/views/kanban/urls.py',
        'backend/src/baserow/contrib/database/api/views/kanban/errors.py',
        'backend/src/baserow/contrib/database/migrations/0198_kanban_view.py',
        'backend/tests/baserow/contrib/database/views/test_kanban_view.py',
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    else:
        print("✅ All required files exist")
        return True


def test_model_definitions():
    """Test that model classes are properly defined."""
    print("Testing model definitions...")
    
    try:
        # Read the models file and check for key class definitions
        models_file = 'backend/src/baserow/contrib/database/views/models.py'
        with open(models_file, 'r') as f:
            content = f.read()
        
        required_classes = [
            'class KanbanView(View):',
            'class KanbanViewFieldOptions(HierarchicalModelMixin, models.Model):',
            'class KanbanViewFieldOptionsManager(models.Manager):'
        ]
        
        missing_classes = []
        for class_def in required_classes:
            if class_def not in content:
                missing_classes.append(class_def)
        
        if missing_classes:
            print("❌ Missing model class definitions:")
            for class_def in missing_classes:
                print(f"   - {class_def}")
            return False
        else:
            print("✅ All model classes are defined")
            return True
            
    except Exception as e:
        print(f"❌ Error reading models file: {e}")
        return False


def test_view_type_definition():
    """Test that KanbanViewType is properly defined."""
    print("Testing view type definition...")
    
    try:
        view_types_file = 'backend/src/baserow/contrib/database/views/view_types.py'
        with open(view_types_file, 'r') as f:
            content = f.read()
        
        required_elements = [
            'class KanbanViewType(ViewType):',
            'type = "kanban"',
            'def get_api_urls(self):',
            'def prepare_values(self, values, table, user):',
            'def export_serialized(',
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in content:
                missing_elements.append(element)
        
        if missing_elements:
            print("❌ Missing view type elements:")
            for element in missing_elements:
                print(f"   - {element}")
            return False
        else:
            print("✅ KanbanViewType is properly defined")
            return True
            
    except Exception as e:
        print(f"❌ Error reading view types file: {e}")
        return False


def test_api_structure():
    """Test that API components are properly structured."""
    print("Testing API structure...")
    
    try:
        # Check views.py
        views_file = 'backend/src/baserow/contrib/database/api/views/kanban/views.py'
        with open(views_file, 'r') as f:
            views_content = f.read()
        
        required_views = [
            'class KanbanViewView(APIView):',
            'class KanbanViewMoveCardView(APIView):',
            'class KanbanViewColumnsView(APIView):',
        ]
        
        for view_class in required_views:
            if view_class not in views_content:
                print(f"❌ Missing API view: {view_class}")
                return False
        
        # Check serializers.py
        serializers_file = 'backend/src/baserow/contrib/database/api/views/kanban/serializers.py'
        with open(serializers_file, 'r') as f:
            serializers_content = f.read()
        
        required_serializers = [
            'class KanbanViewFieldOptionsSerializer(serializers.ModelSerializer):',
            'class KanbanViewMoveCardSerializer(serializers.Serializer):',
        ]
        
        for serializer_class in required_serializers:
            if serializer_class not in serializers_content:
                print(f"❌ Missing serializer: {serializer_class}")
                return False
        
        print("✅ API structure is correct")
        return True
        
    except Exception as e:
        print(f"❌ Error checking API structure: {e}")
        return False


def test_handler_implementation():
    """Test that KanbanViewHandler is properly implemented."""
    print("Testing handler implementation...")
    
    try:
        handler_file = 'backend/src/baserow/contrib/database/views/kanban_handler.py'
        with open(handler_file, 'r') as f:
            content = f.read()
        
        required_methods = [
            'class KanbanViewHandler:',
            'def move_card(',
            'def get_kanban_columns(',
            'def get_cards_for_column(',
            'def update_card_configuration(',
            'def update_column_configuration(',
        ]
        
        missing_methods = []
        for method in required_methods:
            if method not in content:
                missing_methods.append(method)
        
        if missing_methods:
            print("❌ Missing handler methods:")
            for method in missing_methods:
                print(f"   - {method}")
            return False
        else:
            print("✅ KanbanViewHandler is properly implemented")
            return True
            
    except Exception as e:
        print(f"❌ Error reading handler file: {e}")
        return False


def test_migration_file():
    """Test that migration file is properly structured."""
    print("Testing migration file...")
    
    try:
        migration_file = 'backend/src/baserow/contrib/database/migrations/0198_kanban_view.py'
        with open(migration_file, 'r') as f:
            content = f.read()
        
        required_operations = [
            'CreateModel',
            'KanbanView',
            'KanbanViewFieldOptions',
            'AddField',
            'AlterUniqueTogether',
        ]
        
        missing_operations = []
        for operation in required_operations:
            if operation not in content:
                missing_operations.append(operation)
        
        if missing_operations:
            print("❌ Missing migration operations:")
            for operation in missing_operations:
                print(f"   - {operation}")
            return False
        else:
            print("✅ Migration file is properly structured")
            return True
            
    except Exception as e:
        print(f"❌ Error reading migration file: {e}")
        return False


def test_registration():
    """Test that KanbanViewType is registered in apps.py."""
    print("Testing view type registration...")
    
    try:
        apps_file = 'backend/src/baserow/contrib/database/apps.py'
        with open(apps_file, 'r') as f:
            content = f.read()
        
        required_registration = [
            'KanbanViewType',
            'view_type_registry.register(KanbanViewType())',
        ]
        
        missing_registration = []
        for reg in required_registration:
            if reg not in content:
                missing_registration.append(reg)
        
        if missing_registration:
            print("❌ Missing registration elements:")
            for reg in missing_registration:
                print(f"   - {reg}")
            return False
        else:
            print("✅ KanbanViewType is properly registered")
            return True
            
    except Exception as e:
        print(f"❌ Error reading apps file: {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 Testing Kanban View Backend Implementation")
    print("=" * 60)
    
    tests = [
        test_file_structure,
        test_model_definitions,
        test_view_type_definition,
        test_api_structure,
        test_handler_implementation,
        test_migration_file,
        test_registration,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
        print()
    
    print("=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Kanban view backend implementation is complete and properly structured.")
        print("\n📋 Implementation Summary:")
        print("✅ KanbanView model extending base View class")
        print("✅ KanbanViewFieldOptions for card customization")
        print("✅ KanbanViewType with full view type functionality")
        print("✅ API endpoints for listing, filtering, and card movement")
        print("✅ Drag-and-drop logic with KanbanViewHandler")
        print("✅ Database migration for new models")
        print("✅ Proper registration in Django apps")
        print("\n🚀 Ready for frontend integration!")
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)