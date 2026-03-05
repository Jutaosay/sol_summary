#!/usr/bin/env bash
set -euo pipefail

ROUND="${1:-round3}"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPORT_DIR="$PROJECT_DIR/reports"
mkdir -p "$REPORT_DIR"

CODE_REPORT="$REPORT_DIR/code-${ROUND}.md"
TEST_REPORT="$REPORT_DIR/test-report-${ROUND}.md"
REVIEW_REPORT="$REPORT_DIR/review-${ROUND}.md"

log() { echo "[verify_round] $*"; }

# 1) Test fallback
if [[ ! -f "$TEST_REPORT" ]]; then
  log "missing $TEST_REPORT -> generating fallback test report"
  {
    echo "# Test Report ($ROUND)"
    echo
    echo "- GeneratedBy: verify_round.sh fallback"
    echo "- Time: $(date -Iseconds)"
    echo
    cd "$PROJECT_DIR"
    if [[ -x ".venv/bin/pytest" ]]; then
      set +e
      PYTHONPATH=. .venv/bin/pytest -q > "$REPORT_DIR/.pytest-${ROUND}.log" 2>&1
      RC=$?
      set -e
      echo "## Pytest"
      echo "- Command: PYTHONPATH=. .venv/bin/pytest -q"
      echo "- ExitCode: $RC"
      echo "- Log: reports/.pytest-${ROUND}.log"
      echo
      if [[ $RC -eq 0 ]]; then
        echo "- Result: PASS"
      else
        echo "- Result: FAIL"
      fi
    else
      echo "## Pytest"
      echo "- Result: FAIL"
      echo "- Reason: .venv/bin/pytest not found"
    fi
  } > "$TEST_REPORT"
fi

# 2) Review fallback
if [[ ! -f "$REVIEW_REPORT" ]]; then
  log "missing $REVIEW_REPORT -> generating fallback review report"
  {
    echo "# Review Report ($ROUND)"
    echo
    echo "- GeneratedBy: verify_round.sh fallback"
    echo "- Time: $(date -Iseconds)"
    echo
    echo "## Quick Checks"
    if grep -q "RLock" "$PROJECT_DIR/src/sol_summary/storage.py" 2>/dev/null; then
      echo "- [PASS] storage.py contains RLock"
    else
      echo "- [NEED_FIX] storage.py missing RLock"
    fi

    if grep -q "limit must be in \[1, 2000\]" "$PROJECT_DIR/src/sol_summary/api.py" 2>/dev/null; then
      echo "- [PASS] api.py has limit range validation"
    else
      echo "- [NEED_FIX] api.py missing limit range validation"
    fi

    if grep -q "holder_count_is_estimate" "$PROJECT_DIR/src/sol_summary/api.py" 2>/dev/null; then
      echo "- [PASS] api.py exposes holder_count_is_estimate"
    else
      echo "- [NEED_FIX] holder_count_is_estimate not found"
    fi

    echo
    echo "## Conclusion"
    echo "- If any NEED_FIX above, overall = NEED_FIX"
  } > "$REVIEW_REPORT"
fi

# 3) Code report fallback
if [[ ! -f "$CODE_REPORT" ]]; then
  log "missing $CODE_REPORT -> generating fallback code report"
  {
    echo "# Code Report ($ROUND)"
    echo
    echo "- GeneratedBy: verify_round.sh fallback"
    echo "- Time: $(date -Iseconds)"
    echo
    echo "## Files Snapshot"
    echo '```'
    (cd "$PROJECT_DIR" && find src/sol_summary -maxdepth 2 -type f | sort)
    echo '```'
  } > "$CODE_REPORT"
fi

log "done"
printf 'ARTIFACT_OK %s\n' "$CODE_REPORT"
printf 'ARTIFACT_OK %s\n' "$TEST_REPORT"
printf 'ARTIFACT_OK %s\n' "$REVIEW_REPORT"
