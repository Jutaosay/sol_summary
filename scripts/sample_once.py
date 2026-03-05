from src.collector.solana_rpc import fetch_holders
from src.processor.stats import HolderPoint, compute_top50_stats
from src.storage.sqlite_store import SqliteStore
import argparse, json

ap = argparse.ArgumentParser()
ap.add_argument("--ca", required=True)
ap.add_argument("--db", default="data/sol_summary.db")
args = ap.parse_args()

store = SqliteStore(args.db)
holder_data = fetch_holders(args.ca)
points = [HolderPoint(wallet=h["wallet"], balance=h["balance"]) for h in holder_data["holders"]]
stats = compute_top50_stats(points)
store.insert_snapshot(args.ca, stats, holder_data["holder_count_total"], stats["top50"])
print(json.dumps({
    "ca": args.ca,
    "holder_count_total": holder_data["holder_count_total"],
    "top50_count": stats["top50_count"],
    "top50_sum_raw": stats["top50_sum_raw"],
    "top50_sum_trimmed": stats["top50_sum_trimmed"],
    "trimmed_count": stats["trimmed_count"],
}, ensure_ascii=False, indent=2))
