# Test Report - sol_summary

- Time: 2026-03-05 15:55~15:56 (GMT+8)
- Tester: Test subagent
- Scope:
  1. Run `pytest` and summarize result
  2. Start API via `uvicorn`, call `/track/{ca}` for `E9SmMCvtLfitMwkLzkduwgN8ZYcfepiELLQ8d1SApump`
  3. Wait >=12s, fetch `/series?points=5` and `/latest`
  4. Record failures/anomalies and reproducible steps

## Environment Info

- Host: Linux (VM-0-4-ubuntu)
- Project: `/home/ubuntu/Codings/Projects/sol_summary`
- Python venv: `.venv`
- API bind: `127.0.0.1:8088`

## Commands Executed

```bash
# 1) pytest
source .venv/bin/activate && pytest -q

# 2) start api
source .venv/bin/activate && uvicorn src.api.app:app --host 127.0.0.1 --port 8088

# 3) start tracking
curl -sS -X POST http://127.0.0.1:8088/track/E9SmMCvtLfitMwkLzkduwgN8ZYcfepiELLQ8d1SApump

# 4) wait >=12s and query
sleep 13
curl -sS "http://127.0.0.1:8088/series/E9SmMCvtLfitMwkLzkduwgN8ZYcfepiELLQ8d1SApump?points=5"
curl -sS "http://127.0.0.1:8088/latest/E9SmMCvtLfitMwkLzkduwgN8ZYcfepiELLQ8d1SApump"

# 5) stop tracking
curl -sS -X POST http://127.0.0.1:8088/stop/E9SmMCvtLfitMwkLzkduwgN8ZYcfepiELLQ8d1SApump
```

## Key Outputs

### 1) pytest result

```text
ERROR collecting tests/test_stats.py
ModuleNotFoundError: No module named 'src'

1 error in 0.14s
(exit code 2)
```

### 2) API /track + /series + /latest

`POST /track`:

```json
{"ok":true,"tracking":true,"ca":"E9SmMCvtLfitMwkLzkduwgN8ZYcfepiELLQ8d1SApump","poll_seconds":5}
```

`GET /series?points=5`:

```json
[
  {"ts":"2026-03-05 07:55:59","holder_count_total":8,"top50_sum_raw":766129.93383,"top50_sum_trimmed":619.1546549999999},
  {"ts":"2026-03-05 07:56:04","holder_count_total":0,"top50_sum_raw":0.0,"top50_sum_trimmed":0.0},
  {"ts":"2026-03-05 07:56:09","holder_count_total":0,"top50_sum_raw":0.0,"top50_sum_trimmed":0.0},
  {"ts":"2026-03-05 07:56:14","holder_count_total":0,"top50_sum_raw":0.0,"top50_sum_trimmed":0.0},
  {"ts":"2026-03-05 07:56:19","holder_count_total":0,"top50_sum_raw":0.0,"top50_sum_trimmed":0.0}
]
```

`GET /latest`:

```json
{"ts":"2026-03-05 07:56:19","holder_count_total":0,"top50_sum_raw":0.0,"top50_avg_raw":0.0,"top50_sum_trimmed":0.0,"top50_avg_trimmed":0.0,"top50_count":0,"trimmed_count":0,"sample_ok":1,"err_msg":null}
```

## Test Case Results

- [FAIL] TC-01 `pytest` should collect and execute tests successfully
  - Actual: collection failed with `ModuleNotFoundError: No module named 'src'`
- [PASS_WITH_ISSUE] TC-02 API can start and accept `/track`
  - `/track` returned success
- [FAIL] TC-03 after >=12s, series/latest should provide stable non-zero data points for tracked CA
  - Actual: first point non-zero, subsequent points became all-zero (`holder_count_total=0`, `top50_sum_raw=0.0` etc.)

## Failure / Anomaly Evidence & Reproduction

### A) pytest import failure

**Repro steps**:
1. `cd /home/ubuntu/Codings/Projects/sol_summary`
2. `source .venv/bin/activate`
3. `pytest -q`

**Observed**: `ModuleNotFoundError: No module named 'src'`

### B) Runtime sampling anomaly (0-point issue)

**Repro steps**:
1. Start API: `uvicorn src.api.app:app --host 127.0.0.1 --port 8088`
2. Track target CA via `/track`
3. Wait at least 12 seconds (here: 13s)
4. Query `/series/{ca}?points=5` and `/latest/{ca}`

**Observed**:
- First sample had non-zero values, later samples turned to all zeros
- `sample_ok=1` with `err_msg=null`, but statistical fields became zero

## Final Conclusion

**FAIL**

Reasons:
1. Automated tests (`pytest`) do not run due to import/packaging path issue.
2. Live sampling shows instability/anomaly (0-point series after initial non-zero point), affecting data reliability.

## Suggested Regression Checklist

1. Fix test import path/package setup, then rerun full `pytest`.
2. Re-verify continuous sampling for this CA and at least one additional CA over >=1 minute.
3. Confirm behavior when RPC returns empty/partial data and ensure `sample_ok` semantics match output validity.
4. Validate `/latest` and `/series` consistency (non-contradictory status vs values).
