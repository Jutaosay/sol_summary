const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

const REPORT_DIR = path.resolve(__dirname, '../../reports');
const REPORT_PATH = path.join(REPORT_DIR, 'e2e-summary.md');
const CA = 'E9SmMCvtLfitMwkLzkduwgN8ZYcfepiELLQ8d1SApump';

function ensureReportDir() {
  fs.mkdirSync(REPORT_DIR, { recursive: true });
}

function appendReport(lines) {
  ensureReportDir();
  fs.appendFileSync(REPORT_PATH, lines.join('\n') + '\n', 'utf8');
}

test.beforeAll(() => {
  ensureReportDir();
  fs.writeFileSync(
    REPORT_PATH,
    [
      '# Playwright E2E Report',
      '',
      `- Started: ${new Date().toISOString()}`,
      `- CA: ${CA}`,
      ''
    ].join('\n'),
    'utf8'
  );
});

test('page loads and tracking refreshes every ~5s with diagnostic conclusion', async ({ page }) => {
  const consoleLogs = [];
  const networkLogs = [];
  const metricsRequests = [];
  const trackRequests = [];

  page.on('console', (msg) => {
    const line = `[console][${msg.type()}] ${msg.text()}`;
    consoleLogs.push(line);
  });

  page.on('request', (req) => {
    const url = req.url();
    if (url.includes('/metrics?')) {
      metricsRequests.push({ ts: Date.now(), method: req.method(), url });
    }
    if (url.endsWith('/track')) {
      trackRequests.push({ ts: Date.now(), method: req.method(), url, body: req.postData() || '' });
    }
    networkLogs.push(`[request] ${req.method()} ${url}`);
  });

  page.on('response', async (resp) => {
    const url = resp.url();
    if (url.includes('/metrics?')) {
      let body = '';
      try {
        body = await resp.text();
      } catch {}
      networkLogs.push(`[response] ${resp.status()} ${url} body=${body.slice(0, 300)}`);
    } else if (url.endsWith('/track')) {
      let body = '';
      try {
        body = await resp.text();
      } catch {}
      networkLogs.push(`[response] ${resp.status()} ${url} body=${body.slice(0, 300)}`);
    }
  });

  await page.goto('/');

  await expect(page.getByRole('button', { name: '开始追踪' })).toBeVisible();
  await page.locator('#ca').fill(CA);
  await page.getByRole('button', { name: '开始追踪' }).click();

  await expect.poll(() => trackRequests.length, { timeout: 10_000 }).toBeGreaterThan(0);

  // Wait long enough for at least 3 refresh cycles (initial + interval polls)
  await expect.poll(() => metricsRequests.length, { timeout: 22_000 }).toBeGreaterThanOrEqual(3);

  const intervals = [];
  for (let i = 1; i < metricsRequests.length; i += 1) {
    intervals.push(metricsRequests[i].ts - metricsRequests[i - 1].ts);
  }

  const near5s = intervals.filter((ms) => ms >= 3500 && ms <= 7000).length;

  // Pull latest metrics to decide if chart data has points.
  const metricsResp = await page.request.get(`/metrics?ca=${encodeURIComponent(CA)}&limit=120`);
  expect(metricsResp.ok()).toBeTruthy();
  const metricsJson = await metricsResp.json();
  const items = metricsJson.items || [];

  let conclusion = '';
  let pass = false;
  const hasRequests = metricsRequests.length > 0;
  const hasData = items.length > 0;

  if (hasRequests && hasData) {
    const first = items[0];
    const hasRenderableFields =
      first &&
      Object.prototype.hasOwnProperty.call(first, 'holder_count') &&
      Object.prototype.hasOwnProperty.call(first, 'trimmed_avg') &&
      Object.prototype.hasOwnProperty.call(first, 'top50_total_raw');

    expect(hasRenderableFields).toBeTruthy();
    expect(near5s).toBeGreaterThan(0);
    pass = true;
    conclusion = 'PASS：检测到定时请求且已有可渲染图表数据。';
  } else if (hasRequests && !hasData) {
    conclusion = 'FAIL（可诊断）：有请求但无数据，疑似 RPC 限流或上游无可用数据。';
  } else {
    conclusion = 'FAIL：未检测到刷新请求。';
  }

  appendReport([
    '## Test: tracking refresh and chart diagnostics',
    '',
    `- metrics request count: ${metricsRequests.length}`,
    `- track request count: ${trackRequests.length}`,
    `- refresh intervals(ms): ${intervals.join(', ') || 'N/A'}`,
    `- near 5s intervals count: ${near5s}`,
    `- data points returned: ${items.length}`,
    `- conclusion: ${conclusion}`,
    '',
    '### Console logs',
    ...((consoleLogs.length ? consoleLogs : ['(none)']).map((l) => `- ${l}`)),
    '',
    '### Network logs (excerpt)',
    ...networkLogs.slice(0, 80).map((l) => `- ${l}`),
    ''
  ]);

  expect(pass, conclusion).toBeTruthy();
});
