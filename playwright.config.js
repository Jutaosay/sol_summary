// @ts-check
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests/e2e',
  timeout: 60_000,
  expect: { timeout: 10_000 },
  retries: 0,
  reporter: [
    ['list'],
    ['json', { outputFile: 'reports/playwright-results.json' }],
    ['html', { outputFolder: 'reports/playwright-html', open: 'never' }]
  ],
  use: {
    baseURL: 'http://127.0.0.1:8787',
    headless: true,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure'
  },
  webServer: {
    command: 'bash -lc "source .venv/bin/activate && PYTHONPATH=src python -m uvicorn sol_summary.api:app --host 127.0.0.1 --port 8787"',
    url: 'http://127.0.0.1:8787/',
    reuseExistingServer: true,
    timeout: 120_000
  }
});
