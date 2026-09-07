/* global require, module */
const { defineConfig, devices } = require("@playwright/test");

module.exports = defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  retries: 1,
  workers: 1,
  use: {
    baseURL: "http://127.0.0.1:4173",
    trace: "on-first-retry",
  },
  webServer: {
    // PWA SW enabled for US-MOB-002 project only; other projects block service workers
    // so Playwright route stubs are not intercepted.
    command: "VITE_PWA_DEV=true npm run dev -- --host 127.0.0.1 --port 4173",
    url: "http://127.0.0.1:4173",
    reuseExistingServer: true,
    timeout: 120000,
  },
  projects: [
    {
      name: "chromium",
      testIgnore: /us-mob-002-pwa\.spec\.js/,
      use: {
        ...devices["Desktop Chrome"],
        serviceWorkers: "block",
      },
    },
    {
      name: "chromium-pwa",
      testMatch: /us-mob-002-pwa\.spec\.js/,
      use: {
        ...devices["Desktop Chrome"],
        serviceWorkers: "allow",
      },
    },
  ],
});
