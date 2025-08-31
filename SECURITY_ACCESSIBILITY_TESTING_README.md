# Security and Accessibility Testing Suite

A comprehensive testing framework for validating security measures and accessibility compliance in the Baserow expansion project.

## 🎯 Overview

This testing suite implements **Task 32** from the Baserow expansion plan, providing:

- **Security Testing**: Permission system validation, data protection, API security
- **Accessibility Testing**: WCAG 2.1 AA compliance verification
- **Cross-Browser Compatibility**: Testing across Chrome, Firefox, and other browsers
- **Mobile Responsiveness**: Touch-friendly interface validation

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- Chrome browser (required)
- Firefox browser (recommended)
- Active Baserow instance

### Installation & Setup

1. **Validate your setup** (recommended first step):
   ```bash
   python validate_security_setup.py
   ```

2. **Run the full test suite**:
   
   **Linux/macOS:**
   ```bash
   ./run_security_accessibility_tests.sh
   ```
   
   **Windows PowerShell:**
   ```powershell
   .\run_security_accessibility_tests.ps1
   ```
   
   **Direct Python execution:**
   ```bash
   python test_security_accessibility_comprehensive.py --url http://localhost:3000
   ```

### Custom Configuration

Modify `security_test_config.json` to customize:
- Test pages and endpoints
- Security payloads and thresholds
- Accessibility rules and standards
- Browser and device configurations

## 🔒 Security Tests

### Authentication Security
- **Password Strength**: Validates weak password rejection
- **Session Management**: Tests session timeout and security
- **Brute Force Protection**: Verifies login attempt limiting

### Permission System Security
- **Field-Level Permissions**: Tests unauthorized field access
- **Row-Level Permissions**: Validates record access controls
- **API Key Security**: Tests API authentication and authorization

### Data Protection
- **SQL Injection**: Tests database query protection
- **XSS Prevention**: Validates cross-site scripting protection
- **Input Sanitization**: Tests malicious input handling

### API Security
- **Rate Limiting**: Tests API request throttling
- **CORS Configuration**: Validates cross-origin policies
- **CSRF Protection**: Tests cross-site request forgery prevention

## ♿ Accessibility Tests

### WCAG 2.1 AA Compliance
- **Color Contrast**: Validates sufficient contrast ratios
- **Keyboard Navigation**: Tests full keyboard accessibility
- **Focus Management**: Validates focus indicators and order
- **Screen Reader Support**: Tests semantic markup and ARIA labels

### Interactive Elements
- **Touch Targets**: Validates minimum 44px touch targets
- **Form Labels**: Tests proper form labeling
- **Error Messages**: Validates accessible error handling
- **Live Regions**: Tests dynamic content announcements

## 🌐 Cross-Browser Testing

### Supported Browsers
- **Chrome**: Latest version (primary)
- **Firefox**: Latest version (secondary)
- **Edge**: Optional configuration
- **Safari**: Optional configuration

### Test Coverage
- JavaScript functionality
- CSS rendering consistency
- Interactive element behavior
- Performance across browsers

## 📱 Mobile Responsiveness

### Device Testing
- **iPhone X**: 375x812px
- **iPad**: 768x1024px
- **Samsung Galaxy S20**: 360x800px
- **Desktop**: 1920x1080px

### Responsive Features
- Touch-friendly targets (minimum 44px)
- Readable text sizes (minimum 16px)
- Proper viewport scaling
- Gesture support validation

## 📊 Test Results & Reporting

### Output Formats
- **Markdown Report**: Human-readable summary with recommendations
- **JSON Results**: Machine-readable detailed results
- **Screenshots**: Visual evidence of issues (when applicable)

### Report Sections
1. **Executive Summary**: Pass/fail counts and success rate
2. **Security Issues**: Critical vulnerabilities and recommendations
3. **Accessibility Violations**: WCAG compliance issues
4. **Browser Compatibility**: Cross-browser issues
5. **Mobile Issues**: Responsive design problems

