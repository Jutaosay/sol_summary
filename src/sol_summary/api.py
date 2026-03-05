from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .config import DB_PATH
from .runtime import Runtime
from .storage import Storage
from .validation import validate_ca_or_raise


class TrackRequest(BaseModel):
    ca: str


storage = Storage(DB_PATH)
runtime = Runtime(storage)
app = FastAPI(title="sol_summary")


@app.get("/")
def root():
    web = Path(__file__).resolve().parents[2] / "web" / "index.html"
    return FileResponse(web)


@app.post("/track")
def track(req: TrackRequest):
    try:
        ca = validate_ca_or_raise(req.ca)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    started = runtime.start_tracking(ca)
    return {"ok": True, "ca": ca, "started": started, "tracking": runtime.list_tracking()}


@app.post("/stop")
def stop(req: TrackRequest):
    try:
        ca = validate_ca_or_raise(req.ca)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    stopped = runtime.stop_tracking(ca)
    return {"ok": True, "ca": ca, "stopped": stopped, "tracking": runtime.list_tracking()}


@app.get("/tracking")
def tracking():
    return {"tracking": runtime.list_tracking()}


@app.get("/latest")
def latest(ca: str):
    try:
        ca = validate_ca_or_raise(ca)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    row = storage.get_latest(ca)
    if not row:
        raise HTTPException(404, "no data")
    sample_ok = int(row.get("sample_ok", 0)) == 1
    row["holder_count_is_estimate"] = True
    row["latest_sample_ok"] = sample_ok
    row["degraded"] = not sample_ok
    if not sample_ok:
        row["hint"] = "latest sample failed; try include_failed=true or switch to private RPC/SOL_RPC_URLS"
    return row


@app.get("/metrics")
def metrics(ca: str, limit: int = 120, include_failed: bool = False):
    try:
        ca = validate_ca_or_raise(ca)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    if not (1 <= limit <= 2000):
        raise HTTPException(400, "limit must be in [1, 2000]")

    items = storage.get_metrics(ca, limit=limit, include_failed=include_failed)
    all_items = storage.get_metrics(ca, limit=limit, include_failed=True)

    for item in items:
        item["holder_count_is_estimate"] = True

    success_count = sum(1 for x in all_items if int(x.get("sample_ok", 0)) == 1)
    degraded = len(all_items) > 0 and success_count == 0

    resp = {
        "ca": ca,
        "items": items,
        "degraded": degraded,
        "status": "rpc_limited" if degraded else "ok",
    }
    if not include_failed and len(items) == 0 and len(all_items) > 0:
        resp["hint"] = "no successful samples in current window; retry with include_failed=true or configure private RPC/SOL_RPC_URLS"
    return resp
