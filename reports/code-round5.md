# Code Report (round5)

- Time: 2026-03-05T20:49:22
- Scope: multi-RPC fallback + degraded/hint API/web

## Delivered
1. `SOL_RPC_URLS` 支持（逗号分隔）并在 collector 中按候选RPC顺序回退。
2. RPC调用改为：单RPC重试+退避，失败后切下一RPC。
3. `/latest` 增加：`latest_sample_ok`, `degraded`, `hint`。
4. `/metrics` 增加：`degraded`, `status`（ok/rpc_limited）, `hint`（默认过滤导致空时）。
5. 前端状态栏展示 degraded/hint，避免“空图无解释”。

## Files
- src/sol_summary/config.py
- src/sol_summary/collector.py
- src/sol_summary/api.py
- web/index.html
- README.md
