# Round3 Test Report

- CA: E9SmMCvtLfitMwkLzkduwgN8ZYcfepiELLQ8d1SApump

## Pytest Output
....                                                                     [100%]
4 passed in 0.03s

## HTTP Checks
- /metrics?limit=0 => 400
- /metrics?limit=2001 => 400
- /metrics?limit=120 => 200
- POST /track => 200
- GET /latest => 200
- GET /metrics?limit=5 => 200
- GET /metrics?limit=5&include_failed=true => 200
- holder_count_is_estimate present => yes

## Snippets
- latest: {"id":6,"ca":"E9SmMCvtLfitMwkLzkduwgN8ZYcfepiELLQ8d1SApump","ts":1772705234,"holder_count":0,"top50_count":0,"top50_total_raw":0.0,"trimmed_count":0,"trimmed_total":0.0,"trimmed_avg":0.0,"trimmed_median":0.0,"trimmed_min":0.0,"trimmed_max":0.0,"top50_raw_json"
- metrics: {"ca":"E9SmMCvtLfitMwkLzkduwgN8ZYcfepiELLQ8d1SApump","items":[]}
- metrics_all: {"ca":"E9SmMCvtLfitMwkLzkduwgN8ZYcfepiELLQ8d1SApump","items":[{"id":4,"ca":"E9SmMCvtLfitMwkLzkduwgN8ZYcfepiELLQ8d1SApump","ts":1772705181,"holder_count":0,"top50_count":0,"top50_total_raw":0.0,"trimmed_count":0,"trimmed_total":0.0,"trimmed_avg":0.0,"trimmed_me

## Conclusion
- PASS 条件：pytest通过 + limit边界正确 + estimate字段存在。
