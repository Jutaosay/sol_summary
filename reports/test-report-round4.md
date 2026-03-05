# Test Report (round4)

- Time: 2026-03-05T20:33:17+08:00
- CA: E9SmMCvtLfitMwkLzkduwgN8ZYcfepiELLQ8d1SApump

## Pytest
- Command: PYTHONPATH=. .venv/bin/pytest -q
- ExitCode: 0
- Log: reports/.pytest-round4.log

## API Smoke
- /metrics?limit=0 => 400
- /metrics?limit=120 => 200
- POST /track => 200
- GET /latest => 200
- GET /metrics?limit=5 => 200
- GET /metrics?limit=5&include_failed=true => 200
- holder_count_is_estimate present => yes

## Snippets
- latest: {"id":17,"ca":"E9SmMCvtLfitMwkLzkduwgN8ZYcfepiELLQ8d1SApump","ts":1772713985,"holder_count":0,"top50_count":0,"top50_total_raw":0.0,"trimmed_count":0,"trimmed_total":0.0,"trimmed_avg":0.0,"trimmed_median":0.0,"trimmed_mi
- metrics: {"ca":"E9SmMCvtLfitMwkLzkduwgN8ZYcfepiELLQ8d1SApump","items":[]}
- metrics_all: {"ca":"E9SmMCvtLfitMwkLzkduwgN8ZYcfepiELLQ8d1SApump","items":[{"id":13,"ca":"E9SmMCvtLfitMwkLzkduwgN8ZYcfepiELLQ8d1SApump","ts":1772706868,"holder_count":0,"top50_count":0,"top50_total_raw":0.0,"trimmed_count":0,"trimmed

## Conclusion
- NEED_FIX（公共RPC下采样可靠性不足，常见 sample_ok=0 / 429）
