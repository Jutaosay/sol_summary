from __future__ import annotations

from statistics import median

from .models import HolderMetric


def compute_metric(ca: str, ts: int, holder_balances_sorted_desc: list[float], holder_count: int) -> tuple[HolderMetric, list[float], list[float]]:
    top50 = holder_balances_sorted_desc[:50]
    trimmed = top50[3:-3] if len(top50) >= 7 else []

    top50_total_raw = float(sum(top50))
    trimmed_total = float(sum(trimmed))
    trimmed_count = len(trimmed)
    trimmed_avg = float(trimmed_total / trimmed_count) if trimmed_count else 0.0
    trimmed_median = float(median(trimmed)) if trimmed_count else 0.0
    trimmed_min = float(min(trimmed)) if trimmed_count else 0.0
    trimmed_max = float(max(trimmed)) if trimmed_count else 0.0

    metric = HolderMetric(
        ca=ca,
        ts=ts,
        holder_count=holder_count,
        top50_count=len(top50),
        top50_total_raw=top50_total_raw,
        trimmed_count=trimmed_count,
        trimmed_total=trimmed_total,
        trimmed_avg=trimmed_avg,
        trimmed_median=trimmed_median,
        trimmed_min=trimmed_min,
        trimmed_max=trimmed_max,
    )
    return metric, top50, trimmed
