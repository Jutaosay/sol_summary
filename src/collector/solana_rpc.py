from __future__ import annotations

from collections import defaultdict
from typing import Dict

import requests

RPC_URL = "https://api.mainnet-beta.solana.com"
TOKEN_PROGRAM = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
TOKEN_2022_PROGRAM = "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"
RPC_MAX_RETRIES = 3
RPC_BACKOFF_BASE_SECONDS = 0.5


class SolanaRpcError(RuntimeError):
    pass


def _rpc(method: str, params: list, timeout: int = 30) -> dict:
    payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    last_err: Exception | None = None

    for attempt in range(RPC_MAX_RETRIES):
        try:
            r = requests.post(RPC_URL, json=payload, timeout=timeout)
            r.raise_for_status()
            data = r.json()
            if data.get("error"):
                raise SolanaRpcError(str(data["error"]))
            return data["result"]
        except Exception as e:
            last_err = e
            if attempt < RPC_MAX_RETRIES - 1:
                backoff = RPC_BACKOFF_BASE_SECONDS * (2**attempt)
                import time

                time.sleep(backoff)

    raise SolanaRpcError(f"RPC failed after {RPC_MAX_RETRIES} attempts for {method}: {last_err}")


def _fetch_accounts_by_program(program_id: str, ca: str) -> list:
    params = [
        program_id,
        {
            "encoding": "jsonParsed",
            "filters": [
                {"dataSize": 165},
                {"memcmp": {"offset": 0, "bytes": ca}},
            ],
        },
    ]
    return _rpc("getProgramAccounts", params)


def fetch_holders(ca: str) -> dict:
    result = []
    # 同时兼容 legacy SPL Token 与 Token-2022
    for pid in (TOKEN_PROGRAM, TOKEN_2022_PROGRAM):
        try:
            result.extend(_fetch_accounts_by_program(pid, ca))
        except Exception:
            continue

    by_owner: Dict[str, float] = defaultdict(float)
    for row in result:
        parsed = (
            row.get("account", {})
            .get("data", {})
            .get("parsed", {})
            .get("info", {})
        )
        owner = parsed.get("owner")
        ta = parsed.get("tokenAmount", {})
        ui_amount = ta.get("uiAmount")
        if owner is None or ui_amount is None:
            continue
        try:
            amt = float(ui_amount)
        except (TypeError, ValueError):
            continue
        if amt <= 0:
            continue
        by_owner[owner] += amt

    holders = [{"wallet": w, "balance": b} for w, b in by_owner.items()]
    holders.sort(key=lambda x: x["balance"], reverse=True)

    return {
        "holder_count_total": len(holders),
        "holders": holders,
    }
