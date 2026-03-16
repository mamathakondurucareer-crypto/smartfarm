// @ts-check
const { defineConfig, devices } = require("@playwright/test");

/**
 * SmartFarm Playwright configuration.
 *
 * Runs E2E tests in Chrome and Safari (WebKit) headless mode.
 *
 * Prerequisites:
 *   docker compose up -d
 *   OR
 *   1. Backend:  uvicorn backend.main:app --port 8000
 *   2. Frontend: cd mobile && npx expo start --web --port 8081
 *   3. Seed DB:  python3 -m backend.seeds.seed_data
 */
module.exports = defineConfig({
  testDir: "./tests",
  timeout: 30_000,
  expect: { timeout: 8_000 },

  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : 2,

  reporter: [
    ["list"],
    ["html", { outputFolder: "playwright-report", open: "never" }],
    ["json", { outputFile: "test-results/results.json" }],
  ],

  use: {
    baseURL: process.env.APP_URL || "http://localhost:8081",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
    headless: true,
  },

  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
    {
      name: "webkit",
      use: { ...devices["Desktop Safari"] },
    },
  ],
});
