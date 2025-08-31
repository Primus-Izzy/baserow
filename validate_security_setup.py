#!/usr/bin/env python3
"""
Quick validation script to test security testing setup
This ensures all dependencies are working before running the full test suite
"""

import sys
import json
import time
from pathlib import Path

def check_imports():
    """Check if all required Python packages are available"""
    print("🔍 Checking Python dependencies...")
    
    required_packages = [
        ('selenium', 'Selenium WebDriver'),
        ('requests', 'HTTP requests library'),
        ('axe_selenium_python', 'Axe accessibility testing'),
    ]
    
    missing_packages = []
    
    for package, description in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {description}")
        except ImportError:
            print(f"  ❌ {description} - Missing")
            missing_packages.append(package)
    
    return len(missing_packages) == 0

def check_webdriver():
    """Check if WebDriver is working"""
    print("\n🌐 Checking WebDriver setup...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        # Test Chrome WebDriver
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=options)
        driver.get("https://www.google.com")
        
        if "Google" in driver.title:
            print("  ✅ Chrome WebDriver working")
            driver.quit()
            return True
        else:
            print("  ❌ Chrome WebDriver not responding correctly")
            driver.quit()
            return False
            
    except Exception as e:
        print(f"  ❌ Chrome WebDriver error: {str(e)}")
        return False

def check_accessibility_tools():
    """Check if accessibility testing tools are working"""
    print("\n♿ Checking accessibility tools...")
    
    try:
        import axe_selenium_python
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=options)
        driver.get("data:text/html,<html><body><h1>Test</h1><button>Click me</button></body></html>")
        
        axe = axe_selenium_python.Axe(driver)
        results = axe.run()
        
        if 'violations' in results:
            print("  ✅ Axe accessibility testing working")
            driver.quit()
            return True
        else:
            print("  ❌ Axe accessibility testing not working correctly")
            driver.quit()
            return False
            
    except Exception as e:
        print(f"  ❌ Accessibility tools error: {str(e)}")
        return False

def check_config_file():
    """Check if configuration file is valid"""
    print("\n⚙️  Checking configuration file...")
    
    config_file = Path("security_test_config.json")
    
    if not config_file.exists():
        print("  ❌ Configuration file not found")
        return False
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        required_sections = ['security_tests', 'accessibility_tests', 'test_pages']
        
        for section in required_sections:
            if section not in config:
                print(f"  ❌ Missing configuration section: {section}")
                return False
        
        print("  ✅ Configuration file valid")
        return True
        
    except json.JSONDecodeError as e:
        print(f"  ❌ Configuration file JSON error: {str(e)}")
        return False
    except Exception as e:
        print(f"  ❌ Configuration file error: {str(e)}")
        return False

def test_basic_security_functions():
    """Test basic security testing functions"""
    print("\n🔒 Testing security functions...")
    
    try:
        import requests
        
        # Test basic HTTP request
        response = requests.get("https://httpbin.org/get", timeout=10)
        
        if response.status_code == 200:
            print("  ✅ HTTP requests working")
        else:
            print(f"  ❌ HTTP request failed with status: {response.status_code}")
            return False
        
        # Test request with headers
        headers = {'User-Agent': 'Security-Test-Suite/1.0'}
        response = requests.get("https://httpbin.org/headers", headers=headers, timeout=10)
        
        if response.status_code == 200 and 'Security-Test-Suite' in response.text:
            print("  ✅ Custom headers working")
        else:
            print("  ❌ Custom headers not working")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Security functions error: {str(e)}")
        return False

def run_mini_security_test():
    """Run a mini security test to validate functionality"""
    print("\n🧪 Running mini security test...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # Create a simple test page with potential issues
        test_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Security Test Page</title>
        </head>
        <body>
            <h1>Test Page</h1>
            <form>
                <input type="text" placeholder="Username">
                <input type="password" placeholder="Password">
                <button type="submit">Login</button>
            </form>
            <img src="test.jpg">
            <a href="#" onclick="alert('test')">Click me</a>
        </body>
        </html>
        """
        
        driver = webdriver.Chrome(options=options)
        driver.get(f"data:text/html,{test_html}")
        
        # Test basic element detection
        forms = driver.find_elements(By.TAG_NAME, "form")
        inputs = driver.find_elements(By.TAG_NAME, "input")
        images = driver.find_elements(By.TAG_NAME, "img")
        
        if len(forms) > 0 and len(inputs) > 0:
            print("  ✅ Element detection working")
        else:
            print("  ❌ Element detection not working")
            driver.quit()
            return False
        
        # Test accessibility check
        import axe_selenium_python
        axe = axe_selenium_python.Axe(driver)
        results = axe.run()
        
        violations = results.get('violations', [])
        if len(violations) > 0:
            print(f"  ✅ Accessibility testing detected {len(violations)} issues (expected)")
        else:
            print("  ⚠️  Accessibility testing didn't detect expected issues")
        
        driver.quit()
        return True
        
    except Exception as e:
        print(f"  ❌ Mini security test error: {str(e)}")
        return False

def main():
    """Main validation function"""
    print("🔒 Security Testing Setup Validation")
    print("=" * 50)
    
    all_checks_passed = True
    
    # Run all validation checks
    checks = [
        check_imports,
        check_webdriver,
        check_accessibility_tools,
        check_config_file,
        test_basic_security_functions,
        run_mini_security_test
    ]
    
    for check in checks:
        try:
            if not check():
                all_checks_passed = False
        except Exception as e:
            print(f"  ❌ Check failed with error: {str(e)}")
            all_checks_passed = False
    
    print("\n" + "=" * 50)
    
    if all_checks_passed:
        print("✅ All validation checks passed!")
        print("🚀 Ready to run comprehensive security and accessibility tests")
        print("\nNext steps:")
        print("  1. Start your Baserow instance")
        print("  2. Run: python test_security_accessibility_comprehensive.py")
        print("  3. Or use the shell script: ./run_security_accessibility_tests.sh")
        return 0
    else:
        print("❌ Some validation checks failed!")
        print("🔧 Please fix the issues above before running the full test suite")
        print("\nCommon fixes:")
        print("  - Install missing Python packages: pip install selenium requests axe-selenium-python")
        print("  - Install Chrome browser")
        print("  - Check your internet connection")
        return 1

if __name__ == "__main__":
    exit(main())