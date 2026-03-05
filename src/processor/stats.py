from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class HolderPoint:
    wallet: str
    balance: float


def compute_top50_stats(points: List[HolderPoint]) -> dict:
    sorted_points = sorted(points, key=lambda x: x.balance, reverse=True)[:50]
    balances = [p.balance for p in sorted_points]
    if not balances:
        return {
            "top50_count": 0,
            "top50_sum_raw": 0.0,
            "top50_avg_raw": 0.0,
            "top50_sum_trimmed": 0.0,
            "top50_avg_trimmed": 0.0,
            "trimmed_count": 0,
            "top50": [],
        }

    raw_sum = float(sum(balances))
    raw_avg = raw_sum / len(balances)

    if len(balances) > 6:
        trimmed = balances[3:-3]
    else:
        trimmed = []

    trim_sum = float(sum(trimmed))
    trim_avg = trim_sum / len(trimmed) if trimmed else 0.0

    return {
        "top50_count": len(balances),
        "top50_sum_raw": raw_sum,
        "top50_avg_raw": raw_avg,
        "top50_sum_trimmed": trim_sum,
        "top50_avg_trimmed": trim_avg,
        "trimmed_count": len(trimmed),
        "top50": [{"wallet": p.wallet, "balance": p.balance} for p in sorted_points],
    }
