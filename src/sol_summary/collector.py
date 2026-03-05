from __future__ import annotations

import logging
import os
import time
from typing import Any

import requests

from .config import REQUEST_TIMEOUT, RPC_URL, RPC_URLS

logger = logging.getLogger(__name__)

MAX_RETRIES = 5
BACKOFF_BASE_SECONDS = 0.6
BACKOFF_MAX_SECONDS = 8.0


def _resolve_rpc_candidates(explicit_rpc_url: str | None = None) -> list[str]:
    if explicit_rpc_url:
        return [explicit_rpc_url]
    env_urls = [x.strip() for x in os.getenv("SOL_RPC_URLS", "").split(",") if x.strip()]
    candidates = env_urls or RPC_URLS[:]
    primary = os.getenv("SOL_RPC_URL", RPC_URL)
    if primary and primary not in candidates:
        candidates.insert(0, primary)
    return candidates or [RPC_URL]


def _rpc_call_once(method: str, params: list[Any], rpc: str) -> dict[str, Any]:
    payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    last_err: Exception | None = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.post(rpc, json=payload, timeout=REQUEST_TIMEOUT)

            if r.status_code == 429:
                wait_s = min(BACKOFF_BASE_SECONDS * (2 ** (attempt - 1)), BACKOFF_MAX_SECONDS)
                msg = (
                    f"rpc rate limited (HTTP 429), method={method}, rpc={rpc}, "
                    f"attempt={attempt}/{MAX_RETRIES}, backoff={wait_s:.2f}s"
                )
                logger.warning(msg)
                last_err = RuntimeError(msg)
                if attempt < MAX_RETRIES:
                    time.sleep(wait_s)
                    continue
                raise last_err

            r.raise_for_status()
            data = r.json()
            if "error" in data:
                raise RuntimeError(str(data["error"]))
            return data["result"]
        except requests.RequestException as e:
            last_err = e
            if attempt < MAX_RETRIES:
                wait_s = min(BACKOFF_BASE_SECONDS * (2 ** (attempt - 1)), BACKOFF_MAX_SECONDS)
                logger.warning(
                    "rpc request failed, method=%s rpc=%s attempt=%s/%s retry_in=%.2fs err=%s",
                    method,
                    rpc,
                    attempt,
                    MAX_RETRIES,
                    wait_s,
                    e,
                )
                time.sleep(wait_s)
                continue
            break
        except Exception as e:
            last_err = e
            break

    raise RuntimeError(
        f"rpc failed method={method} rpc={rpc} attempts={MAX_RETRIES}: {last_err}"
    )


def _rpc_call(method: str, params: list[Any], rpc_url: str | None = None) -> dict[str, Any]:
    candidates = _resolve_rpc_candidates(rpc_url)
    errors: list[str] = []
    for rpc in candidates:
        try:
            return _rpc_call_once(method, params, rpc)
        except Exception as e:
            errors.append(str(e))
            logger.warning("rpc candidate failed, switching next rpc=%s err=%s", rpc, e)
            continue
    raise RuntimeError(f"all rpc candidates failed for {method}: {' | '.join(errors[:3])}")


def get_token_supply_and_decimals(ca: str, rpc_url: str | None = None) -> tuple[int, int]:
    result = _rpc_call("getTokenSupply", [ca], rpc_url=rpc_url)
    value = result.get("value", {})
    amount = int(value.get("amount", "0"))
    decimals = int(value.get("decimals", 0))
    return amount, decimals


def get_token_largest_accounts(ca: str, rpc_url: str | None = None) -> list[dict[str, Any]]:
    result = _rpc_call("getTokenLargestAccounts", [ca], rpc_url=rpc_url)
    return result.get("value", [])


def collect_holder_snapshot(ca: str, rpc_url: str | None = None) -> tuple[list[float], int]:
    # 注意：这里使用 largest accounts 作为实时近似（用于快速 5s 刷新）
    # 真正的全量 holder 数可改为 Helius 增强接口。
    accounts = get_token_largest_accounts(ca, rpc_url=rpc_url)
    balances = []
    for a in accounts:
        ui = a.get("uiAmount")
        if ui is None:
            ui = float(a.get("amount", 0))
        balances.append(float(ui))
    balances.sort(reverse=True)

    # holder_count_estimate：当前是 non-zero largest accounts 的近似值（MVP）
    holder_count_estimate = len([x for x in balances if x > 0])
    return balances, holder_count_estimate
