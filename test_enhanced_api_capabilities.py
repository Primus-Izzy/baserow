#!/usr/bin/env python3
"""
Comprehensive test for enhanced API capabilities (Task 28).

This test verifies:
1. Batch record operations with transaction support
2. Enhanced webhook system with reliable delivery
3. Expanded API endpoints for views, users, roles, and new features
4. Zapier and Make.com integration support
"""

import json
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any


class EnhancedAPITester:
    """Test suite for enhanced API capabilities."""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_token: str = None):
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.session = requests.Session()
        
        if api_token:
            self.session.headers.update({
                'Authorization': f'Token {api_token}',
                'Content-Type': 'application/json'
            })
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all enhanced API capability tests."""
        results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'summary': {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'errors': []
            }
        }
        
        test_methods = [
            ('batch_operations', self.test_batch_operations),
            ('webhook_system', self.test_webhook_system),
            ('enhanced_endpoints', self.test_enhanced_endpoints),
            ('zapier_integration', self.test_zapier_integration),
            ('make_integration', self.test_make_integration),
            ('api_statistics', self.test_api_statistics),
            ('api_key_management', self.test_api_key_management)
        ]
        
        for test_name, test_method in test_methods:
            print(f"Running {test_name} test...")
            try:
                test_result = test_method()
                results['tests'][test_name] = test_result
                results['summary']['total'] += 1
                
                if test_result.get('success', False):
                    results['summary']['passed'] += 1
                    print(f"✅ {test_name} test passed")
                else:
                    results['summary']['failed'] += 1
                    print(f"❌ {test_name} test failed: {test_result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                results['tests'][test_name] = {
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                results['summary']['total'] += 1
                results['summary']['failed'] += 1
                results['summary']['errors'].append(f"{test_name}: {str(e)}")
                print(f"💥 {test_name} test crashed: {str(e)}")
        
        return results
    
    def test_batch_operations(self) -> Dict[str, Any]:
        """Test batch record operations with transaction support."""
        try:
            # Test data for batch operations
            batch_data = {
                'table_id': 1,  # Assuming table ID 1 exists
                'atomic': True,
                'operations': [
                    {
                        'operation': 'create',
                        'data': {
                            'field_1': 'Batch Test Row 1',
                            'field_2': 100
                        }
                    },
                    {
                        'operation': 'create',
                        'data': {
                            'field_1': 'Batch Test Row 2',
                            'field_2': 200
                        }
                    }
                ]
            }
            
            # Test batch create operations
            response = self.session.post(
                f"{self.base_url}/api/database/batch/records/",
                json=batch_data
            )
            
            if response.status_code not in [200, 207]:
                return {
                    'success': False,
                    'error': f"Batch operations failed with status {response.status_code}: {response.text}",
                    'timestamp': datetime.now().isoformat()
                }
            
            result = response.json()
            
            # Verify response structure
            required_fields = ['success', 'total_operations', 'successful_operations', 'results']
            for field in required_fields:
                if field not in result:
                    return {
                        'success': False,
                        'error': f"Missing field in batch response: {field}",
                        'timestamp': datetime.now().isoformat()
                    }
            
            # Test non-atomic operations
            batch_data['atomic'] = False
            response = self.session.post(
                f"{self.base_url}/api/database/batch/records/",
                json=batch_data
            )
            
            return {
                'success': True,
                'message': 'Batch operations test completed successfully',
                'atomic_result': result,
                'non_atomic_status': response.status_code,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Batch operations test error: {str(e)}",
                'timestamp': datetime.now().isoformat()
            }
    
    def test_webhook_system(self) -> Dict[str, Any]:
        """Test enhanced webhook system."""
        try:
            # Test webhook creation
            webhook_data = {
                'name': 'Test Enhanced Webhook',
                'group_id': 1,  # Assuming group ID 1 exists
                'table_id': 1,  # Assuming table ID 1 exists
                'url': 'https://httpbin.org/post',
                'events': ['row.created', 'row.updated'],
                'headers': {'X-Test-Header': 'test-value'},
                'is_active': True
            }
            
            response = self.session.post(
                f"{self.base_url}/api/database/webhooks/webhooks/",
                json=webhook_data
            )
            
            if response.status_code != 201:
                return {
                    'success': False,
                    'error': f"Webhook creation failed with status {response.status_code}: {response.text}",
                    'timestamp': datetime.now().isoformat()
                }
            
            webhook = response.json()
            webhook_id = webhook['id']
            
            # Test webhook testing endpoint
            test_response = self.session.post(
                f"{self.base_url}/api/database/webhooks/webhooks/{webhook_id}/test/",
                json={'test_payload': {'message': 'Test webhook delivery'}}
            )
            
            # Test webhook statistics
            stats_response = self.session.get(
                f"{self.base_url}/api/database/webhooks/groups/1/webhook-stats/"
            )
            
            # Test webhook deliveries
            deliveries_response = self.session.get(
                f"{self.base_url}/api/database/webhooks/webhooks/{webhook_id}/deliveries/"
            )
            
            return {
                'success': True,
                'message': 'Webhook system test completed successfully',
                'webhook_created': webhook_id,
                'test_status': test_response.status_code,
                'stats_status': stats_response.status_code,
                'deliveries_status': deliveries_response.status_code,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Webhook system test error: {str(e)}",
                'timestamp': datetime.now().isoformat()
            }
    
    def test_enhanced_endpoints(self) -> Dict[str, Any]:
        """Test enhanced API endpoints for views, users, roles."""
        try:
            endpoints_to_test = [
                '/api/database/enhanced/users/',
                '/api/database/enhanced/groups/',
                '/api/database/enhanced/databases/',
                '/api/database/enhanced/tables/',
                '/api/database/enhanced/views/',
                '/api/database/enhanced/stats/'
            ]
            
            results = {}
            
            for endpoint in endpoints_to_test:
                response = self.session.get(f"{self.base_url}{endpoint}")
                results[endpoint] = {
                    'status_code': response.status_code,
                    'success': response.status_code == 200,
                    'has_data': len(response.json()) > 0 if response.status_code == 200 else False
                }
            
            # Test user details endpoint
            me_response = self.session.get(f"{self.base_url}/api/database/enhanced/users/me/")
            results['/api/database/enhanced/users/me/'] = {
                'status_code': me_response.status_code,
                'success': me_response.status_code == 200
            }
            
            # Test filtering on views endpoint
            filtered_response = self.session.get(
                f"{self.base_url}/api/database/enhanced/views/?type=grid&search=test"
            )
            results['filtered_views'] = {
                'status_code': filtered_response.status_code,
                'success': filtered_response.status_code == 200
            }
            
            all_successful = all(result['success'] for result in results.values())
            
            return {
                'success': all_successful,
                'message': 'Enhanced endpoints test completed',
                'endpoint_results': results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Enhanced endpoints test error: {str(e)}",
                'timestamp': datetime.now().isoformat()
            }
    
    def test_zapier_integration(self) -> Dict[str, Any]:
        """Test Zapier integration support."""
        try:
            # Test Zapier trigger integration creation
            trigger_data = {
                'name': 'Test Zapier Trigger',
                'group_id': 1,
                'table_id': 1,
                'integration_type': 'trigger',
                'trigger_type': 'new_row',
                'configuration': {
                    'fields': ['field_1', 'field_2'],
                    'filters': {}
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/database/integrations/zapier/",
                json=trigger_data
            )
            
            if response.status_code != 201:
                return {
                    'success': False,
                    'error': f"Zapier integration creation failed: {response.status_code} - {response.text}",
                    'timestamp': datetime.now().isoformat()
                }
            
            integration = response.json()
            integration_id = integration['id']
            
            # Test trigger testing
            test_response = self.session.post(
                f"{self.base_url}/api/database/integrations/zapier/{integration_id}/test_trigger/",
                json={'sample_data': {'row': {'id': 1, 'field_1': 'test'}}}
            )
            
            # Test Zapier action integration
            action_data = {
                'name': 'Test Zapier Action',
                'group_id': 1,
                'table_id': 1,
                'integration_type': 'action',
                'action_type': 'create_row',
                'configuration': {
                    'field_mapping': {
                        'field_1': 'input_field_1',
                        'field_2': 'input_field_2'
                    }
                }
            }
            
            action_response = self.session.post(
                f"{self.base_url}/api/database/integrations/zapier/",
                json=action_data
            )
            
            return {
                'success': True,
                'message': 'Zapier integration test completed successfully',
                'trigger_integration_id': integration_id,
                'test_trigger_status': test_response.status_code,
                'action_integration_status': action_response.status_code,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Zapier integration test error: {str(e)}",
                'timestamp': datetime.now().isoformat()
            }
    
    def test_make_integration(self) -> Dict[str, Any]:
        """Test Make.com integration support."""
        try:
            # Test Make.com trigger integration creation
            trigger_data = {
                'name': 'Test Make Trigger',
                'group_id': 1,
                'table_id': 1,
                'module_type': 'trigger',
                'webhook_type': 'instant',
                'webhook_url': 'https://hook.integromat.com/test',
                'configuration': {
                    'events': ['row.created', 'row.updated'],
                    'fields': ['field_1', 'field_2']
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/database/integrations/make/",
                json=trigger_data
            )
            
            if response.status_code != 201:
                return {
                    'success': False,
                    'error': f"Make.com integration creation failed: {response.status_code} - {response.text}",
                    'timestamp': datetime.now().isoformat()
                }
            
            integration = response.json()
            integration_id = integration['id']
            
            # Test webhook testing
            test_response = self.session.post(
                f"{self.base_url}/api/database/integrations/make/{integration_id}/test_webhook/",
                json={'sample_data': {'row': {'id': 1, 'field_1': 'test'}}}
            )
            
            # Test Make.com action integration
            action_data = {
                'name': 'Test Make Action',
                'group_id': 1,
                'table_id': 1,
                'module_type': 'action',
                'configuration': {
                    'action_type': 'create_row',
                    'field_mapping': {
                        'field_1': 'input_field_1',
                        'field_2': 'input_field_2'
                    }
                }
            }
            
            action_response = self.session.post(
                f"{self.base_url}/api/database/integrations/make/",
                json=action_data
            )
            
            return {
                'success': True,
                'message': 'Make.com integration test completed successfully',
                'trigger_integration_id': integration_id,
                'test_webhook_status': test_response.status_code,
                'action_integration_status': action_response.status_code,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Make.com integration test error: {str(e)}",
                'timestamp': datetime.now().isoformat()
            }
    
    def test_api_statistics(self) -> Dict[str, Any]:
        """Test API statistics endpoints."""
        try:
            # Test general API stats
            stats_response = self.session.get(f"{self.base_url}/api/database/enhanced/stats/")
            
            if stats_response.status_code != 200:
                return {
                    'success': False,
                    'error': f"API stats failed: {stats_response.status_code} - {stats_response.text}",
                    'timestamp': datetime.now().isoformat()
                }
            
            stats = stats_response.json()
            
            # Verify stats structure
            required_sections = ['user', 'resources', 'api_info']
            for section in required_sections:
                if section not in stats:
                    return {
                        'success': False,
                        'error': f"Missing section in API stats: {section}",
                        'timestamp': datetime.now().isoformat()
                    }
            
            # Test integration stats
            integration_stats_response = self.session.get(
                f"{self.base_url}/api/database/integrations/groups/1/stats/"
            )
            
            return {
                'success': True,
                'message': 'API statistics test completed successfully',
                'api_stats_status': stats_response.status_code,
                'integration_stats_status': integration_stats_response.status_code,
                'user_resources': stats['resources'],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"API statistics test error: {str(e)}",
                'timestamp': datetime.now().isoformat()
            }
    
    def test_api_key_management(self) -> Dict[str, Any]:
        """Test API key management endpoints."""
        try:
            # Test API key creation
            key_data = {
                'name': 'Test API Key',
                'permissions': ['database.read', 'table.read', 'row.read'],
                'expires_at': (datetime.now() + timedelta(days=30)).isoformat()
            }
            
            create_response = self.session.post(
                f"{self.base_url}/api/database/enhanced/api-keys/",
                json=key_data
            )
            
            if create_response.status_code != 201:
                return {
                    'success': False,
                    'error': f"API key creation failed: {create_response.status_code} - {create_response.text}",
                    'timestamp': datetime.now().isoformat()
                }
            
            # Test API key listing
            list_response = self.session.get(f"{self.base_url}/api/database/enhanced/api-keys/")
            
            return {
                'success': True,
                'message': 'API key management test completed successfully',
                'create_status': create_response.status_code,
                'list_status': list_response.status_code,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"API key management test error: {str(e)}",
                'timestamp': datetime.now().isoformat()
            }


def main():
    """Main test execution function."""
    print("🚀 Starting Enhanced API Capabilities Test Suite (Task 28)")
    print("=" * 60)
    
    # Initialize tester
    tester = EnhancedAPITester()
    
    # Run all tests
    results = tester.run_all_tests()
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {results['summary']['total']}")
    print(f"Passed: {results['summary']['passed']}")
    print(f"Failed: {results['summary']['failed']}")
    print(f"Success Rate: {(results['summary']['passed'] / results['summary']['total'] * 100):.1f}%")
    
    if results['summary']['errors']:
        print("\n❌ ERRORS:")
        for error in results['summary']['errors']:
            print(f"  - {error}")
    
    # Save detailed results
    with open('enhanced_api_test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: enhanced_api_test_results.json")
    
    # Return appropriate exit code
    return 0 if results['summary']['failed'] == 0 else 1


if __name__ == "__main__":
    exit(main())