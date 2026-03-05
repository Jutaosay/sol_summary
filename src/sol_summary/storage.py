from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path

from .models import HolderMetric


HOLDER_METRICS_COLUMNS = {
    "id",
    "ca",
    "ts",
    "holder_count",
    "top50_count",
    "top50_total_raw",
    "trimmed_count",
    "trimmed_total",
    "trimmed_avg",
    "trimmed_median",
    "trimmed_min",
    "trimmed_max",
    "top50_raw_json",
    "trimmed_json",
    "sample_ok",
    "err_msg",
}

JOB_LOG_COLUMNS = {
    "id",
    "ts",
    "ca",
    "status",
    "latency_ms",
    "err_msg",
}


class Storage:
    def __init__(self, db_path: str) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._db_lock = threading.RLock()
        self.conn = sqlite3.connect(self.db_path.as_posix(), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        with self._db_lock:
            self.conn.execute("PRAGMA journal_mode=WAL;")
            self.conn.execute("PRAGMA synchronous=NORMAL;")
            self._init_schema()

    def _table_columns(self, table: str) -> set[str]:
        with self._db_lock:
            rows = self.conn.execute(f"PRAGMA table_info({table})").fetchall()
            return {r[1] for r in rows}

    def _drop_if_incompatible(self, table: str, expected_columns: set[str]) -> None:
        cols = self._table_columns(table)
        if cols and cols != expected_columns:
            # 旧 schema 与当前需求不一致时，直接重建，避免依赖历史表结构。
            with self._db_lock:
                self.conn.execute(f"DROP TABLE IF EXISTS {table}")

    def _init_schema(self) -> None:
        # 保证幂等：可重复执行；且遇到旧/不兼容表时自动重建。
        self._drop_if_incompatible("holder_metrics", HOLDER_METRICS_COLUMNS)
        self._drop_if_incompatible("job_log", JOB_LOG_COLUMNS)

        with self._db_lock:
            self.conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS holder_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ca TEXT NOT NULL,
                    ts INTEGER NOT NULL,
                    holder_count INTEGER NOT NULL,
                    top50_count INTEGER NOT NULL,
                    top50_total_raw REAL NOT NULL,
                    trimmed_count INTEGER NOT NULL,
                    trimmed_total REAL NOT NULL,
                    trimmed_avg REAL NOT NULL,
                    trimmed_median REAL NOT NULL,
                    trimmed_min REAL NOT NULL,
                    trimmed_max REAL NOT NULL,
                    top50_raw_json TEXT NOT NULL,
                    trimmed_json TEXT NOT NULL,
                    sample_ok INTEGER NOT NULL DEFAULT 1,
                    err_msg TEXT
                );

                CREATE TABLE IF NOT EXISTS job_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts INTEGER NOT NULL,
                    ca TEXT NOT NULL,
                    status TEXT NOT NULL,
                    latency_ms INTEGER,
                    err_msg TEXT
                );

                CREATE INDEX IF NOT EXISTS idx_holder_metrics_ca_ts
                ON holder_metrics(ca, ts DESC);

                CREATE INDEX IF NOT EXISTS idx_job_log_ca_ts
                ON job_log(ca, ts DESC);
                """
            )
            self.conn.commit()

    def insert_metric(self, metric: HolderMetric, top50_raw: list[float], trimmed: list[float]) -> None:
        with self._db_lock:
            self.conn.execute(
                """
                INSERT INTO holder_metrics (
                    ca, ts, holder_count, top50_count, top50_total_raw,
                    trimmed_count, trimmed_total, trimmed_avg, trimmed_median,
                    trimmed_min, trimmed_max, top50_raw_json, trimmed_json,
                    sample_ok, err_msg
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    metric.ca,
                    metric.ts,
                    metric.holder_count,
                    metric.top50_count,
                    metric.top50_total_raw,
                    metric.trimmed_count,
                    metric.trimmed_total,
                    metric.trimmed_avg,
                    metric.trimmed_median,
                    metric.trimmed_min,
                    metric.trimmed_max,
                    json.dumps(top50_raw),
                    json.dumps(trimmed),
                    metric.sample_ok,
                    metric.err_msg,
                ),
            )
            self.conn.commit()

    def insert_job_log(self, ts: int, ca: str, status: str, latency_ms: int | None = None, err_msg: str | None = None) -> None:
        with self._db_lock:
            self.conn.execute(
                "INSERT INTO job_log (ts, ca, status, latency_ms, err_msg) VALUES (?, ?, ?, ?, ?)",
                (ts, ca, status, latency_ms, err_msg),
            )
            self.conn.commit()

    def get_latest(self, ca: str):
        with self._db_lock:
            row = self.conn.execute(
                "SELECT * FROM holder_metrics WHERE ca = ? ORDER BY ts DESC LIMIT 1",
                (ca,),
            ).fetchone()
            return dict(row) if row else None

    def get_metrics(self, ca: str, limit: int = 120, include_failed: bool = False):
        where_clause = "ca = ?" if include_failed else "ca = ? AND sample_ok = 1"
        with self._db_lock:
            rows = self.conn.execute(
                f"SELECT * FROM holder_metrics WHERE {where_clause} ORDER BY ts DESC LIMIT ?",
                (ca, limit),
            ).fetchall()
            return [dict(r) for r in rows][::-1]
