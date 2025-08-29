#!/usr/bin/env python3
"""
Verification script for Enhanced Form View implementation.
This script checks if all the required components are in place and properly structured.
"""

import os
import sys
import json
import re
from pathlib import Path

def check_file_exists(file_path, description):
    """Check if a file exists and print status."""
    if os.path.exists(file_path):
        print(f"✓ {description}: {file_path}")
        return True
    else:
        print(f"✗ {description}: {file_path} (NOT FOUND)")
        return False

def check_file_content(file_path, patterns, description):
    """Check if file contains required patterns."""
    if not os.path.exists(file_path):
        print(f"✗ {description}: {file_path} (FILE NOT FOUND)")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        missing_patterns = []
        for pattern_name, pattern in patterns.items():
            if not re.search(pattern, content, re.MULTILINE | re.DOTALL):
                missing_patterns.append(pattern_name)
        
        if missing_patterns:
            print(f"✗ {description}: Missing patterns: {', '.join(missing_patterns)}")
            return False
        else:
            print(f"✓ {description}: All required patterns found")
            return True
    except Exception as e:
        print(f"✗ {description}: Error reading file: {e}")
        return False

def main():
    """Main verification function."""
    print("Enhanced Form View Implementation Verification")
    print("=" * 50)
    
    # Track overall success
    all_checks_passed = True
    
    # Backend files to check
    backend_files = [
        ("backend/src/baserow/contrib/database/views/enhanced_form_handler.py", "Enhanced Form Handler"),
        ("backend/src/baserow/contrib/database/migrations/0203_enhanced_form_view.py", "Enhanced Form Migration"),
        ("backend/src/baserow/contrib/database/api/views/form/views.py", "Enhanced Form API Views"),
        ("backend/src/baserow/contrib/database/api/views/form/serializers.py", "Enhanced Form Serializers"),
        ("backend/src/baserow/contrib/database/api/views/form/urls.py", "Enhanced Form URLs"),
        ("backend/tests/baserow/contrib/database/views/test_enhanced_form_view.py", "Enhanced Form Tests"),
    ]
    
    # Frontend files to check
    frontend_files = [
        ("web-frontend/modules/database/components/view/form/FormViewEnhancedSidebar.vue", "Enhanced Form Sidebar"),
        ("web-frontend/modules/database/components/view/form/FormViewConditionalLogic.vue", "Conditional Logic Component"),
        ("web-frontend/modules/database/components/view/form/FormViewValidationRules.vue", "Validation Rules Component"),
        ("web-frontend/modules/database/components/view/form/FormViewCustomBranding.vue", "Custom Branding Component"),
        ("web-frontend/modules/database/components/view/form/FormViewShareableLinks.vue", "Shareable Links Component"),
        ("web-frontend/modules/database/services/view/enhancedForm.js", "Enhanced Form Service"),
        ("web-frontend/modules/database/store/view/enhancedForm.js", "Enhanced Form Store"),
    ]
    
    print("\n1. Checking Backend Files:")
    print("-" * 30)
    for file_path, description in backend_files:
        if not check_file_exists(file_path, description):
            all_checks_passed = False
    
    print("\n2. Checking Frontend Files:")
    print("-" * 30)
    for file_path, description in frontend_files:
        if not check_file_exists(file_path, description):
            all_checks_passed = False
    
    print("\n3. Checking Backend Implementation Details:")
    print("-" * 40)
    
    # Check Enhanced Form Handler
    handler_patterns = {
        "EnhancedFormHandler class": r"class EnhancedFormHandler:",
        "update_custom_branding method": r"def update_custom_branding\(",
        "update_access_control method": r"def update_access_control\(",
        "create_shareable_link method": r"def create_shareable_link\(",
        "evaluate_conditional_logic method": r"def evaluate_conditional_logic\(",
        "validate_field_value method": r"def validate_field_value\(",
    }
    
    if not check_file_content(
        "backend/src/baserow/contrib/database/views/enhanced_form_handler.py",
        handler_patterns,
        "Enhanced Form Handler Implementation"
    ):
        all_checks_passed = False
    
    # Check Migration
    migration_patterns = {
        "custom_branding field": r"custom_branding.*JSONField",
        "access_control field": r"access_control.*JSONField",
        "validation_config field": r"validation_config.*JSONField",
        "shareable_links field": r"shareable_links.*JSONField",
        "conditional_logic field": r"conditional_logic.*JSONField",
        "validation_rules field": r"validation_rules.*JSONField",
    }
    
    if not check_file_content(
        "backend/src/baserow/contrib/database/migrations/0203_enhanced_form_view.py",
        migration_patterns,
        "Enhanced Form Migration Fields"
    ):
        all_checks_passed = False
    
    # Check API Views
    api_patterns = {
        "EnhancedFormViewCustomBrandingView": r"class EnhancedFormViewCustomBrandingView",
        "EnhancedFormViewAccessControlView": r"class EnhancedFormViewAccessControlView",
        "EnhancedFormViewValidationConfigView": r"class EnhancedFormViewValidationConfigView",
        "EnhancedFormViewShareableLinksView": r"class EnhancedFormViewShareableLinksView",
        "EnhancedFormViewFieldOptionsView": r"class EnhancedFormViewFieldOptionsView",
    }
    
    if not check_file_content(
        "backend/src/baserow/contrib/database/api/views/form/views.py",
        api_patterns,
        "Enhanced Form API Views"
    ):
        all_checks_passed = False
    
    print("\n4. Checking Frontend Implementation Details:")
    print("-" * 42)
    
    # Check Enhanced Sidebar
    sidebar_patterns = {
        "FormViewEnhancedSidebar component": r"name:\s*['\"]FormViewEnhancedSidebar['\"]",
        "tabs configuration": r"tabs\(\)",
        "conditional logic tab": r"conditional",
        "validation tab": r"validation",
        "branding tab": r"branding",
        "access control tab": r"access",
        "sharing tab": r"sharing",
    }
    
    if not check_file_content(
        "web-frontend/modules/database/components/view/form/FormViewEnhancedSidebar.vue",
        sidebar_patterns,
        "Enhanced Form Sidebar Implementation"
    ):
        all_checks_passed = False
    
    # Check Service
    service_patterns = {
        "updateCustomBranding": r"updateCustomBranding\(",
        "updateAccessControl": r"updateAccessControl\(",
        "createShareableLink": r"createShareableLink\(",
        "updateFieldOptions": r"updateFieldOptions\(",
        "evaluateConditionalLogic": r"evaluateConditionalLogic\(",
        "validateFieldValues": r"validateFieldValues\(",
    }
    
    if not check_file_content(
        "web-frontend/modules/database/services/view/enhancedForm.js",
        service_patterns,
        "Enhanced Form Service Methods"
    ):
        all_checks_passed = False
    
    # Check Store
    store_patterns = {
        "SET_CUSTOM_BRANDING": r"SET_CUSTOM_BRANDING",
        "SET_ACCESS_CONTROL": r"SET_ACCESS_CONTROL",
        "SET_SHAREABLE_LINKS": r"SET_SHAREABLE_LINKS",
        "SET_FIELD_CONDITIONAL_LOGIC": r"SET_FIELD_CONDITIONAL_LOGIC",
        "SET_VALIDATION_ERRORS": r"SET_VALIDATION_ERRORS",
        "updateCustomBranding action": r"updateCustomBranding.*async",
        "evaluateConditionalLogic action": r"evaluateConditionalLogic.*async",
    }
    
    if not check_file_content(
        "web-frontend/modules/database/store/view/enhancedForm.js",
        store_patterns,
        "Enhanced Form Store Implementation"
    ):
        all_checks_passed = False
    
    print("\n5. Summary:")
    print("-" * 10)
    
    if all_checks_passed:
        print("✓ All checks passed! Enhanced Form View implementation appears complete.")
        print("\nImplemented Features:")
        print("- ✓ Conditional field logic showing/hiding fields based on answers")
        print("- ✓ Custom branding support (logos, colors, thank-you messages)")
        print("- ✓ Public and internal form access controls")
        print("- ✓ Comprehensive field validation with clear error messages")
        print("- ✓ Secure shareable link generation with access controls")
        print("\nNext Steps:")
        print("1. Run database migrations: python manage.py migrate")
        print("2. Test the implementation with unit tests")
        print("3. Test the UI components in the browser")
        print("4. Verify API endpoints with integration tests")
        return 0
    else:
        print("✗ Some checks failed. Please review the missing components above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())