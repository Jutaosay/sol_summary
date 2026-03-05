from __future__ import annotations

from dataclasses import dataclass


@dataclass
class HolderMetric:
    ca: str
    ts: int
    holder_count: int
    top50_count: int
    top50_total_raw: float
    trimmed_count: int
    trimmed_total: float
    trimmed_avg: float
    trimmed_median: float
    trimmed_min: float
    trimmed_max: float
    sample_ok: int = 1
    err_msg: str | None = None
