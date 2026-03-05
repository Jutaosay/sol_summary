from __future__ import annotations

import os

RPC_URL = os.getenv("SOL_RPC_URL", "https://api.mainnet-beta.solana.com")
DB_PATH = os.getenv("SOL_SUMMARY_DB", "data/sol_summary.db")
REFRESH_SECONDS = int(os.getenv("SOL_SUMMARY_REFRESH_SECONDS", "5"))
REQUEST_TIMEOUT = int(os.getenv("SOL_SUMMARY_REQUEST_TIMEOUT", "15"))
