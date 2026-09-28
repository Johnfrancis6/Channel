import { defineConfig, devices } from '@playwright/test';

// Dans un conteneur où Chromium est préinstallé ailleurs (ex. /opt/pw-browsers/chromium).
const executablePath = process.env.CHROMIUM_PATH || undefined;

export default defineConfig({
  testDir: 'tests/e2e',
  timeout: 10 * 60 * 1000,
  reporter: [['list']],
  use: {
    baseURL: 'http://localhost:5173',
    launchOptions: { executablePath },
  },
  projects: [{ name: 'iphone', use: { ...devices['iPhone 13'], defaultBrowserType: 'chromium', launchOptions: { executablePath } } }],
  webServer: {
    command: 'npm run vendor && npx vite --port 5173 --strictPort',
    url: 'http://localhost:5173',
    reuseExistingServer: true,
    timeout: 120 * 1000,
  },
});
