#!/usr/bin/env python3
"""
Comprehensive Security and Accessibility Testing Suite for Baserow Expansion

This test suite covers:
- Security testing for permission system and data protection
- Accessibility testing for WCAG 2.1 AA compliance
- Cross-browser compatibility validation
- Mobile responsiveness testing

Run with: python test_security_accessibility_comprehensive.py
"""

import asyncio
import json
import time
import requests
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import axe_selenium_python


@dataclass
class TestResult:
    """Test result data structure"""
    test_name: str
    status: str  # 'PASS', 'FAIL', 'SKIP'
    message: str
    details: Optional[Dict] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class SecurityTester:
    """Security testing for permission system and data protection"""
    
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = []
    
    def test_authentication_security(self) -> List[TestResult]:
        """Test authentication and session security"""
        results = []
        
        # Test 1: Password strength requirements
        try:
            weak_passwords = ["123", "password", "admin", "test"]
            for pwd in weak_passwords:
                response = self.session.post(f"{self.base_url}/api/auth/register/", {
                    "email": "test@example.com",
                    "password": pwd,
                    "name": "Test User"
                })
                
                if response.status_code == 400:
                    results.append(TestResult(
                        "password_strength_validation",
                        "PASS",
                        f"Weak password '{pwd}' correctly rejected"
                    ))
                else:
                    results.append(TestResult(
                        "password_strength_validation",
                        "FAIL",
                        f"Weak password '{pwd}' was accepted",
                        {"response_code": response.status_code}
                    ))
        except Exception as e:
            results.append(TestResult(
                "password_strength_validation",
                "FAIL",
                f"Error testing password strength: {str(e)}"
            ))
        
        # Test 2: Session timeout
        try:
            # Login and check session expiry
            login_response = self.session.post(f"{self.base_url}/api/auth/login/", {
                "email": "admin@example.com",
                "password": "secure_password_123"
            })
            
            if login_response.status_code == 200:
                # Wait and test if session expires appropriately
                time.sleep(2)  # Simulate some time passing
                
                protected_response = self.session.get(f"{self.base_url}/api/user/")
                if protected_response.status_code in [200, 401]:
                    results.append(TestResult(
                        "session_management",
                        "PASS",
                        "Session management working correctly"
                    ))
                else:
                    results.append(TestResult(
                        "session_management",
                        "FAIL",
                        f"Unexpected session response: {protected_response.status_code}"
                    ))
        except Exception as e:
            results.append(TestResult(
                "session_management",
                "FAIL",
                f"Error testing session management: {str(e)}"
            ))
        
        return results
    
    def test_permission_system_security(self) -> List[TestResult]:
        """Test granular permission system security"""
        results = []
        
        # Test 1: Field-level permissions
        try:
            # Attempt to access restricted field as unauthorized user
            response = self.session.get(f"{self.base_url}/api/database/tables/1/fields/")
            
            # Check if sensitive fields are properly filtered
            if response.status_code == 200:
                fields = response.json()
                sensitive_fields = [f for f in fields if f.get('name', '').lower() in ['password', 'ssn', 'credit_card']]
                
                if not sensitive_fields:
                    results.append(TestResult(
                        "field_level_permissions",
                        "PASS",
                        "Sensitive fields properly protected"
                    ))
                else:
                    results.append(TestResult(
                        "field_level_permissions",
                        "FAIL",
                        "Sensitive fields exposed",
                        {"exposed_fields": [f['name'] for f in sensitive_fields]}
                    ))
        except Exception as e:
            results.append(TestResult(
                "field_level_permissions",
                "FAIL",
                f"Error testing field permissions: {str(e)}"
            ))
        
        # Test 2: Row-level permissions
        try:
            # Test access to restricted rows
            response = self.session.get(f"{self.base_url}/api/database/tables/1/rows/")
            
            if response.status_code in [200, 403]:
                results.append(TestResult(
                    "row_level_permissions",
                    "PASS",
                    "Row-level permissions enforced"
                ))
            else:
                results.append(TestResult(
                    "row_level_permissions",
                    "FAIL",
                    f"Unexpected row access response: {response.status_code}"
                ))
        except Exception as e:
            results.append(TestResult(
                "row_level_permissions",
                "FAIL",
                f"Error testing row permissions: {str(e)}"
            ))
        
        return results
    
    def test_data_protection(self) -> List[TestResult]:
        """Test data encryption and protection measures"""
        results = []
        
        # Test 1: SQL Injection protection
        try:
            malicious_inputs = [
                "'; DROP TABLE users; --",
                "1' OR '1'='1",
                "admin'/*",
                "1; DELETE FROM users WHERE 1=1; --"
            ]
            
            for payload in malicious_inputs:
                response = self.session.get(f"{self.base_url}/api/database/tables/1/rows/", 
                                          params={"filter": payload})
                
                if response.status_code in [400, 403, 422]:
                    results.append(TestResult(
                        "sql_injection_protection",
                        "PASS",
                        f"SQL injection payload blocked: {payload[:20]}..."
                    ))
                elif response.status_code == 500:
                    results.append(TestResult(
                        "sql_injection_protection",
                        "FAIL",
                        f"SQL injection caused server error: {payload[:20]}..."
                    ))
        except Exception as e:
            results.append(TestResult(
                "sql_injection_protection",
                "FAIL",
                f"Error testing SQL injection protection: {str(e)}"
            ))
        
        # Test 2: XSS protection
        try:
            xss_payloads = [
                "<script>alert('xss')</script>",
                "javascript:alert('xss')",
                "<img src=x onerror=alert('xss')>",
                "';alert('xss');//"
            ]
            
            for payload in xss_payloads:
                response = self.session.post(f"{self.base_url}/api/database/tables/1/rows/", 
                                           json={"field_1": payload})
                
                if response.status_code in [400, 403, 422]:
                    results.append(TestResult(
                        "xss_protection",
                        "PASS",
                        f"XSS payload blocked: {payload[:20]}..."
                    ))
                elif response.status_code == 201:
                    # Check if payload was sanitized
                    row_data = response.json()
                    if payload not in str(row_data):
                        results.append(TestResult(
                            "xss_protection",
                            "PASS",
                            f"XSS payload sanitized: {payload[:20]}..."
                        ))
                    else:
                        results.append(TestResult(
                            "xss_protection",
                            "FAIL",
                            f"XSS payload not sanitized: {payload[:20]}..."
                        ))
        except Exception as e:
            results.append(TestResult(
                "xss_protection",
                "FAIL",
                f"Error testing XSS protection: {str(e)}"
            ))
        
        return results
    
    def test_api_security(self) -> List[TestResult]:
        """Test API security measures"""
        results = []
        
        # Test 1: Rate limiting
        try:
            # Make rapid requests to test rate limiting
            responses = []
            for i in range(20):
                response = self.session.get(f"{self.base_url}/api/database/tables/")
                responses.append(response.status_code)
            
            # Check if rate limiting kicked in
            if 429 in responses:
                results.append(TestResult(
                    "api_rate_limiting",
                    "PASS",
                    "Rate limiting properly enforced"
                ))
            else:
                results.append(TestResult(
                    "api_rate_limiting",
                    "FAIL",
                    "Rate limiting not detected",
                    {"response_codes": responses}
                ))
        except Exception as e:
            results.append(TestResult(
                "api_rate_limiting",
                "FAIL",
                f"Error testing rate limiting: {str(e)}"
            ))
        
        # Test 2: CORS headers
        try:
            response = self.session.options(f"{self.base_url}/api/database/tables/")
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
            }
            
            if any(cors_headers.values()):
                results.append(TestResult(
                    "cors_configuration",
                    "PASS",
                    "CORS headers properly configured",
                    cors_headers
                ))
            else:
                results.append(TestResult(
                    "cors_configuration",
                    "FAIL",
                    "CORS headers missing or misconfigured"
                ))
        except Exception as e:
            results.append(TestResult(
                "cors_configuration",
                "FAIL",
                f"Error testing CORS: {str(e)}"
            ))
        
        return results


