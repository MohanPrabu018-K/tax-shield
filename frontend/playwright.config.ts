import { defineConfig, devices } from '@playwright/test';

/**
 * TaxShield browser suite. CI must provide:
 *  - MongoDB at $TAXSHIELD_MONGODB_URL (default mongodb://localhost:27017)
 *  - backend on :8000 (uvicorn app.main:app)
 *  - frontend via webServer below (:3000)
 * Desktop + mobile viewports. No paid services.
 */
export default defineConfig({
  testDir: './tests',
  fullyParallel: false,
  retries: process.env.CI ? 1 : 0,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: process.env.TAXSHIELD_FRONTEND_URL || 'http://localhost:3000',
    trace: 'retain-on-failure',
  },
  projects: [
    { name: 'desktop', use: { ...devices['Desktop Chrome'] } },
    { name: 'mobile', use: { ...devices['Pixel 7'] } },
    // Cross-browser runs: PLAYWRIGHT_FIREFOX=1 / PLAYWRIGHT_WEBKIT=1
    ...(process.env.PLAYWRIGHT_FIREFOX
      ? [{ name: 'firefox', use: { ...devices['Desktop Firefox'] } }]
      : []),
    ...(process.env.PLAYWRIGHT_WEBKIT
      ? [{ name: 'webkit', use: { ...devices['Desktop Safari'] } }]
      : []),
  ],
  webServer: {
    command: 'npm run dev',
    port: 3000,
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
    env: {
      NEXT_PUBLIC_API_URL: process.env.TAXSHIELD_API_URL || 'http://localhost:8000/api',
    },
  },
});
