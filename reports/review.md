# sol_summary 代码审查报告（Check）

- 审查范围：`/home/ubuntu/Codings/Projects/sol_summary`
- 关注点：数据口径、异常处理、并发线程、SQLite 事务、API 设计、可观测性
- 审查方式：静态代码审查（未改代码）
- 结论：**NEED_FIX**（当前不建议直接上线）

---

## 风险分级总览

### Critical

#### 1) 数据口径严重偏差：`holder_count` 被“近似值”替代，可能误导业务判断
- **现象**：`src/sol_summary/collector.py:44-58` 使用 `getTokenLargestAccounts`，并明确注释“holder_count 先用 non-zero largest 数做近似”。
- **影响**：`holder_count` 实际仅是“最大账户列表里的非零数”，并非真实全量持币人数。若下游把它当真实指标，会导致策略误判。
- **复现条件**：大多数 token（真实 holder 远大于 largest accounts 返回数量）均可复现。
- **修复建议**：
  - API 字段更名为 `holder_count_estimated`（至少先防误用）；
  - 或改为全量口径采集（如 `getProgramAccounts`/索引服务），并在文档中定义精确口径。

#### 2) 多线程共享单 SQLite 连接，无串行保护，存在写入异常/数据丢失风险
- **现象**：`src/sol_summary/storage.py:14` 单连接 `check_same_thread=False`，`src/sol_summary/runtime.py:49-62` 多 tracker 线程并发写同一连接，无锁。
- **影响**：可能出现 `database is locked`、事务竞争、写失败、线程崩溃；高频采样下风险显著。
- **复现条件**：同时追踪多个 CA（>=2）且 5s 写频率持续一段时间。
- **修复建议**：
  - 每线程独立连接 + `busy_timeout` + WAL；或
  - 单写线程队列化（生产更稳），统一 commit 与重试策略。

---

### High

#### 3) 异常被吞并并“伪装成功”，监控面会看到正常但数据是空
- **现象**：`src/collector/solana_rpc.py:59-63` 对 program 查询异常直接 `continue`；若两个 program 都失败，`fetch_holders` 返回空集合（`holder_count_total=0`），上层仍按成功路径写入。
- **影响**：RPC 故障/限流会被误记为“真实归零”，造成错误告警与错误分析。
- **复现条件**：RPC 网络异常、429、节点不稳定。
- **修复建议**：
  - 定义“采样失败”与“真实零值”两种状态；
  - 两个 program 全失败时抛异常并落 `sample_ok=0`。

#### 4) 线程生命周期与状态管理有竞态：可能重复采样、僵尸状态
- **现象**：`src/api/app.py:20,110-128` 的 `workers` 字典无锁；`stop` 先 `pop` 再等待线程退出。并发请求下可出现重复启动/停止竞态。
- **影响**：同一 CA 可能出现多线程重复采样；状态返回与真实线程状态不一致。
- **复现条件**：短时间内并发 `track/stop` 同一 CA。
- **修复建议**：
  - 对 tracker 注册/注销加锁；
  - `stop` 后 `join(timeout)` 再移除；
  - 为每个 tracker 增加状态机（starting/running/stopping/stopped）。

#### 5) 错误回写路径不安全：异常分支再次写库失败会直接打崩 worker
- **现象**：`src/api/app.py:74-101` 中 try 失败后在 except 内再次 `insert_snapshot`，但该调用本身未保护；若 DB 本身故障，会逃逸异常导致线程退出。
- **影响**：单次 DB/IO 抖动可导致该 CA 的采样线程永久停止。
- **复现条件**：数据库锁冲突/磁盘异常/连接错误。
- **修复建议**：except 内再包一层 fail-safe（日志+退避），确保线程不会因“记录错误失败”而退出。

#### 6) API 实现双轨并存且语义不一致，外部调用方容易误用
- **现象**：
  - `src/api/app.py`：`/track/{ca}`、`/latest/{ca}`、`/series/{ca}`；
  - `src/sol_summary/api.py`：`/track`(body)、`/latest?ca=...`、`/metrics`。
  - 两条链路的数据采集口径也不同（全量聚合 vs largest accounts 近似）。
