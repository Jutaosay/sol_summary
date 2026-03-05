from __future__ import annotations

import argparse
import json
import socket
import subprocess
import sys
import time

import requests
import uvicorn


def _wait_port(host: str, port: int, timeout: float = 10.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=1.0):
                return True
        except OSError:
            time.sleep(0.2)
    return False


def _smoke_existing(base_url: str, ca: str, wait_seconds: int) -> int:
    print(f"[smoke] track ca={ca}")
    r = requests.post(f"{base_url}/track", json={"ca": ca}, timeout=10)
    print(f"[smoke] POST /track -> {r.status_code} {r.text}")
    r.raise_for_status()

    if wait_seconds > 0:
        print(f"[smoke] waiting {wait_seconds}s for at least one sample...")
        time.sleep(wait_seconds)

    latest = requests.get(f"{base_url}/latest", params={"ca": ca}, timeout=10)
    print(f"[smoke] GET /latest?ca=... -> {latest.status_code}")
    print(json.dumps(latest.json(), ensure_ascii=False, indent=2))

    metrics = requests.get(
        f"{base_url}/metrics",
        params={"ca": ca, "limit": 1, "include_failed": True},
        timeout=10,
    )
    print(f"[smoke] GET /metrics?ca=...&limit=1&include_failed=true -> {metrics.status_code}")
    print(json.dumps(metrics.json(), ensure_ascii=False, indent=2))

    stop = requests.post(f"{base_url}/stop", json={"ca": ca}, timeout=10)
    print(f"[smoke] POST /stop -> {stop.status_code} {stop.text}")
    stop.raise_for_status()

    return 0


def _smoke_with_spawn(host: str, port: int, ca: str, wait_seconds: int) -> int:
    cmd = [
        sys.executable,
        "-m",
        "sol_summary.main",
        "serve",
        "--host",
        host,
        "--port",
        str(port),
    ]
    print(f"[smoke] starting server: {' '.join(cmd)}")
    proc = subprocess.Popen(cmd)
    try:
        if not _wait_port(host, port, timeout=15):
            raise RuntimeError(f"server not ready at {host}:{port}")
        base_url = f"http://{host}:{port}"
        return _smoke_existing(base_url, ca, wait_seconds)
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


def main() -> int:
    ap = argparse.ArgumentParser(prog="sol_summary")
    sub = ap.add_subparsers(dest="cmd", required=True)

    srv = sub.add_parser("serve")
    srv.add_argument("--host", default="127.0.0.1")
    srv.add_argument("--port", type=int, default=8787)

    smoke = sub.add_parser("smoke")
    smoke.add_argument("--ca", required=True)
    smoke.add_argument("--wait-seconds", type=int, default=6)
    smoke.add_argument("--host", default="127.0.0.1")
    smoke.add_argument("--port", type=int, default=8787)
    smoke.add_argument(
        "--use-existing-server",
        action="store_true",
        help="如果提供该参数，则不拉起新服务，直接访问现有 http://host:port",
    )

    args = ap.parse_args()

    if args.cmd == "serve":
        uvicorn.run("sol_summary.api:app", host=args.host, port=args.port, reload=False)
        return 0

    if args.cmd == "smoke":
        if args.use_existing_server:
            return _smoke_existing(f"http://{args.host}:{args.port}", args.ca, args.wait_seconds)
        return _smoke_with_spawn(args.host, args.port, args.ca, args.wait_seconds)

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
