/**
 * Playwright Configuration for Security and Accessibility Testing
 * 
 * Specialized configuration for running security and accessibility tests
 * across multiple browsers and devices with appropriate timeouts and settings.
 */

import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests',
  
  // Test files for security and accessibility
  testMatch: [
    '**/accessibility-comprehensive.spec.js',
    '**/cross-browser-compatibility.spec.ts',
    '**/mobile-responsiveness.spec.ts'
  ],
  
  // Global test timeout
  timeout: 60000,
  
  // Expect timeout for assertions
  expect: {
    timeout: 10000
  },
  
  // Fail the build on CI if you accidentally left test.only in the source code
  forbidOnly: !!process.env.CI,
  
  // Retry on CI only
  retries: process.env.CI ? 2 : 0,
  
  // Opt out of parallel tests for more stable results
  workers: process.env.CI ? 1 : undefined,
  
  // Reporter configuration
  reporter: [
    ['html', { outputFolder: 'test-results/html-report' }],
    ['json', { outputFile: 'test-results/results.json' }],
    ['junit', { outputFile: 'test-results/junit.xml' }],
    ['list']
  ],
  
  // Global setup and teardown
  globalSetup: require.resolve('./global-setup'),
  globalTeardown: require.resolve('./global-teardown'),
  
  // Shared settings for all projects
  use: {
    // Base URL for tests
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    
    // Collect trace when retrying the failed test
    trace: 'on-first-retry',
    
    // Record video on failure
    video: 'retain-on-failure',
    
    // Take screenshot on failure
    screenshot: 'only-on-failure',
    
    // Ignore HTTPS errors
    ignoreHTTPSErrors: true,
    
    // Accept downloads
    acceptDownloads: true,
    
    // Viewport size
    viewport: { width: 1280, height: 720 },
    
    // User agent
    userAgent: 'Baserow-Test-Agent/1.0',
    
    // Permissions
    permissions: ['camera', 'microphone', 'notifications'],
    
    // Geolocation
    geolocation: { longitude: 12.492507, latitude: 41.889938 },
    
    // Locale
    locale: 'en-US',
    
    // Timezone
    timezoneId: 'America/New_York',
    
    // Color scheme
    colorScheme: 'light'
  },

  // Configure projects for major browsers and devices
  projects: [
    // Desktop browsers
    {
      name: 'chromium',
      use: { 
        ...devices['Desktop Chrome'],
        // Enable accessibility tree snapshots
        launchOptions: {
          args: ['--enable-accessibility-logging']
        }
      },
    },
    
    {
      name: 'firefox',
      use: { 
        ...devices['Desktop Firefox'],
        // Firefox-specific settings
        launchOptions: {
          firefoxUserPrefs: {
            'accessibility.force_disabled': 0
          }
        }
      },
    },
    
    {
      name: 'webkit',
      use: { 
        ...devices['Desktop Safari'],
        // Safari-specific settings
        launchOptions: {
          args: ['--enable-accessibility']
        }
      },
    },
    
    // Mobile devices for responsiveness testing
    {
      name: 'Mobile Chrome',
      use: { 
        ...devices['Pixel 5'],
        // Mobile-specific settings
        hasTouch: true,
        isMobile: true
      },
    },
    
    {
      name: 'Mobile Safari',
      use: { 
        ...devices['iPhone 12'],
        hasTouch: true,
        isMobile: true
      },
    },
    
    // Tablet devices
    {
      name: 'iPad',
      use: { 
        ...devices['iPad Pro'],
        hasTouch: true,
        isMobile: false
      },
    },
    
    // High contrast mode testing
    {
      name: 'chromium-high-contrast',
      use: {
        ...devices['Desktop Chrome'],
        colorScheme: 'dark',
        forcedColors: 'active',
        launchOptions: {
          args: [
            '--enable-accessibility-logging',
            '--force-prefers-color-scheme=dark',
            '--enable-features=ForcedColors'
          ]
        }
      },
    },
    
    // Reduced motion testing
    {
      name: 'chromium-reduced-motion',
      use: {
        ...devices['Desktop Chrome'],
        reducedMotion: 'reduce',
        launchOptions: {
          args: ['--enable-accessibility-logging']
        }
      },
    },
    
    // Screen reader simulation
    {
      name: 'chromium-screen-reader',
      use: {
        ...devices['Desktop Chrome'],
        launchOptions: {
          args: [
            '--enable-accessibility-logging',
            '--enable-screen-reader'
          ]
        }
      },
    }
  ],

  // Web server configuration for local testing
  webServer: process.env.CI ? undefined : {
    command: 'npm run dev',
    port: 3000,
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },
  
  // Test output directory
  outputDir: 'test-results/',
  
  // Global test configuration
  globalTimeout: 600000, // 10 minutes for all tests
  
  // Metadata for test reporting
  metadata: {
    testType: 'Security and Accessibility',
    environment: process.env.NODE_ENV || 'test',
    version: process.env.npm_package_version || '1.0.0'
  }
})