### Sample Report Structure
```
# Security and Accessibility Test Report

## Summary
- Total Tests: 156
- Passed: 142 ✅
- Failed: 12 ❌
- Skipped: 2 ⏭️
- Success Rate: 91.0%

## 🛡️ Security Tests
- ✅ password_strength_validation: Weak passwords correctly rejected
- ❌ sql_injection_protection: SQL injection payload not blocked
- ✅ xss_protection: XSS payload sanitized

## ♿ Accessibility Tests
- ✅ wcag_compliance_home: No WCAG violations found
- ❌ keyboard_navigation_kanban: Focus management issues
- ✅ screen_reader_table: Screen reader compatibility good
```

## 🔧 Configuration Options

### Test Configuration (`security_test_config.json`)

```json
{
  "security_tests": {
    "authentication": {
      "enabled": true,
      "weak_passwords": ["123", "password", "admin"],
      "session_timeout_seconds": 3600
    },
    "data_protection": {
      "sql_injection_payloads": ["'; DROP TABLE users; --"],
      "xss_payloads": ["<script>alert('xss')</script>"]
    }
  },
  "accessibility_tests": {
    "wcag_compliance": {
      "level": "AA",
      "version": "2.1"
    }
  }
}
```

### Command Line Options

```bash
# Custom URL
python test_security_accessibility_comprehensive.py --url https://demo.baserow.io

# Custom output location
python test_security_accessibility_comprehensive.py --output ./reports/security_report.md

# JSON output
python test_security_accessibility_comprehensive.py --json
```

## 🚨 Troubleshooting

### Common Issues

**WebDriver Not Found**
```bash
# Install webdriver-manager
pip install webdriver-manager

# Or manually download ChromeDriver
# Place in PATH or specify location
```

**Chrome/Firefox Not Found**
- Install Chrome: https://google.com/chrome
- Install Firefox: https://mozilla.org/firefox
- Update browser paths in configuration

**Permission Denied (Linux/macOS)**
```bash
chmod +x run_security_accessibility_tests.sh
```

**Python Dependencies Missing**
```bash
pip install -r requirements.txt
# Or install individually:
pip install selenium requests axe-selenium-python
```

### Debug Mode

Enable verbose logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔄 Continuous Integration

### GitHub Actions Example
```yaml
name: Security and Accessibility Tests
on: [push, pull_request]
jobs:
  security-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run security tests
        run: python test_security_accessibility_comprehensive.py
```

### Jenkins Pipeline
```groovy
pipeline {
    agent any
    stages {
        stage('Security Tests') {
            steps {
                sh 'python validate_security_setup.py'
                sh 'python test_security_accessibility_comprehensive.py --json'
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'test_results',
                    reportFiles: '*.html',
                    reportName: 'Security Test Report'
                ])
            }
        }
    }
}
```

## 📈 Performance Considerations

### Test Optimization
- **Parallel Execution**: Run browser tests in parallel
- **Headless Mode**: Faster execution without GUI
- **Selective Testing**: Configure which tests to run
- **Caching**: Reuse WebDriver instances when possible

### Resource Usage
- **Memory**: ~200MB per browser instance
- **CPU**: Moderate during test execution
- **Network**: Minimal (mostly local testing)
- **Disk**: ~50MB for reports and screenshots

## 🤝 Contributing

### Adding New Security Tests
1. Extend `SecurityTester` class
2. Add test method following naming convention
3. Update configuration schema
4. Add documentation

### Adding New Accessibility Tests
1. Extend `AccessibilityTester` class
2. Follow WCAG guidelines
3. Include axe-core rule references
4. Test with real assistive technologies

### Test Categories
- **Critical**: Must pass for security/accessibility
- **High**: Important for user experience
- **Medium**: Best practices and recommendations
- **Low**: Nice-to-have improvements

## 📚 References

### Security Standards
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

### Accessibility Standards
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Section 508 Standards](https://www.section508.gov/)
- [axe-core Rules](https://github.com/dequelabs/axe-core/blob/develop/doc/rule-descriptions.md)

### Testing Tools
- [Selenium WebDriver](https://selenium-python.readthedocs.io/)
- [axe-selenium-python](https://github.com/mozilla-services/axe-selenium-python)
- [Requests Library](https://docs.python-requests.org/)

## 📄 License

This testing suite is part of the Baserow project and follows the same licensing terms.

---

**Need Help?** 
- Check the troubleshooting section above
- Run `python validate_security_setup.py` to diagnose issues
- Review the configuration file for customization options
- Consult the Baserow documentation for project-specific details