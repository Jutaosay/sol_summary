from src.processor.stats import HolderPoint, compute_top50_stats


def test_trimmed_math():
    pts = [HolderPoint(wallet=f"w{i}", balance=float(i)) for i in range(1, 51)]
    s = compute_top50_stats(pts)
    assert s["top50_count"] == 50
    assert s["trimmed_count"] == 44
    assert round(s["top50_sum_raw"], 2) == 1275.0
    assert round(s["top50_sum_trimmed"], 2) == 1122.0