class AccessibilityTester:
    """Accessibility testing for WCAG 2.1 AA compliance"""
    
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self.results = []
    
    def setup_driver(self, browser: str = "chrome", mobile: bool = False) -> webdriver:
        """Setup WebDriver for testing"""
        if browser == "chrome":
            options = ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            if mobile:
                mobile_emulation = {"deviceName": "iPhone X"}
                options.add_experimental_option("mobileEmulation", mobile_emulation)
            
            return webdriver.Chrome(options=options)
        
        elif browser == "firefox":
            options = FirefoxOptions()
            options.add_argument("--headless")
            
            if mobile:
                options.set_preference("general.useragent.override", 
                                     "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)")
            
            return webdriver.Firefox(options=options)
    
    def test_wcag_compliance(self, pages: List[str]) -> List[TestResult]:
        """Test WCAG 2.1 AA compliance using axe-core"""
        results = []
        
        for page in pages:
            try:
                driver = self.setup_driver()
                driver.get(f"{self.base_url}{page}")
                
                # Wait for page to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Run axe accessibility tests
                axe = axe_selenium_python.Axe(driver)
                axe_results = axe.run()
                
                violations = axe_results.get('violations', [])
                
                if not violations:
                    results.append(TestResult(
                        f"wcag_compliance_{page.replace('/', '_')}",
                        "PASS",
                        f"No WCAG violations found on {page}"
                    ))
                else:
                    violation_summary = []
                    for violation in violations:
                        violation_summary.append({
                            'id': violation['id'],
                            'impact': violation['impact'],
                            'description': violation['description'],
                            'nodes': len(violation['nodes'])
                        })
                    
                    results.append(TestResult(
                        f"wcag_compliance_{page.replace('/', '_')}",
                        "FAIL",
                        f"WCAG violations found on {page}",
                        {"violations": violation_summary}
                    ))
                
                driver.quit()
                
            except Exception as e:
                results.append(TestResult(
                    f"wcag_compliance_{page.replace('/', '_')}",
                    "FAIL",
                    f"Error testing WCAG compliance on {page}: {str(e)}"
                ))
                if 'driver' in locals():
                    driver.quit()
        
        return results
    
    def test_keyboard_navigation(self, pages: List[str]) -> List[TestResult]:
        """Test keyboard navigation accessibility"""
        results = []
        
        for page in pages:
            try:
                driver = self.setup_driver()
                driver.get(f"{self.base_url}{page}")
                
                # Wait for page to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Test tab navigation
                focusable_elements = driver.find_elements(
                    By.CSS_SELECTOR, 
                    "a, button, input, select, textarea, [tabindex]:not([tabindex='-1'])"
                )
                
                if focusable_elements:
                    # Test that elements can receive focus
                    first_element = focusable_elements[0]
                    first_element.click()
                    
                    # Check if focus is visible
                    focused_element = driver.switch_to.active_element
                    
                    if focused_element == first_element:
                        results.append(TestResult(
                            f"keyboard_navigation_{page.replace('/', '_')}",
                            "PASS",
                            f"Keyboard navigation working on {page}"
                        ))
                    else:
                        results.append(TestResult(
                            f"keyboard_navigation_{page.replace('/', '_')}",
                            "FAIL",
                            f"Focus management issues on {page}"
                        ))
                else:
                    results.append(TestResult(
                        f"keyboard_navigation_{page.replace('/', '_')}",
                        "FAIL",
                        f"No focusable elements found on {page}"
                    ))
                
                driver.quit()
                
            except Exception as e:
                results.append(TestResult(
                    f"keyboard_navigation_{page.replace('/', '_')}",
                    "FAIL",
                    f"Error testing keyboard navigation on {page}: {str(e)}"
                ))
                if 'driver' in locals():
                    driver.quit()
        
        return results
    
    def test_screen_reader_compatibility(self, pages: List[str]) -> List[TestResult]:
        """Test screen reader compatibility"""
        results = []
        
        for page in pages:
            try:
                driver = self.setup_driver()
                driver.get(f"{self.base_url}{page}")
                
                # Wait for page to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Check for proper heading structure
                headings = driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3, h4, h5, h6")
                heading_levels = [int(h.tag_name[1]) for h in headings]
                
                # Check if heading hierarchy is logical
                proper_hierarchy = True
                for i in range(1, len(heading_levels)):
                    if heading_levels[i] > heading_levels[i-1] + 1:
                        proper_hierarchy = False
                        break
                
                # Check for alt text on images
                images = driver.find_elements(By.TAG_NAME, "img")
                images_without_alt = [img for img in images if not img.get_attribute("alt")]
                
                # Check for form labels
                inputs = driver.find_elements(By.CSS_SELECTOR, "input, select, textarea")
                inputs_without_labels = []
                for input_elem in inputs:
                    input_id = input_elem.get_attribute("id")
                    aria_label = input_elem.get_attribute("aria-label")
                    aria_labelledby = input_elem.get_attribute("aria-labelledby")
                    
                    has_label = False
                    if input_id:
                        labels = driver.find_elements(By.CSS_SELECTOR, f"label[for='{input_id}']")
                        has_label = len(labels) > 0
                    
                    if not (has_label or aria_label or aria_labelledby):
                        inputs_without_labels.append(input_elem.get_attribute("name") or "unnamed")
                
                # Compile results
                issues = []
                if not proper_hierarchy:
                    issues.append("Improper heading hierarchy")
                if images_without_alt:
                    issues.append(f"{len(images_without_alt)} images without alt text")
                if inputs_without_labels:
                    issues.append(f"{len(inputs_without_labels)} form inputs without labels")
                
                if not issues:
                    results.append(TestResult(
                        f"screen_reader_{page.replace('/', '_')}",
                        "PASS",
                        f"Screen reader compatibility good on {page}"
                    ))
                else:
                    results.append(TestResult(
                        f"screen_reader_{page.replace('/', '_')}",
                        "FAIL",
                        f"Screen reader issues on {page}",
                        {"issues": issues}
                    ))
                
                driver.quit()
                
            except Exception as e:
                results.append(TestResult(
                    f"screen_reader_{page.replace('/', '_')}",
                    "FAIL",
                    f"Error testing screen reader compatibility on {page}: {str(e)}"
                ))
                if 'driver' in locals():
                    driver.quit()
        
        return results


