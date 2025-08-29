#!/usr/bin/env python3
"""
Comprehensive test runner for the Baserow Monday.com expansion.
This script runs all test suites and generates comprehensive reports.
"""
import os
import sys
import subprocess
import time
import json
from pathlib import Path
from datetime import datetime
import argparse


class TestRunner:
    """Comprehensive test runner for all test suites."""
    
    def __init__(self):
        self.results = {
            'start_time': datetime.now().isoformat(),
            'test_suites': {},
            'summary': {
                'total_tests': 0,
                'passed': 0,
                'failed': 0,
                'skipped': 0,
                'errors': 0
            }
        }
        self.project_root = Path(__file__).parent
    
    def run_backend_unit_tests(self):
        """Run backend unit tests."""
        print("🧪 Running backend unit tests...")
        
        test_commands = [
            # Field type tests
            'python manage.py test backend.tests.baserow.contrib.database.fields.test_comprehensive_field_types --verbosity=2',
            
            # View type tests
            'python manage.py test backend.tests.baserow.contrib.database.views.test_comprehensive_view_types --verbosity=2',
            
            # Existing field tests
            'python manage.py test backend.tests.baserow.contrib.database.fields.test_progress_bar_field --verbosity=2',
            'python manage.py test backend.tests.baserow.contrib.database.fields.test_people_field --verbosity=2',
            
            # View tests
            'python manage.py test backend.tests.baserow.contrib.database.views.test_kanban_view --verbosity=2',
            'python manage.py test backend.tests.baserow.contrib.database.views.test_kanban_models --verbosity=2',
            
            # Collaboration tests
            'python manage.py test backend.tests.baserow.contrib.database.collaboration.test_enhanced_comment_system --verbosity=2',
            'python manage.py test backend.tests.baserow.contrib.database.collaboration.test_comment_api --verbosity=2',
            'python manage.py test backend.tests.baserow.contrib.database.collaboration.test_comment_mentions --verbosity=2',
            'python manage.py test backend.tests.baserow.contrib.database.collaboration.test_collaboration_handler --verbosity=2',
            'python manage.py test backend.tests.baserow.contrib.database.collaboration.test_collaboration_integration --verbosity=2',
            
            # Automation tests
            'python manage.py test backend.tests.baserow.contrib.automation.nodes.test_enhanced_triggers --verbosity=2',
            'python manage.py test backend.tests.baserow.contrib.automation.nodes.test_enhanced_actions --verbosity=2',
            
            # Dashboard tests
            'python manage.py test backend.tests.baserow.contrib.dashboard --verbosity=2',
            
            # Security and permissions tests
            'python manage.py test backend.tests.baserow.contrib.database.permissions.test_granular_permissions --verbosity=2',
            'python manage.py test backend.tests.baserow.contrib.security.test_security_system --verbosity=2',
        ]
        
        results = []
        for cmd in test_commands:
            try:
                result = subprocess.run(
                    cmd.split(),
                    cwd=self.project_root / 'backend',
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutes timeout
                )
                
                results.append({
                    'command': cmd,
                    'returncode': result.returncode,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'success': result.returncode == 0
                })
                
                if result.returncode == 0:
                    print(f"✅ {cmd.split()[-2]} - PASSED")
                else:
                    print(f"❌ {cmd.split()[-2]} - FAILED")
                    print(f"Error: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                print(f"⏰ {cmd} - TIMEOUT")
                results.append({
                    'command': cmd,
                    'returncode': -1,
                    'error': 'Timeout',
                    'success': False
                })
            except Exception as e:
                print(f"💥 {cmd} - ERROR: {e}")
                results.append({
                    'command': cmd,
                    'returncode': -1,
                    'error': str(e),
                    'success': False
                })
        
        self.results['test_suites']['backend_unit'] = results
        return results
    
    def run_backend_integration_tests(self):
        """Run backend integration tests."""
        print("🔗 Running backend integration tests...")
        
        test_commands = [
            'python manage.py test backend.tests.baserow.contrib.database.api.test_comprehensive_api_integration --verbosity=2',
        ]
        
        results = []
        for cmd in test_commands:
            try:
                result = subprocess.run(
                    cmd.split(),
                    cwd=self.project_root / 'backend',
                    capture_output=True,
                    text=True,
                    timeout=600  # 10 minutes timeout
                )
                
                results.append({
                    'command': cmd,
                    'returncode': result.returncode,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'success': result.returncode == 0
                })
                
                if result.returncode == 0:
                    print("✅ API Integration Tests - PASSED")
                else:
                    print("❌ API Integration Tests - FAILED")
                    print(f"Error: {result.stderr}")
                    
            except Exception as e:
                print(f"💥 Integration tests - ERROR: {e}")
                results.append({
                    'command': cmd,
                    'returncode': -1,
                    'error': str(e),
                    'success': False
                })
        
        self.results['test_suites']['backend_integration'] = results
        return results
    
    def run_performance_tests(self):
        """Run performance tests."""
        print("⚡ Running performance tests...")
        
        test_commands = [
            'python manage.py test backend.tests.baserow.performance.test_comprehensive_performance --verbosity=2',
        ]
        
        results = []
        for cmd in test_commands:
            try:
                result = subprocess.run(
                    cmd.split(),
                    cwd=self.project_root / 'backend',
                    capture_output=True,
                    text=True,
                    timeout=900  # 15 minutes timeout for performance tests
                )
                
                results.append({
                    'command': cmd,
                    'returncode': result.returncode,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'success': result.returncode == 0
                })
                
                if result.returncode == 0:
                    print("✅ Performance Tests - PASSED")
                else:
                    print("❌ Performance Tests - FAILED")
                    print(f"Error: {result.stderr}")
                    
            except Exception as e:
                print(f"💥 Performance tests - ERROR: {e}")
                results.append({
                    'command': cmd,
                    'returncode': -1,
                    'error': str(e),
                    'success': False
                })
        
        self.results['test_suites']['performance'] = results
        return results
    
    def run_frontend_unit_tests(self):
        """Run frontend unit tests."""
        print("🎨 Running frontend unit tests...")
        
        test_commands = [
            'npm test -- --testPathPattern=test_comprehensive_components.spec.js --verbose',
            'npm test -- --testPathPattern=test_kanban_frontend.js --verbose',
            'npm test -- --testPathPattern=test_calendar_frontend.js --verbose',
            'npm test -- --testPathPattern=test_progress_bar_frontend.js --verbose',
            'npm test -- --testPathPattern=test_people_field_frontend.js --verbose',
            'npm test -- --testPathPattern=test_comment_system_frontend.js --verbose',
            'npm test -- --testPathPattern=test_activity_log_frontend.js --verbose',
            'npm test -- --testPathPattern=test_visual_automation_builder.js --verbose',
            'npm test -- --testPathPattern=test_enhanced_dashboard_widgets.js --verbose',
            'npm test -- --testPathPattern=test_advanced_chart_types.js --verbose',
        ]
        
        results = []
        for cmd in test_commands:
            try:
                result = subprocess.run(
                    cmd.split(),
                    cwd=self.project_root / 'web-frontend',
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutes timeout
                )
                
                results.append({
                    'command': cmd,
                    'returncode': result.returncode,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'success': result.returncode == 0
                })
                
                test_name = cmd.split('--testPathPattern=')[1].split()[0] if '--testPathPattern=' in cmd else 'Frontend Tests'
                if result.returncode == 0:
                    print(f"✅ {test_name} - PASSED")
                else:
                    print(f"❌ {test_name} - FAILED")
                    print(f"Error: {result.stderr}")
                    
            except Exception as e:
                print(f"💥 Frontend tests - ERROR: {e}")
                results.append({
                    'command': cmd,
                    'returncode': -1,
                    'error': str(e),
                    'success': False
                })
        
        self.results['test_suites']['frontend_unit'] = results
        return results
    
    def run_e2e_tests(self):
        """Run end-to-end tests."""
        print("🌐 Running end-to-end tests...")
        
        test_commands = [
            'npx playwright test comprehensive-workflows.spec.ts --reporter=json',
        ]
        
        results = []
        for cmd in test_commands:
            try:
                result = subprocess.run(
                    cmd.split(),
                    cwd=self.project_root / 'e2e-tests',
                    capture_output=True,
                    text=True,
                    timeout=1800  # 30 minutes timeout for E2E tests
                )
                
                results.append({
                    'command': cmd,
                    'returncode': result.returncode,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'success': result.returncode == 0
                })
                
                if result.returncode == 0:
                    print("✅ E2E Tests - PASSED")
                else:
                    print("❌ E2E Tests - FAILED")
                    print(f"Error: {result.stderr}")
                    
            except Exception as e:
                print(f"💥 E2E tests - ERROR: {e}")
                results.append({
                    'command': cmd,
                    'returncode': -1,
                    'error': str(e),
                    'success': False
                })
        
        self.results['test_suites']['e2e'] = results
        return results
    
    def run_verification_tests(self):
        """Run verification tests for implemented features."""
        print("✅ Running verification tests...")
        
        verification_scripts = [
            'python verify_kanban_implementation.py',
            'python verify_calendar_implementation.py',
            'python verify_people_field_backend.py',
            'python verify_people_field_frontend.py',
            'python verify_progress_bar_frontend.py',
            'python verify_activity_logging_implementation.py',
            'python verify_enhanced_form_implementation.py',
            'python verify_enhanced_action_implementation.py',
            'python verify_dashboard_sharing_export.py',
            'python verify_granular_permissions.py',
            'python verify_security_implementation.py',
            'python verify_enhanced_api_implementation.py',
            'python verify_mobile_optimization.py',
        ]
        
        results = []
        for script in verification_scripts:
            try:
                result = subprocess.run(
                    script.split(),
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=120  # 2 minutes timeout
                )
                
                results.append({
                    'script': script,
                    'returncode': result.returncode,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'success': result.returncode == 0
                })
                
                script_name = script.replace('verify_', '').replace('.py', '').replace('_', ' ').title()
                if result.returncode == 0:
                    print(f"✅ {script_name} - VERIFIED")
                else:
                    print(f"❌ {script_name} - FAILED")
                    print(f"Error: {result.stderr}")
                    
            except Exception as e:
                print(f"💥 {script} - ERROR: {e}")
                results.append({
                    'script': script,
                    'returncode': -1,
                    'error': str(e),
                    'success': False
                })
        
        self.results['test_suites']['verification'] = results
        return results
    
    def run_specific_feature_tests(self):
        """Run tests for specific implemented features."""
        print("🎯 Running specific feature tests...")
        
        feature_tests = [
            'python test_kanban_simple.py',
            'python test_calendar_backend.py',
            'python test_timeline_backend.py',
            'python test_progress_bar_frontend.py',
            'python test_people_field_frontend.py',
            'python test_comment_system_frontend.py',
            'python test_activity_logging_system.py',
            'python test_notification_system.py',
            'python test_notification_system_integration.py',
            'python test_visual_automation_builder.js',
            'python test_enhanced_dashboard_widgets.py',
            'python test_dashboard_sharing_export.py',
            'python test_native_integrations.py',
            'python test_enhanced_api_capabilities.py',
            'python test_mobile_features.py',
        ]
        
        results = []
        for test in feature_tests:
            try:
                if test.endswith('.js'):
                    # Run JavaScript tests with Node
                    result = subprocess.run(
                        ['node', test],
                        cwd=self.project_root,
                        capture_output=True,
                        text=True,
                        timeout=180
                    )
                else:
                    # Run Python tests
                    result = subprocess.run(
                        test.split(),
                        cwd=self.project_root,
                        capture_output=True,
                        text=True,
                        timeout=180
                    )
                
                results.append({
                    'test': test,
                    'returncode': result.returncode,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'success': result.returncode == 0
                })
                
                test_name = test.replace('test_', '').replace('.py', '').replace('.js', '').replace('_', ' ').title()
                if result.returncode == 0:
                    print(f"✅ {test_name} - PASSED")
                else:
                    print(f"❌ {test_name} - FAILED")
                    if result.stderr:
                        print(f"Error: {result.stderr}")
                    
            except Exception as e:
                print(f"💥 {test} - ERROR: {e}")
                results.append({
                    'test': test,
                    'returncode': -1,
                    'error': str(e),
                    'success': False
                })
        
        self.results['test_suites']['feature_tests'] = results
        return results
    
    def generate_summary(self):
        """Generate test summary."""
        print("\n" + "="*80)
        print("📊 TEST SUMMARY")
        print("="*80)
        
        total_suites = len(self.results['test_suites'])
        passed_suites = 0
        failed_suites = 0
        
        for suite_name, suite_results in self.results['test_suites'].items():
            suite_passed = all(result.get('success', False) for result in suite_results)
            if suite_passed:
                passed_suites += 1
                print(f"✅ {suite_name.replace('_', ' ').title()}: PASSED")
            else:
                failed_suites += 1
                print(f"❌ {suite_name.replace('_', ' ').title()}: FAILED")
        
        print(f"\nTotal Test Suites: {total_suites}")
        print(f"Passed: {passed_suites}")
        print(f"Failed: {failed_suites}")
        
        # Calculate overall success rate
        success_rate = (passed_suites / total_suites * 100) if total_suites > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        self.results['end_time'] = datetime.now().isoformat()
        self.results['summary'].update({
            'total_suites': total_suites,
            'passed_suites': passed_suites,
            'failed_suites': failed_suites,
            'success_rate': success_rate
        })
        
        return success_rate >= 80  # Consider successful if 80% or more tests pass
    
    def save_results(self, filename='test_results.json'):
        """Save test results to JSON file."""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n📄 Test results saved to {filename}")
    
    def run_all_tests(self, skip_e2e=False, skip_performance=False):
        """Run all test suites."""
        print("🚀 Starting comprehensive test suite...")
        print(f"Start time: {self.results['start_time']}")
        print("="*80)
        
        try:
            # Run backend tests
            self.run_backend_unit_tests()
            self.run_backend_integration_tests()
            
            # Run performance tests (optional)
            if not skip_performance:
                self.run_performance_tests()
            
            # Run frontend tests
            self.run_frontend_unit_tests()
            
            # Run E2E tests (optional, can be slow)
            if not skip_e2e:
                self.run_e2e_tests()
            
            # Run verification tests
            self.run_verification_tests()
            
            # Run specific feature tests
            self.run_specific_feature_tests()
            
            # Generate summary
            success = self.generate_summary()
            
            # Save results
            self.save_results()
            
            return success
            
        except KeyboardInterrupt:
            print("\n⚠️  Test run interrupted by user")
            self.save_results('test_results_interrupted.json')
            return False
        except Exception as e:
            print(f"\n💥 Unexpected error during test run: {e}")
            self.save_results('test_results_error.json')
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Run comprehensive test suite for Baserow Monday.com expansion')
    parser.add_argument('--skip-e2e', action='store_true', help='Skip end-to-end tests')
    parser.add_argument('--skip-performance', action='store_true', help='Skip performance tests')
    parser.add_argument('--backend-only', action='store_true', help='Run only backend tests')
    parser.add_argument('--frontend-only', action='store_true', help='Run only frontend tests')
    parser.add_argument('--verification-only', action='store_true', help='Run only verification tests')
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    if args.backend_only:
        runner.run_backend_unit_tests()
        runner.run_backend_integration_tests()
        if not args.skip_performance:
            runner.run_performance_tests()
    elif args.frontend_only:
        runner.run_frontend_unit_tests()
        if not args.skip_e2e:
            runner.run_e2e_tests()
    elif args.verification_only:
        runner.run_verification_tests()
    else:
        success = runner.run_all_tests(
            skip_e2e=args.skip_e2e,
            skip_performance=args.skip_performance
        )
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()