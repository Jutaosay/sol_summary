#!/usr/bin/env bash
set -u

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPORT_DIR="$ROOT_DIR/reports"
RUN_LOG="$REPORT_DIR/e2e-run.log"
SUMMARY_MD="$REPORT_DIR/e2e-summary.md"
CMD="npx playwright test"

mkdir -p "$REPORT_DIR"

{
  echo "[run] $(date -Iseconds)"
  echo "[cmd] $CMD"
} > "$RUN_LOG"

cd "$ROOT_DIR" || exit 1

if [ ! -d node_modules ]; then
  echo "[setup] npm install" | tee -a "$RUN_LOG"
  npm install >> "$RUN_LOG" 2>&1
fi

echo "[setup] playwright install chromium" | tee -a "$RUN_LOG"
npx playwright install chromium >> "$RUN_LOG" 2>&1

echo "[exec] $CMD" | tee -a "$RUN_LOG"
$CMD >> "$RUN_LOG" 2>&1
EXIT_CODE=$?

echo "[result] exit_code=$EXIT_CODE" | tee -a "$RUN_LOG"

{
  echo ""
  echo "## Run command"
  echo "- $CMD"
  echo "## Final result"
  if [ "$EXIT_CODE" -eq 0 ]; then
    echo "- PASS"
  else
    echo "- FAIL"
  fi
  echo "## Artifacts"
  echo "- run log: reports/e2e-run.log"
  echo "- playwright json: reports/playwright-results.json"
  echo "- playwright html: reports/playwright-html/index.html"
} >> "$SUMMARY_MD"

exit "$EXIT_CODE"