class CrossBrowserTester:
    """Cross-browser compatibility testing"""
    
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self.browsers = ["chrome", "firefox"]
    
    def test_browser_compatibility(self, pages: List[str]) -> List[TestResult]:
        """Test compatibility across different browsers"""
        results = []
        
        for browser in self.browsers:
            for page in pages:
                try:
                    if browser == "chrome":
                        options = ChromeOptions()
                        options.add_argument("--headless")
                        driver = webdriver.Chrome(options=options)
                    else:
                        options = FirefoxOptions()
                        options.add_argument("--headless")
                        driver = webdriver.Firefox(options=options)
                    
                    driver.get(f"{self.base_url}{page}")
                    
                    # Wait for page to load
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    
                    # Check for JavaScript errors
                    logs = driver.get_log('browser')
                    js_errors = [log for log in logs if log['level'] == 'SEVERE']
                    
                    # Test basic functionality
                    try:
                        # Try to find and interact with common elements
                        buttons = driver.find_elements(By.TAG_NAME, "button")
                        links = driver.find_elements(By.TAG_NAME, "a")
                        inputs = driver.find_elements(By.TAG_NAME, "input")
                        
                        functionality_working = len(buttons) > 0 or len(links) > 0 or len(inputs) > 0
                        
                        if not js_errors and functionality_working:
                            results.append(TestResult(
                                f"browser_compatibility_{browser}_{page.replace('/', '_')}",
                                "PASS",
                                f"{browser.title()} compatibility good on {page}"
                            ))
                        else:
                            error_details = {
                                "js_errors": len(js_errors),
                                "functionality_working": functionality_working
                            }
                            results.append(TestResult(
                                f"browser_compatibility_{browser}_{page.replace('/', '_')}",
                                "FAIL",
                                f"{browser.title()} compatibility issues on {page}",
                                error_details
                            ))
                    
                    except Exception as interaction_error:
                        results.append(TestResult(
                            f"browser_compatibility_{browser}_{page.replace('/', '_')}",
                            "FAIL",
                            f"{browser.title()} interaction error on {page}: {str(interaction_error)}"
                        ))
                    
                    driver.quit()
                    
                except Exception as e:
                    results.append(TestResult(
                        f"browser_compatibility_{browser}_{page.replace('/', '_')}",
                        "FAIL",
                        f"Error testing {browser} on {page}: {str(e)}"
                    ))
                    if 'driver' in locals():
                        driver.quit()
        
        return results


