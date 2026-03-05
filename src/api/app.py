from __future__ import annotations

import os
import threading
import time
from typing import Dict

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from src.collector.solana_rpc import fetch_holders
from src.processor.stats import HolderPoint, compute_top50_stats
from src.storage.sqlite_store import SqliteStore

DB_PATH = os.getenv("SOL_SUMMARY_DB", "data/sol_summary.db")
POLL_SECONDS = int(os.getenv("SOL_SUMMARY_POLL_SECONDS", "5"))

app = FastAPI(title="sol_summary")
store = SqliteStore(DB_PATH)
workers: Dict[str, threading.Event] = {}


INDEX_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>sol_summary</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
  <h3>sol_summary 实时曲线</h3>
  <input id="ca" style="width:520px" placeholder="贴 Solana CA"/>
  <button onclick="track()">开始跟踪</button>
  <canvas id="c" width="1200" height="420"></canvas>
  <script>
    const ctx = document.getElementById('c').getContext('2d');
    const chart = new Chart(ctx, {
      type: 'line',
      data: { labels: [], datasets: [
        {label:'top50_sum_raw', data: [], borderColor: '#1f77b4'},
        {label:'top50_sum_trimmed', data: [], borderColor: '#ff7f0e'},
        {label:'holder_count_total', data: [], borderColor: '#2ca02c'}
      ]},
      options: { animation: false, responsive: false }
    });

    async function track(){
      const ca = document.getElementById('ca').value.trim();
      if(!ca) return;
      await fetch(`/track/${ca}`, {method:'POST'});
      window.__ca = ca;
    }

    async function tick(){
      if(!window.__ca) return;
      const res = await fetch(`/series/${window.__ca}?points=120`);
      const data = await res.json();
      chart.data.labels = data.map(x => x.ts.slice(11,19));
      chart.data.datasets[0].data = data.map(x => x.top50_sum_raw);
      chart.data.datasets[1].data = data.map(x => x.top50_sum_trimmed);
      chart.data.datasets[2].data = data.map(x => x.holder_count_total);
      chart.update();
    }
    setInterval(tick, 5000);
  </script>
</body>
</html>
"""


def run_job(ca: str, stop_event: threading.Event):
    while not stop_event.is_set():
        try:
            holder_data = fetch_holders(ca)
            points = [HolderPoint(wallet=h["wallet"], balance=h["balance"]) for h in holder_data["holders"]]
            stats = compute_top50_stats(points)
            store.insert_snapshot(
                ca=ca,
                stats=stats,
                holder_count_total=holder_data["holder_count_total"],
                top50=stats["top50"],
                sample_ok=1,
                err_msg=None,
            )
        except Exception as e:
            store.insert_snapshot(
                ca=ca,
                stats={
                    "top50_sum_raw": 0.0,
                    "top50_avg_raw": 0.0,
                    "top50_sum_trimmed": 0.0,
                    "top50_avg_trimmed": 0.0,
                    "top50_count": 0,
                    "trimmed_count": 0,
                },
                holder_count_total=0,
                top50=[],
                sample_ok=0,
                err_msg=str(e),
            )
        stop_event.wait(POLL_SECONDS)


@app.get("/", response_class=HTMLResponse)
def home():
    return INDEX_HTML


@app.post("/track/{ca}")
def track(ca: str):
    if ca in workers:
        return {"ok": True, "tracking": True, "ca": ca, "msg": "already tracking"}
    stop_event = threading.Event()
    workers[ca] = stop_event
    th = threading.Thread(target=run_job, args=(ca, stop_event), daemon=True)
    th.start()
    return {"ok": True, "tracking": True, "ca": ca, "poll_seconds": POLL_SECONDS}


@app.post("/stop/{ca}")
def stop(ca: str):
    evt = workers.get(ca)
    if not evt:
        raise HTTPException(status_code=404, detail="not tracking")
    evt.set()
    workers.pop(ca, None)
    return {"ok": True, "tracking": False, "ca": ca}


@app.get("/latest/{ca}")
def latest(ca: str):
    data = store.latest(ca)
    if not data:
        raise HTTPException(status_code=404, detail="no data")
    return data


@app.get("/series/{ca}")
def series(ca: str, points: int = 120, include_failed: bool = False):
    return store.series(ca, points=points, include_failed=include_failed)
