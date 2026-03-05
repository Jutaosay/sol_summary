# Test Report (round5)

- Time: 2026-03-05T20:49:22
- CA: E9SmMCvtLfitMwkLzkduwgN8ZYcfepiELLQ8d1SApump

## Pytest
```text
....                                                                     [100%]
4 passed in 0.03s

```

## API Result
- /track: {"ok":true,"ca":"E9SmMCvtLfitMwkLzkduwgN8ZYcfepiELLQ8d1SApump","started":true,"tracking":["E9SmMCvtLfitMwkLzkduwgN8ZYcfepiELLQ8d1SApump"]}
- /latest: {'id': 18, 'ca': 'E9SmMCvtLfitMwkLzkduwgN8ZYcfepiELLQ8d1SApump', 'ts': 1772714950, 'holder_count': 0, 'top50_count': 0, 'top50_total_raw': 0.0, 'trimmed_count': 0, 'trimmed_total': 0.0, 'trimmed_avg': 0.0, 'trimmed_median': 0.0, 'trimmed_min': 0.0, 'trimmed_max': 0.0, 'top50_raw_json': '[]', 'trimmed_json': '[]', 'sample_ok': 0, 'err_msg': 'all rpc candidates failed for getTokenLargestAccounts: rpc failed method=getTokenLargestAccounts rpc=https://api.mainnet-beta.solana.com attempts=5: rpc rate limited (HTTP 429), method=getTokenLargestAccounts, rpc=https://api.mainnet-beta.solana.com, attempt=5/5, backoff=8.00s', 'holder_count_is_estimate': True, 'latest_sample_ok': False, 'degraded': True, 'hint': 'latest sample failed; try include_failed=true or switch to private RPC/SOL_RPC_URLS'}
- /metrics: {'ca': 'E9SmMCvtLfitMwkLzkduwgN8ZYcfepiELLQ8d1SApump', 'items': [], 'degraded': True, 'status': 'rpc_limited', 'hint': 'no successful samples in current window; retry with include_failed=true or configure private RPC/SOL_RPC_URLS'}
- /metrics(include_failed=true): {'ca': 'E9SmMCvtLfitMwkLzkduwgN8ZYcfepiELLQ8d1SApump', 'items': [{'id': 14, 'ca': 'E9SmMCvtLfitMwkLzkduwgN8ZYcfepiELLQ8d1SApump', 'ts': 1772706879, 'holder_count': 0, 'top50_count': 0, 'top50_total_raw': 0.0, 'trimmed_count': 0, 'trimmed_total': 0.0, 'trimmed_avg': 0.0, 'trimmed_median': 0.0, 'trimmed_min': 0.0, 'trimmed_max': 0.0, 'top50_raw_json': '[]', 'trimmed_json': '[]', 'sample_ok': 0, 'err_msg': 'rpc failed method=getTokenLargestAccounts rpc=https://api.mainnet-beta.solana.com attempts=5: rpc rate limited (HTTP 429), method=getTokenLargestAccounts, rpc=https://api.mainnet-beta.solana.com, attempt=5/5, backoff=8.00s', 'holder_count_is_estimate': True}, {'id': 15, 'ca': 'E9SmMCvtLfitMwkLzkduwgN8ZYcfepiELLQ8d1SApump', 'ts': 1772706890, 'holder_count': 0, 'top50_count': 0, 'top50_total_raw': 0.0, 'trimmed_count': 0, 'trimmed_total': 0.0, 'trimmed_avg': 0.0, 'trimmed_median': 0.0, 'trimmed_min': 0.0, 'trimmed_max': 0.0, 'top50_raw_json': '[]', 'trimmed_json': '[]', 'sample_ok': 0, 'err_msg': 'rpc failed method=getTokenLargestAccounts rpc=https://api.mainnet-beta.solana.com attempts=5: rpc rate limited (HTTP 429), method=getTokenLargestAccounts, rpc=https://api.mainnet-beta.solana.com, attempt=5/5, backoff=8.00s', 'holder_count_is_estimate': True}, {'id': 16, 'ca': 'E9SmMCvtLfitMwkLzkduwgN8ZYcfepiELLQ8d1SApump', 'ts': 1772706901, 'holder_count': 0, 'top50_count': 0, 'top50_total_raw': 0.0, 'trimmed_count': 0, 'trimmed_total': 0.0, 'trimmed_avg': 0.0, 'trimmed_median': 0.0, 'trimmed_min': 0.0, 'trimmed_max': 0.0, 'top50_raw_json': '[]', 'trimmed_json': '[]', 'sample_ok': 0, 'err_msg': 'rpc failed method=getTokenLargestAccounts rpc=https://api.mainnet-beta.solana.com attempts=5: rpc rate limited (HTTP 429), method=getTokenLargestAccounts, rpc=https://api.mainnet-beta.solana.com, attempt=5/5, backoff=8.00s', 'holder_count_is_estimate': True}, {'id': 17, 'ca': 'E9SmMCvtLfitMwkLzkduwgN8ZYcfepiELLQ8d1SApump', 'ts': 1772713985, 'holder_count': 0, 'top50_count': 0, 'top50_total_raw': 0.0, 'trimmed_count': 0, 'trimmed_total': 0.0, 'trimmed_avg': 0.0, 'trimmed_median': 0.0, 'trimmed_min': 0.0, 'trimmed_max': 0.0, 'top50_raw_json': '[]', 'trimmed_json': '[]', 'sample_ok': 0, 'err_msg': 'rpc failed method=getTokenLargestAccounts rpc=https://api.mainnet-beta.solana.com attempts=5: rpc rate limited (HTTP 429), method=getTokenLargestAccounts, rpc=https://api.mainnet-beta.solana.com, attempt=5/5, backoff=8.00s', 'holder_count_is_estimate': True}, {'id': 18, 'ca': 'E9SmMCvtLfitMwkLzkduwgN8ZYcfepiELLQ8d1SApump', 'ts': 1772714950, 'holder_count': 0, 'top50_count': 0, 'top50_total_raw': 0.0, 'trimmed_count': 0, 'trimmed_total': 0.0, 'trimmed_avg': 0.0, 'trimmed_median': 0.0, 'trimmed_min': 0.0, 'trimmed_max': 0.0, 'top50_raw_json': '[]', 'trimmed_json': '[]', 'sample_ok': 0, 'err_msg': 'all rpc candidates failed for getTokenLargestAccounts: rpc failed method=getTokenLargestAccounts rpc=https://api.mainnet-beta.solana.com attempts=5: rpc rate limited (HTTP 429), method=getTokenLargestAccounts, rpc=https://api.mainnet-beta.solana.com, attempt=5/5, backoff=8.00s', 'holder_count_is_estimate': True}], 'degraded': True, 'status': 'rpc_limited'}

## Assertions
- latest contains degraded/latest_sample_ok/hint: yes
- metrics contains degraded/status: yes
- metrics may include hint when default items empty with failed samples: yes

## Conclusion
- PASS（功能已交付；公共RPC下仍可能 degraded=true，属于预期降级路径）
