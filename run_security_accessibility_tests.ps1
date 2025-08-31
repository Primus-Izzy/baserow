# Security and Accessibility Test Runner for Baserow (PowerShell)
# This script sets up the environment and runs comprehensive security and accessibility tests

param(
    [string]$BaseUrl = "http://localhost:3000",
    [string]$OutputDir = "test_results",
    [switch]$Help
)

if ($Help) {
    Write-Host "Baserow Security & Accessibility Test Suite" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\run_security_accessibility_tests.ps1 [OPTIONS]" -ForegroundColor White
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "  -BaseUrl URL       Base URL to test (default: http://localhost:3000)" -ForegroundColor White
    Write-Host "  -OutputDir DIR     Output directory for reports (default: test_results)" -ForegroundColor White
    Write-Host "  -Help             Show this help message" -ForegroundColor White
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\run_security_accessibility_tests.ps1" -ForegroundColor White
    Write-Host "  .\run_security_accessibility_tests.ps1 -BaseUrl https://demo.baserow.io" -ForegroundColor White
    Write-Host "  .\run_security_accessibility_tests.ps1 -OutputDir .\reports" -ForegroundColor White
    exit 0
}

Write-Host "🔒 Baserow Security & Accessibility Test Suite" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$ReportFile = Join-Path $OutputDir "security_accessibility_report_$Timestamp.md"
$JsonFile = Join-Path $OutputDir "security_accessibility_results_$Timestamp.json"

Write-Host ""
Write-Host "Configuration:" -ForegroundColor Blue
Write-Host "  Base URL: $BaseUrl" -ForegroundColor White
Write-Host "  Output Directory: $OutputDir" -ForegroundColor White
Write-Host "  Report File: $ReportFile" -ForegroundColor White
Write-Host ""

# Create output directory
if (!(Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

# Check dependencies
Write-Host "Checking dependencies..." -ForegroundColor Yellow

function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        Write-Host "  ✅ $Command is available" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "  ❌ $Command is not available" -ForegroundColor Red
        return $false
    }
}

$MissingDeps = 0

# Check Python
if (!(Test-Command "python")) {
    if (!(Test-Command "python3")) {
        $MissingDeps++
    }
}

# Check pip
if (!(Test-Command "pip")) {
    if (!(Test-Command "pip3")) {
        $MissingDeps++
    }
}

# Check Chrome
$ChromePaths = @(
    "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe",
    "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
    "${env:LOCALAPPDATA}\Google\Chrome\Application\chrome.exe"
)

$ChromeFound = $false
foreach ($path in $ChromePaths) {
    if (Test-Path $path) {
        Write-Host "  ✅ Chrome is available" -ForegroundColor Green
        $ChromeFound = $true
        break
    }
}

if (!$ChromeFound) {
    Write-Host "  ❌ Chrome is not installed" -ForegroundColor Red
    $MissingDeps++
}

# Check Firefox (optional)
$FirefoxPaths = @(
    "${env:ProgramFiles}\Mozilla Firefox\firefox.exe",
    "${env:ProgramFiles(x86)}\Mozilla Firefox\firefox.exe"
)

$FirefoxFound = $false
foreach ($path in $FirefoxPaths) {
    if (Test-Path $path) {
        Write-Host "  ✅ Firefox is available" -ForegroundColor Green
        $FirefoxFound = $true
        break
    }
}

if (!$FirefoxFound) {
    Write-Host "  ⚠️  Firefox is not installed (optional, but recommended)" -ForegroundColor Yellow
}

if ($MissingDeps -gt 0) {
    Write-Host ""
    Write-Host "Missing required dependencies. Please install them and try again." -ForegroundColor Red
    Write-Host ""
    Write-Host "Installation instructions:" -ForegroundColor Yellow
    Write-Host "  1. Install Python from https://python.org" -ForegroundColor White
    Write-Host "  2. Install Chrome from https://google.com/chrome" -ForegroundColor White
    Write-Host "  3. Optionally install Firefox from https://mozilla.org/firefox" -ForegroundColor White
    exit 1
}

# Install Python dependencies
Write-Host ""
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow

$RequirementsContent = @"
selenium>=4.0.0
requests>=2.25.0
axe-selenium-python>=2.1.0
webdriver-manager>=3.8.0
pytest>=6.0.0
pytest-html>=3.1.0
pytest-xdist>=2.5.0
"@

$TempRequirements = Join-Path $env:TEMP "test_requirements.txt"
$RequirementsContent | Out-File -FilePath $TempRequirements -Encoding UTF8

try {
    $PipCommand = if (Get-Command "pip3" -ErrorAction SilentlyContinue) { "pip3" } else { "pip" }
    & $PipCommand install -r $TempRequirements --quiet
    Write-Host "  ✅ Python dependencies installed" -ForegroundColor Green
}
catch {
    Write-Host "  ❌ Failed to install Python dependencies: $_" -ForegroundColor Red
    exit 1
}
finally {
    Remove-Item $TempRequirements -ErrorAction SilentlyContinue
}

