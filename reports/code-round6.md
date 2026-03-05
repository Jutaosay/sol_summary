# Code Report (round6)

- Scope: UI/UX 优化（web）
- File: `web/index.html`

## Delivered
1. 新增卡片化布局与状态 badge（正常/降级/错误）。
2. 新增 KPI 面板：点位数、latest holder_count、trimmed_avg、top50_total_raw。
3. 新增交互：
   - 立即刷新按钮
   - 刷新间隔选择（3s/5s/10s）
   - 展示失败样本开关（include_failed）
   - 复制 CA 按钮
4. 在 degraded/hint 场景显示明确文案，避免“空图无解释”。

## Compatibility
- 不改后端接口，仅消费现有 `/metrics` 返回字段。