- **影响**：前端/脚本接错入口会得到不同指标口径，难以排障和对账。
- **复现条件**：按不同 README/启动方式运行。
- **修复建议**：收敛到单一 API 面，标注版本与口径；旧接口明确 deprecated。

---

### Medium

#### 7) SQLite 事务边界可优化：高频小事务 + 每次新连接，吞吐与锁竞争压力大
- **现象**：`src/storage/sqlite_store.py` 每次调用都新建连接并立即 commit；`upsert_token` 与 `insert_snapshot` 也是分离事务。
- **影响**：在 5s×多 CA 场景中，锁竞争与 I/O 放大明显，稳定性下降。
- **修复建议**：
  - 合并 token upsert + snapshot insert 至同一事务；
  - 设置 `PRAGMA busy_timeout`、WAL、合理同步级别；
  - 批量/异步写入减小事务频率。

#### 8) API 参数缺少约束与保护，易被滥用或导致重查询
- **现象**：`src/api/app.py:139-141` 的 `points` 无上限；`ca` 未做格式校验。
- **影响**：超大 `points` 可造成慢查询；非法 CA 带来无效 RPC 与日志噪音。
- **修复建议**：
  - 对 `ca` 加正则校验（base58 长度与字符集）；
  - 对 `points` 做上限（如 500/2000）和默认兜底。

#### 9) 可观测性不足：缺少健康度、错误率、线程状态可视化
- **现象**：仅部分路径写 `job_log`（`src/sol_summary` 线），`src/api` 线几乎无统一日志/指标；无 `/health`、无 per-CA 错误率和最后成功时间。
- **影响**：线上故障定位慢，难区分“数据真实变化”与“采集异常”。
- **修复建议**：补充结构化日志、健康检查、采样成功率/延迟/最近错误指标。

#### 10) 测试与运行入口不一致，CI 可靠性不足
- **现象**：`tests/test_stats.py` 直接 `from src.processor...`，在当前环境下 pytest 收集失败（`ModuleNotFoundError: No module named 'src'`）。
- **影响**：核心计算逻辑缺少有效自动化回归保障。
- **修复建议**：统一包结构与 PYTHONPATH（或改成可安装包），修复测试导入并接入 CI。

---

### Low

#### 11) 文档与实现存在偏差，增加协作成本
- **现象**：README 主要描述的是 `src/api/app.py` 路径；代码中同时存在另一套 `sol_summary` API/存储实现。
- **影响**：新成员易混淆“哪套是主线”。
- **修复建议**：README 明确唯一推荐入口、数据口径、字段语义与废弃路径。

---

## 可立即修复清单（最多 8 条）

1. **给 `ca` 做强校验**（base58 + 长度），非法请求直接 400。  
2. **给 `points/limit` 加上限**（例如 1~500），避免重查询。  
3. **并发写 SQLite 加串行化**：先用全局写锁/单写线程止血。  
4. **设置 SQLite `busy_timeout` + WAL**（两套存储实现都统一）。  
5. **区分“采样失败”与“真实零值”**，两个 program 全失败时强制 `sample_ok=0`。  
6. **修复 stop/track 竞态**：加锁 + `join(timeout)` 后再移除 tracker。  
7. **补 `/health` 与基础指标**：最近成功时间、连续失败次数、采样延迟 P95。  
8. **统一单一 API 入口并标注口径**，把另一条链路标记 deprecated。  

---

## 复核建议（修复后重点回归）

1. **数据口径回归**：同一 CA 下 `holder_count` 与口径说明一致，不再“近似冒充精确”。
2. **并发稳定性回归**：同时追踪 5~20 个 CA，持续 30~60 分钟无线程退出、无 DB lock 异常。
3. **异常链路回归**：模拟 RPC 429/超时/断网，确认 `sample_ok`、错误日志、恢复行为正确。
4. **API 一致性回归**：前端与脚本仅使用统一入口，字段语义稳定。
5. **可观测性回归**：故障时可在 1 分钟内通过指标定位问题来源（RPC/DB/线程）。