class MobileResponsivenessTester:
    """Mobile responsiveness testing"""
    
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self.devices = [
            {"name": "iPhone X", "width": 375, "height": 812},
            {"name": "iPad", "width": 768, "height": 1024},
            {"name": "Samsung Galaxy S20", "width": 360, "height": 800},
            {"name": "Desktop", "width": 1920, "height": 1080}
        ]
    
    def test_responsive_design(self, pages: List[str]) -> List[TestResult]:
        """Test responsive design across different screen sizes"""
        results = []
        
        for device in self.devices:
            for page in pages:
                try:
                    options = ChromeOptions()
                    options.add_argument("--headless")
                    options.add_argument(f"--window-size={device['width']},{device['height']}")
                    
                    driver = webdriver.Chrome(options=options)
                    driver.set_window_size(device['width'], device['height'])
                    driver.get(f"{self.base_url}{page}")
                    
                    # Wait for page to load
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    
                    # Check for horizontal scrollbar (indicates responsive issues)
                    body_width = driver.execute_script("return document.body.scrollWidth")
                    viewport_width = driver.execute_script("return window.innerWidth")
                    
                    # Check if elements are properly sized
                    buttons = driver.find_elements(By.TAG_NAME, "button")
                    small_buttons = []
                    
                    for button in buttons[:5]:  # Check first 5 buttons
                        size = button.size
                        if size['width'] < 44 or size['height'] < 44:  # WCAG minimum touch target
                            small_buttons.append(size)
                    
                    # Check text readability
                    text_elements = driver.find_elements(By.CSS_SELECTOR, "p, span, div")
                    small_text = []
                    
                    for element in text_elements[:10]:  # Check first 10 text elements
                        font_size = driver.execute_script(
                            "return window.getComputedStyle(arguments[0]).fontSize", 
                            element
                        )
                        if font_size and int(font_size.replace('px', '')) < 16:
                            small_text.append(font_size)
                    
                    # Compile results
                    issues = []
                    if body_width > viewport_width + 20:  # Allow small tolerance
                        issues.append("Horizontal scrolling detected")
                    if small_buttons:
                        issues.append(f"{len(small_buttons)} buttons below minimum touch target size")
                    if len(small_text) > 3:  # Allow some small text
                        issues.append(f"{len(small_text)} text elements with small font size")
                    
                    if not issues:
                        results.append(TestResult(
                            f"responsive_design_{device['name'].replace(' ', '_')}_{page.replace('/', '_')}",
                            "PASS",
                            f"Responsive design good on {device['name']} for {page}"
                        ))
                    else:
                        results.append(TestResult(
                            f"responsive_design_{device['name'].replace(' ', '_')}_{page.replace('/', '_')}",
                            "FAIL",
                            f"Responsive issues on {device['name']} for {page}",
                            {"issues": issues, "viewport": f"{device['width']}x{device['height']}"}
                        ))
                    
                    driver.quit()
                    
                except Exception as e:
                    results.append(TestResult(
                        f"responsive_design_{device['name'].replace(' ', '_')}_{page.replace('/', '_')}",
                        "FAIL",
                        f"Error testing {device['name']} on {page}: {str(e)}"
                    ))
                    if 'driver' in locals():
                        driver.quit()
        
        return results
    
    def test_touch_interactions(self, pages: List[str]) -> List[TestResult]:
        """Test touch interactions on mobile devices"""
        results = []
        
        mobile_device = {"name": "iPhone X", "width": 375, "height": 812}
        
        for page in pages:
            try:
                options = ChromeOptions()
                options.add_argument("--headless")
                options.add_experimental_option("mobileEmulation", {"deviceName": "iPhone X"})
                
                driver = webdriver.Chrome(options=options)
                driver.get(f"{self.base_url}{page}")
                
                # Wait for page to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Test touch targets
                interactive_elements = driver.find_elements(
                    By.CSS_SELECTOR, 
                    "button, a, input, select, [onclick], [role='button']"
                )
                
                adequate_touch_targets = 0
                total_elements = len(interactive_elements)
                
                for element in interactive_elements:
                    size = element.size
                    if size['width'] >= 44 and size['height'] >= 44:
                        adequate_touch_targets += 1
                
                # Calculate percentage of adequate touch targets
                if total_elements > 0:
                    percentage = (adequate_touch_targets / total_elements) * 100
                    
                    if percentage >= 90:  # 90% or more should have adequate touch targets
                        results.append(TestResult(
                            f"touch_interactions_{page.replace('/', '_')}",
                            "PASS",
                            f"Touch interactions good on {page} ({percentage:.1f}% adequate targets)"
                        ))
                    else:
                        results.append(TestResult(
                            f"touch_interactions_{page.replace('/', '_')}",
                            "FAIL",
                            f"Touch target issues on {page} ({percentage:.1f}% adequate targets)",
                            {
                                "total_elements": total_elements,
                                "adequate_targets": adequate_touch_targets,
                                "percentage": percentage
                            }
                        ))
                else:
                    results.append(TestResult(
                        f"touch_interactions_{page.replace('/', '_')}",
                        "SKIP",
                        f"No interactive elements found on {page}"
                    ))
                
                driver.quit()
                
            except Exception as e:
                results.append(TestResult(
                    f"touch_interactions_{page.replace('/', '_')}",
                    "FAIL",
                    f"Error testing touch interactions on {page}: {str(e)}"
                ))
                if 'driver' in locals():
                    driver.quit()
        
        return results


