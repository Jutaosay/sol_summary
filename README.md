# sol_summary

Solana CA 贴出后自动追踪：
- Top50 持仓余额（raw）
- 去前三/后三后的余额统计（trimmed）
- 持币人数（当前为估算口径）

采样默认每 5 秒，落库 SQLite，提供 API + 前端实时查看。

---

## 1) 架构说明

主实现统一在 `src/sol_summary/*`：

1. **collector** (`src/sol_summary/collector.py`)
   - 调用 Solana RPC `getTokenLargestAccounts`
   - 带重试与指数退避
   - 当前 `holder_count` 为估算值（非全量 holder）

2. **compute** (`src/sol_summary/compute.py`)
   - 计算 top50/raw/trimmed 指标：
   - `top50_total_raw`, `trimmed_total`, `trimmed_avg`, `trimmed_median`, `trimmed_min`, `trimmed_max`

3. **storage** (`src/sol_summary/storage.py`)
   - SQLite 表：`holder_metrics`, `job_log`
   - 进程内 `RLock` 串行化 DB 访问（规避多线程并发写冲突）

4. **runtime** (`src/sol_summary/runtime.py`)
   - 每个 CA 一个后台线程，按固定间隔采样
   - 失败样本也落库：`sample_ok=0`, `err_msg` 记录错误

5. **api** (`src/sol_summary/api.py`)
   - `/track`, `/stop`, `/tracking`, `/latest`, `/metrics`
   - `/metrics` 支持 `include_failed`
   - `limit` 约束：`1..2000`

6. **web** (`web/index.html`)
   - Chart.js 简单折线图展示

> 旧目录 `src/api|collector|storage|processor` 仅历史残留，不作为主入口。

---

## 2) 依赖安装

### Python 依赖（必须装到项目 `.venv`）

```bash
cd /home/ubuntu/Codings/Projects/sol_summary
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`requirements.txt`：
- fastapi
- uvicorn
- requests
- pydantic

### Node 依赖（仅 E2E Playwright 用）

```bash
npm install
```

---

## 3) 启动方式

### API 服务

```bash
cd /home/ubuntu/Codings/Projects/sol_summary
source .venv/bin/activate
PYTHONPATH=src uvicorn sol_summary.api:app --host 0.0.0.0 --port 8787
```

页面：`http://<host>:8787/`

---

## 4) API

Base URL: `http://<host>:8787`

- `POST /track` body: `{ "ca": "..." }`
- `POST /stop` body: `{ "ca": "..." }`
- `GET /tracking`
- `GET /latest?ca=<CA>`
  - 返回包含 `holder_count_is_estimate=true`
- `GET /metrics?ca=<CA>&limit=120`
  - 默认仅成功样本（`sample_ok=1`）
  - 返回 `degraded/status`；当窗口内全失败且默认过滤后为空，会返回 `hint`
- `GET /metrics?ca=<CA>&limit=120&include_failed=true`
  - 包含失败样本
- `GET /latest?ca=<CA>`
  - 额外返回 `latest_sample_ok/degraded/hint`
- `limit` 不在 `[1,2000]` 时返回 HTTP 400

---

## 5) 环境变量

- `SOL_RPC_URL`：主 RPC 地址
- `SOL_RPC_URLS`：备用 RPC 列表（逗号分隔，主RPC失败时自动回退）
- `SOL_SUMMARY_DB`：数据库路径（默认 `data/sol_summary.db`）
- `SOL_SUMMARY_REFRESH_SECONDS`：采样间隔，默认 5
- `SOL_SUMMARY_REQUEST_TIMEOUT`：请求超时，默认 15

---

## 6) 5 轮长 Check 结果（最新）

报告文件：
- `reports/check-round5.md`
- `reports/check-round5.json`

结论（CA: `E9SmMCvtLfitMwkLzkduwgN8ZYcfepiELLQ8d1SApump`）：
- 成功轮次（默认 metrics 有成功样本）：**0/5**
- 失败轮次：**5/5**
- 主要原因：公共 RPC `HTTP 429` 限流
- 现象：
  - `/metrics` 默认常为空（因为只回 `sample_ok=1`）
  - `/metrics?include_failed=true` 可看到失败样本与 `err_msg`

优化优先级：
1. 接入私有 RPC（最高优先）
2. 增加 RPC 池（多个 URL 回退）
3. 增大采样间隔到 8~15s

---

## 7) 测试

### 单元测试

```bash
cd /home/ubuntu/Codings/Projects/sol_summary
source .venv/bin/activate
PYTHONPATH=. .venv/bin/pytest -q
```

### E2E（Playwright）

```bash
bash scripts/run_playwright_e2e.sh
```

---

## 8) 已知限制

1. `holder_count` 目前是估算值（largest accounts 近似），不等于全量链上 holder。
2. 公共 RPC 在高频采样下很容易 429。
3. SQLite 适合单机轻量，后续可迁移 PostgreSQL + 时序存储。
