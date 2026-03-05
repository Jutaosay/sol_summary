#!/usr/bin/env bash
set -euo pipefail

ROUND="${1:-round3}"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPORT_DIR="$PROJECT_DIR/reports"
mkdir -p "$REPORT_DIR"

cat <<EOF
[run_round] round=$ROUND
[run_round] project=$PROJECT_DIR
[run_round] policy:
  - require artifacts: code-$ROUND.md / test-report-$ROUND.md / review-$ROUND.md
  - missing artifact => FAILED
  - fallback: scripts/verify_round.sh $ROUND
EOF

# Intended use:
# 1) main dispatches code/check/test agents
# 2) they write required files under reports/
# 3) call verify_round.sh to fill missing reports and enforce non-empty outputs

"$PROJECT_DIR/scripts/verify_round.sh" "$ROUND"

echo "[run_round] summary files:"
ls -1 "$REPORT_DIR"/*"$ROUND".md 2>/dev/null || true