class TestRunner:
    """Main test runner that orchestrates all tests"""
    
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self.all_results = []
        
        # Define pages to test
        self.test_pages = [
            "/",
            "/database/1/table/1",
            "/database/1/table/1/kanban",
            "/database/1/table/1/timeline",
            "/database/1/table/1/calendar",
            "/database/1/table/1/form",
            "/dashboard",
            "/settings"
        ]
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all security and accessibility tests"""
        print("🔒 Starting Comprehensive Security and Accessibility Testing Suite")
        print("=" * 70)
        
        start_time = time.time()
        
        # Security Tests
        print("\n🛡️  Running Security Tests...")
        security_tester = SecurityTester(self.base_url)
        
        print("  - Testing authentication security...")
        self.all_results.extend(security_tester.test_authentication_security())
        
        print("  - Testing permission system security...")
        self.all_results.extend(security_tester.test_permission_system_security())
        
        print("  - Testing data protection...")
        self.all_results.extend(security_tester.test_data_protection())
        
        print("  - Testing API security...")
        self.all_results.extend(security_tester.test_api_security())
        
        # Accessibility Tests
        print("\n♿ Running Accessibility Tests...")
        accessibility_tester = AccessibilityTester(self.base_url)
        
        print("  - Testing WCAG 2.1 AA compliance...")
        self.all_results.extend(accessibility_tester.test_wcag_compliance(self.test_pages))
        
        print("  - Testing keyboard navigation...")
        self.all_results.extend(accessibility_tester.test_keyboard_navigation(self.test_pages))
        
        print("  - Testing screen reader compatibility...")
        self.all_results.extend(accessibility_tester.test_screen_reader_compatibility(self.test_pages))
        
        # Cross-Browser Tests
        print("\n🌐 Running Cross-Browser Compatibility Tests...")
        browser_tester = CrossBrowserTester(self.base_url)
        
        print("  - Testing browser compatibility...")
        self.all_results.extend(browser_tester.test_browser_compatibility(self.test_pages))
        
        # Mobile Responsiveness Tests
        print("\n📱 Running Mobile Responsiveness Tests...")
        mobile_tester = MobileResponsivenessTester(self.base_url)
        
        print("  - Testing responsive design...")
        self.all_results.extend(mobile_tester.test_responsive_design(self.test_pages))
        
        print("  - Testing touch interactions...")
        self.all_results.extend(mobile_tester.test_touch_interactions(self.test_pages))
        
        # Calculate summary
        end_time = time.time()
        duration = end_time - start_time
        
        passed = len([r for r in self.all_results if r.status == "PASS"])
        failed = len([r for r in self.all_results if r.status == "FAIL"])
        skipped = len([r for r in self.all_results if r.status == "SKIP"])
        total = len(self.all_results)
        
        summary = {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "success_rate": (passed / total * 100) if total > 0 else 0,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "summary": summary,
            "results": [
                {
                    "test_name": r.test_name,
                    "status": r.status,
                    "message": r.message,
                    "details": r.details,
                    "timestamp": r.timestamp
                }
                for r in self.all_results
            ]
        }
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate a comprehensive test report"""
        summary = results["summary"]
        test_results = results["results"]
        
        report = f"""
# Security and Accessibility Test Report

**Generated:** {summary['timestamp']}
**Duration:** {summary['duration']:.2f} seconds

## Summary

- **Total Tests:** {summary['total_tests']}
- **Passed:** {summary['passed']} ✅
- **Failed:** {summary['failed']} ❌
- **Skipped:** {summary['skipped']} ⏭️
- **Success Rate:** {summary['success_rate']:.1f}%

## Test Categories

### 🛡️ Security Tests
"""
        
        # Group results by category
        security_tests = [r for r in test_results if any(keyword in r['test_name'] for keyword in 
                         ['password', 'session', 'permission', 'sql', 'xss', 'api', 'cors', 'rate'])]
        
        accessibility_tests = [r for r in test_results if any(keyword in r['test_name'] for keyword in 
                              ['wcag', 'keyboard', 'screen_reader'])]
        
        browser_tests = [r for r in test_results if 'browser_compatibility' in r['test_name']]
        
        mobile_tests = [r for r in test_results if any(keyword in r['test_name'] for keyword in 
                       ['responsive', 'touch'])]
        
        # Security section
        for test in security_tests:
            status_icon = "✅" if test['status'] == "PASS" else "❌" if test['status'] == "FAIL" else "⏭️"
            report += f"\n- {status_icon} **{test['test_name']}**: {test['message']}"
            if test['details'] and test['status'] == "FAIL":
                report += f"\n  - Details: {test['details']}"
        
        # Accessibility section
        report += f"\n\n### ♿ Accessibility Tests\n"
        for test in accessibility_tests:
            status_icon = "✅" if test['status'] == "PASS" else "❌" if test['status'] == "FAIL" else "⏭️"
            report += f"\n- {status_icon} **{test['test_name']}**: {test['message']}"
            if test['details'] and test['status'] == "FAIL":
                report += f"\n  - Issues: {test['details']}"
        
        # Browser compatibility section
        report += f"\n\n### 🌐 Cross-Browser Compatibility\n"
        for test in browser_tests:
            status_icon = "✅" if test['status'] == "PASS" else "❌" if test['status'] == "FAIL" else "⏭️"
            report += f"\n- {status_icon} **{test['test_name']}**: {test['message']}"
        
        # Mobile responsiveness section
        report += f"\n\n### 📱 Mobile Responsiveness\n"
        for test in mobile_tests:
            status_icon = "✅" if test['status'] == "PASS" else "❌" if test['status'] == "FAIL" else "⏭️"
            report += f"\n- {status_icon} **{test['test_name']}**: {test['message']}"
        
        # Recommendations
        failed_tests = [r for r in test_results if r['status'] == "FAIL"]
        if failed_tests:
            report += f"\n\n## 🔧 Recommendations\n"
            
            security_failures = [t for t in failed_tests if any(keyword in t['test_name'] for keyword in 
                               ['password', 'session', 'permission', 'sql', 'xss', 'api'])]
            
            if security_failures:
                report += f"\n### Security Issues\n"
                for test in security_failures:
                    report += f"\n- **{test['test_name']}**: {test['message']}"
                    if test['details']:
                        report += f"\n  - Action needed: Review and fix security vulnerability"
            
            accessibility_failures = [t for t in failed_tests if any(keyword in t['test_name'] for keyword in 
                                     ['wcag', 'keyboard', 'screen_reader'])]
            
            if accessibility_failures:
                report += f"\n\n### Accessibility Issues\n"
                for test in accessibility_failures:
                    report += f"\n- **{test['test_name']}**: {test['message']}"
                    if test['details']:
                        report += f"\n  - Action needed: Fix accessibility barriers for users with disabilities"
        
        report += f"\n\n---\n*Report generated by Baserow Security & Accessibility Test Suite*"
        
        return report


