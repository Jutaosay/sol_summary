# Review Report (round4)

- Time: 2026-03-05T20:33:17+08:00

## Review Summary
1. 代码基础能力（参数校验、失败样本落库、estimate 标记）已具备。
2. 主要瓶颈为外部依赖：公共 Solana RPC 429 限流，导致默认 metrics 经常为空。
3. 当前默认行为虽合理（过滤失败样本），但在全失败场景下用户观感为“无数据”。

## Risk Level
- High: 公共RPC 429 导致高失败率，影响可用性。
- Medium: 缺少多RPC池回退与降级提示字段。
- Low: 旧目录残留仍可能造成维护歧义。

## Verdict
- NEED_FIX

## Action Items
- 引入 SOL_RPC_URLS 多RPC回退
- /latest 与 /metrics 增强 degraded/hint 可观测字段
- 增加 8~10 轮长测为发布前门禁
