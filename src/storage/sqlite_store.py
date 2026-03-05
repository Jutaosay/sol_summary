from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict, Iterable


SCHEMA = """
CREATE TABLE IF NOT EXISTS tokens (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ca TEXT NOT NULL UNIQUE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  token_id INTEGER NOT NULL,
  ts DATETIME DEFAULT CURRENT_TIMESTAMP,
  holder_count_total INTEGER NOT NULL,
  top50_sum_raw REAL NOT NULL,
  top50_avg_raw REAL NOT NULL,
  top50_sum_trimmed REAL NOT NULL,
  top50_avg_trimmed REAL NOT NULL,
  top50_count INTEGER NOT NULL,
  trimmed_count INTEGER NOT NULL,
  sample_ok INTEGER NOT NULL DEFAULT 1,
  err_msg TEXT,
  FOREIGN KEY (token_id) REFERENCES tokens(id)
);

CREATE TABLE IF NOT EXISTS holders_snapshot (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  snapshot_id INTEGER NOT NULL,
  rank INTEGER NOT NULL,
  wallet TEXT NOT NULL,
  balance REAL NOT NULL,
  FOREIGN KEY (snapshot_id) REFERENCES snapshots(id)
);

CREATE INDEX IF NOT EXISTS idx_snapshots_token_ts ON snapshots(token_id, ts DESC);
CREATE INDEX IF NOT EXISTS idx_holders_snapshot_rank ON holders_snapshot(snapshot_id, rank);
"""


class SqliteStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._connect() as conn:
            conn.executescript(SCHEMA)
            conn.commit()

    def upsert_token(self, ca: str) -> int:
        with self._connect() as conn:
            conn.execute("INSERT OR IGNORE INTO tokens(ca) VALUES(?)", (ca,))
            cur = conn.execute("SELECT id FROM tokens WHERE ca=?", (ca,))
            token_id = cur.fetchone()[0]
            conn.commit()
            return token_id

    def insert_snapshot(self, ca: str, stats: Dict, holder_count_total: int, top50: Iterable[Dict], sample_ok: int = 1, err_msg: str | None = None) -> int:
        token_id = self.upsert_token(ca)
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO snapshots(
                  token_id, holder_count_total, top50_sum_raw, top50_avg_raw,
                  top50_sum_trimmed, top50_avg_trimmed, top50_count, trimmed_count,
                  sample_ok, err_msg
                ) VALUES(?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    token_id,
                    holder_count_total,
                    stats["top50_sum_raw"],
                    stats["top50_avg_raw"],
                    stats["top50_sum_trimmed"],
                    stats["top50_avg_trimmed"],
                    stats["top50_count"],
                    stats["trimmed_count"],
                    sample_ok,
                    err_msg,
                ),
            )
            snapshot_id = cur.lastrowid
            for i, item in enumerate(top50, start=1):
                conn.execute(
                    "INSERT INTO holders_snapshot(snapshot_id, rank, wallet, balance) VALUES(?,?,?,?)",
                    (snapshot_id, i, item["wallet"], item["balance"]),
                )
            conn.commit()
            return snapshot_id

    def latest(self, ca: str):
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT s.ts, s.holder_count_total, s.top50_sum_raw, s.top50_avg_raw,
                       s.top50_sum_trimmed, s.top50_avg_trimmed, s.top50_count, s.trimmed_count,
                       s.sample_ok, s.err_msg
                FROM snapshots s JOIN tokens t ON s.token_id=t.id
                WHERE t.ca=? ORDER BY s.ts DESC, s.id DESC LIMIT 1
                """,
                (ca,),
            ).fetchone()
            if not row:
                return None
            return {
                "ts": row[0],
                "holder_count_total": row[1],
                "top50_sum_raw": row[2],
                "top50_avg_raw": row[3],
                "top50_sum_trimmed": row[4],
                "top50_avg_trimmed": row[5],
                "top50_count": row[6],
                "trimmed_count": row[7],
                "sample_ok": row[8],
                "err_msg": row[9],
            }

    def series(self, ca: str, points: int = 120, include_failed: bool = False):
        with self._connect() as conn:
            where_clause = "WHERE t.ca=?" if include_failed else "WHERE t.ca=? AND s.sample_ok=1"
            rows = conn.execute(
                f"""
                SELECT s.ts, s.holder_count_total, s.top50_sum_raw, s.top50_sum_trimmed, s.sample_ok, s.err_msg
                FROM snapshots s JOIN tokens t ON s.token_id=t.id
                {where_clause} ORDER BY s.ts DESC, s.id DESC LIMIT ?
                """,
                (ca, points),
            ).fetchall()
        rows = list(reversed(rows))
        return [
            {
                "ts": r[0],
                "holder_count_total": r[1],
                "top50_sum_raw": r[2],
                "top50_sum_trimmed": r[3],
                "sample_ok": r[4],
                "err_msg": r[5],
            }
            for r in rows
        ]