# Setup WebDriver
Write-Host ""
Write-Host "Setting up WebDriver..." -ForegroundColor Yellow

$PythonCommand = if (Get-Command "python3" -ErrorAction SilentlyContinue) { "python3" } else { "python" }

$WebDriverSetup = @"
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
"@

try {
    $WebDriverSetup | & $PythonCommand
}
catch {
    Write-Host "  ⚠️  WebDriver setup encountered issues, but continuing..." -ForegroundColor Yellow
}

# Check if Baserow is accessible
Write-Host ""
Write-Host "Checking if Baserow is accessible..." -ForegroundColor Yellow

try {
    $Response = Invoke-WebRequest -Uri $BaseUrl -Method Head -TimeoutSec 10 -ErrorAction Stop
    Write-Host "  ✅ Baserow is accessible at $BaseUrl" -ForegroundColor Green
}
catch {
    Write-Host "  ⚠️  Baserow may not be running at $BaseUrl" -ForegroundColor Yellow
    Write-Host "     Continuing anyway - some tests may fail" -ForegroundColor Yellow
}

# Run the security and accessibility tests
Write-Host ""
Write-Host "Starting Security and Accessibility Tests..." -ForegroundColor Green
Write-Host "This may take several minutes depending on the number of pages and tests." -ForegroundColor White
Write-Host ""

try {
    & $PythonCommand test_security_accessibility_comprehensive.py --url $BaseUrl --output $ReportFile --json
    $TestExitCode = $LASTEXITCODE
    
    if ($TestExitCode -eq 0) {
        Write-Host ""
        Write-Host "✅ All tests completed successfully!" -ForegroundColor Green
        $SuccessIcon = "✅"
    }
    else {
        Write-Host ""
        Write-Host "⚠️  Tests completed with some failures." -ForegroundColor Yellow
        $SuccessIcon = "⚠️"
    }
}
catch {
    Write-Host ""
    Write-Host "❌ Error running tests: $_" -ForegroundColor Red
    exit 1
}

# Generate summary
Write-Host ""
Write-Host "📊 Test Results Summary:" -ForegroundColor Blue

if (Test-Path $JsonFile) {
    $SummaryScript = @"
import json
import sys

try:
    with open('$($JsonFile.Replace('\', '\\'))', 'r') as f:
        results = json.load(f)
    
    summary = results['summary']
    
    print(f"  Total Tests: {summary['total_tests']}")
    print(f"  Passed: {summary['passed']} ✅")
    print(f"  Failed: {summary['failed']} ❌")
    print(f"  Skipped: {summary['skipped']} ⏭️")
    print(f"  Success Rate: {summary['success_rate']:.1f}%")
    print(f"  Duration: {summary['duration']:.2f} seconds")
    
    # Show critical failures
    failed_tests = [r for r in results['results'] if r['status'] == 'FAIL']
    security_failures = [t for t in failed_tests if any(keyword in t['test_name'] for keyword in ['password', 'session', 'permission', 'sql', 'xss', 'api'])]
    
    if security_failures:
        print(f"\n  🚨 Critical Security Issues: {len(security_failures)}")
        for test in security_failures[:3]:  # Show first 3
            print(f"    - {test['test_name']}: {test['message']}")
        if len(security_failures) > 3:
            print(f"    ... and {len(security_failures) - 3} more")
    
except Exception as e:
    print(f"Error reading results: {e}")
    sys.exit(1)
"@
    
    try {
        $SummaryScript | & $PythonCommand
    }
    catch {
        Write-Host "  ❌ Could not read results file" -ForegroundColor Red
    }
}
else {
    Write-Host "  ❌ Could not find results file" -ForegroundColor Red
}

# Show file locations
Write-Host ""
Write-Host "📄 Generated Reports:" -ForegroundColor Blue
Write-Host "  📋 Markdown Report: $ReportFile" -ForegroundColor White
if (Test-Path $JsonFile) {
    Write-Host "  📊 JSON Results: $JsonFile" -ForegroundColor White
}

# Open report if possible
if (Test-Path $ReportFile) {
    Write-Host ""
    Write-Host "Opening report in default application..." -ForegroundColor Yellow
    try {
        Start-Process $ReportFile
    }
    catch {
        Write-Host "Could not open report automatically. Please open manually: $ReportFile" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "$SuccessIcon Security and Accessibility Testing Complete!" -ForegroundColor Green
Write-Host "   View the detailed report at: $ReportFile" -ForegroundColor Blue

# Exit with appropriate code based on test results
if (Test-Path $JsonFile) {
    $FailedCountScript = @"
import json
try:
    with open('$($JsonFile.Replace('\', '\\'))', 'r') as f:
        results = json.load(f)
    print(results['summary']['failed'])
except:
    print('0')
"@
    
    try {
        $FailedCount = $FailedCountScript | & $PythonCommand
        if ([int]$FailedCount -gt 0) {
            exit 1
        }
    }
    catch {
        # If we can't read the results, assume success
    }
}

exit 0