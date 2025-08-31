#!/bin/bash

# Security and Accessibility Test Runner for Baserow
# This script sets up the environment and runs comprehensive security and accessibility tests

set -e

echo "🔒 Baserow Security & Accessibility Test Suite"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
BASE_URL="http://localhost:3000"
OUTPUT_DIR="test_results"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_FILE="${OUTPUT_DIR}/security_accessibility_report_${TIMESTAMP}.md"
JSON_FILE="${OUTPUT_DIR}/security_accessibility_results_${TIMESTAMP}.json"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --url)
            BASE_URL="$2"
            shift 2
            ;;
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --url URL          Base URL to test (default: http://localhost:3000)"
            echo "  --output-dir DIR   Output directory for reports (default: test_results)"
            echo "  --help            Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                                    # Test localhost:3000"
            echo "  $0 --url https://demo.baserow.io     # Test demo instance"
            echo "  $0 --output-dir ./reports            # Custom output directory"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}Configuration:${NC}"
echo "  Base URL: $BASE_URL"
echo "  Output Directory: $OUTPUT_DIR"
echo "  Report File: $REPORT_FILE"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Check if required tools are installed
echo -e "${YELLOW}Checking dependencies...${NC}"

check_dependency() {
    if command -v "$1" &> /dev/null; then
        echo -e "  ✅ $1 is installed"
        return 0
    else
        echo -e "  ❌ $1 is not installed"
        return 1
    fi
}

MISSING_DEPS=0

# Check Python
if ! check_dependency python3; then
    MISSING_DEPS=1
fi

# Check pip
if ! check_dependency pip3; then
    MISSING_DEPS=1
fi

# Check if Chrome/Chromium is available
if ! command -v google-chrome &> /dev/null && ! command -v chromium-browser &> /dev/null && ! command -v chromium &> /dev/null; then
    echo -e "  ❌ Chrome/Chromium is not installed"
    MISSING_DEPS=1
else
    echo -e "  ✅ Chrome/Chromium is available"
fi

# Check if Firefox is available
if ! check_dependency firefox; then
    echo -e "  ⚠️  Firefox is not installed (optional, but recommended for cross-browser testing)"
fi

if [ $MISSING_DEPS -eq 1 ]; then
    echo -e "\n${RED}Missing required dependencies. Please install them and try again.${NC}"
    echo ""
    echo "Installation commands:"
    echo "  Ubuntu/Debian: sudo apt-get install python3 python3-pip chromium-browser firefox"
    echo "  macOS: brew install python3 chromium firefox"
    echo "  Windows: Install Python from python.org and Chrome from google.com"
    exit 1
fi

# Install Python dependencies
echo -e "\n${YELLOW}Installing Python dependencies...${NC}"

# Create a temporary requirements file
cat > /tmp/test_requirements.txt << EOF
selenium>=4.0.0
requests>=2.25.0
axe-selenium-python>=2.1.0
webdriver-manager>=3.8.0
pytest>=6.0.0
pytest-html>=3.1.0
pytest-xdist>=2.5.0
EOF

pip3 install -r /tmp/test_requirements.txt --quiet

# Download and setup WebDriver
echo -e "\n${YELLOW}Setting up WebDriver...${NC}"

python3 -c "
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
import os

print('  📥 Downloading ChromeDriver...')
try:
    ChromeDriverManager().install()
    print('  ✅ ChromeDriver installed')
except Exception as e:
    print(f'  ⚠️  ChromeDriver installation failed: {e}')

print('  📥 Downloading GeckoDriver...')
try:
    GeckoDriverManager().install()
    print('  ✅ GeckoDriver installed')
except Exception as e:
    print(f'  ⚠️  GeckoDriver installation failed: {e}')
"

# Check if Baserow is running
echo -e "\n${YELLOW}Checking if Baserow is accessible...${NC}"

if curl -s --head "$BASE_URL" | head -n 1 | grep -q "200 OK\|302 Found\|301 Moved"; then
    echo -e "  ✅ Baserow is accessible at $BASE_URL"
else
    echo -e "  ⚠️  Baserow may not be running at $BASE_URL"
    echo -e "     ${YELLOW}Continuing anyway - some tests may fail${NC}"
fi

# Run the security and accessibility tests
echo -e "\n${GREEN}Starting Security and Accessibility Tests...${NC}"
echo "This may take several minutes depending on the number of pages and tests."
echo ""

# Run the main test suite
python3 test_security_accessibility_comprehensive.py \
    --url "$BASE_URL" \
    --output "$REPORT_FILE" \
    --json

# Check if tests completed successfully
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ All tests completed successfully!${NC}"
    SUCCESS_ICON="✅"
else
    echo -e "\n${YELLOW}⚠️  Tests completed with some failures.${NC}"
    SUCCESS_ICON="⚠️"
fi

# Generate summary
echo -e "\n${BLUE}📊 Test Results Summary:${NC}"

if [ -f "$JSON_FILE" ]; then
    python3 -c "
import json
import sys

try:
    with open('$JSON_FILE', 'r') as f:
        results = json.load(f)
    
    summary = results['summary']
    
    print(f\"  Total Tests: {summary['total_tests']}\")
    print(f\"  Passed: {summary['passed']} ✅\")
    print(f\"  Failed: {summary['failed']} ❌\")
    print(f\"  Skipped: {summary['skipped']} ⏭️\")
    print(f\"  Success Rate: {summary['success_rate']:.1f}%\")
    print(f\"  Duration: {summary['duration']:.2f} seconds\")
    
    # Show critical failures
    failed_tests = [r for r in results['results'] if r['status'] == 'FAIL']
    security_failures = [t for t in failed_tests if any(keyword in t['test_name'] for keyword in ['password', 'session', 'permission', 'sql', 'xss', 'api'])]
    
    if security_failures:
        print(f\"\\n  🚨 Critical Security Issues: {len(security_failures)}\")
        for test in security_failures[:3]:  # Show first 3
            print(f\"    - {test['test_name']}: {test['message']}\")
        if len(security_failures) > 3:
            print(f\"    ... and {len(security_failures) - 3} more\")
    
except Exception as e:
    print(f\"Error reading results: {e}\")
    sys.exit(1)
"
else
    echo -e "  ${RED}❌ Could not find results file${NC}"
fi

# Show file locations
echo -e "\n${BLUE}📄 Generated Reports:${NC}"
echo "  📋 Markdown Report: $REPORT_FILE"
if [ -f "$JSON_FILE" ]; then
    echo "  📊 JSON Results: $JSON_FILE"
fi

# Open report if possible
if command -v xdg-open &> /dev/null; then
    echo -e "\n${YELLOW}Opening report in default application...${NC}"
    xdg-open "$REPORT_FILE" &
elif command -v open &> /dev/null; then
    echo -e "\n${YELLOW}Opening report in default application...${NC}"
    open "$REPORT_FILE" &
fi

# Cleanup
rm -f /tmp/test_requirements.txt

echo -e "\n${SUCCESS_ICON} Security and Accessibility Testing Complete!"
echo -e "   View the detailed report at: ${BLUE}$REPORT_FILE${NC}"

# Exit with appropriate code based on test results
if [ -f "$JSON_FILE" ]; then
    FAILED_COUNT=$(python3 -c "
import json
try:
    with open('$JSON_FILE', 'r') as f:
        results = json.load(f)
    print(results['summary']['failed'])
except:
    print('0')
")
    
    if [ "$FAILED_COUNT" -gt 0 ]; then
        exit 1
    fi
fi

exit 0