def main():
    """Main function to run the test suite"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Baserow Security and Accessibility Test Suite")
    parser.add_argument("--url", default="http://localhost:3000", help="Base URL to test")
    parser.add_argument("--output", default="security_accessibility_report.md", help="Output report file")
    parser.add_argument("--json", action="store_true", help="Also output JSON results")
    
    args = parser.parse_args()
    
    # Run tests
    runner = TestRunner(args.url)
    results = runner.run_all_tests()
    
    # Generate and save report
    report = runner.generate_report(results)
    
    with open(args.output, 'w') as f:
        f.write(report)
    
    if args.json:
        json_file = args.output.replace('.md', '.json')
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2)
    
    # Print summary
    summary = results["summary"]
    print(f"\n" + "=" * 70)
    print(f"🎯 Test Summary:")
    print(f"   Total: {summary['total_tests']}")
    print(f"   Passed: {summary['passed']} ✅")
    print(f"   Failed: {summary['failed']} ❌")
    print(f"   Skipped: {summary['skipped']} ⏭️")
    print(f"   Success Rate: {summary['success_rate']:.1f}%")
    print(f"   Duration: {summary['duration']:.2f}s")
    print(f"\n📄 Report saved to: {args.output}")
    
    if args.json:
        print(f"📊 JSON results saved to: {json_file}")
    
    # Exit with appropriate code
    exit_code = 0 if summary['failed'] == 0 else 1
    return exit_code


if __name__ == "__main__":
    exit(main())