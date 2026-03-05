# Check Round5 Report

- Time: 2026-03-05T18:35:12
- CA: E9SmMCvtLfitMwkLzkduwgN8ZYcfepiELLQ8d1SApump
- Success rounds (metrics default has data): 0/5
- Failed rounds: 5/5
- Avg elapsed: 10.02s

## Per-round
- R1: track=200 latest=200 metrics=200 all=200 ok_items=0 all_items=5 latest_sample_ok=0 holder=0 err=rpc failed method=getTokenLargestAccounts rpc=https://api.mainnet-beta.solana.com attempts=5: rpc rate limited (HTTP 429
- R2: track=200 latest=200 metrics=200 all=200 ok_items=0 all_items=5 latest_sample_ok=0 holder=0 err=rpc failed method=getTokenLargestAccounts rpc=https://api.mainnet-beta.solana.com attempts=5: rpc rate limited (HTTP 429
- R3: track=200 latest=200 metrics=200 all=200 ok_items=0 all_items=5 latest_sample_ok=0 holder=0 err=rpc failed method=getTokenLargestAccounts rpc=https://api.mainnet-beta.solana.com attempts=5: rpc rate limited (HTTP 429
- R4: track=200 latest=200 metrics=200 all=200 ok_items=0 all_items=5 latest_sample_ok=0 holder=0 err=rpc failed method=getTokenLargestAccounts rpc=https://api.mainnet-beta.solana.com attempts=5: rpc rate limited (HTTP 429
- R5: track=200 latest=200 metrics=200 all=200 ok_items=0 all_items=5 latest_sample_ok=0 holder=0 err=rpc failed method=getTokenLargestAccounts rpc=https://api.mainnet-beta.solana.com attempts=5: rpc rate limited (HTTP 429

## Review
- 结论：公共RPC下稳定性不足，绝大多数轮次为失败样本（429限流）。
- 优化建议：优先接入私有RPC或RPC池；增加降级提示与观测面板。
