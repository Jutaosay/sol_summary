from __future__ import annotations

import re

# Solana pubkey/base58: 32-byte key encoded as base58, usually 32~44 chars.
# Excludes 0,O,I,l by base58 alphabet rule.
_BASE58_RE = re.compile(r"^[1-9A-HJ-NP-Za-km-z]{32,44}$")


def is_valid_ca(value: str) -> bool:
    if not value:
        return False
    ca = value.strip()
    if not ca:
        return False
    return bool(_BASE58_RE.fullmatch(ca))


def validate_ca_or_raise(value: str) -> str:
    ca = (value or "").strip()
    if not ca:
        raise ValueError("ca is required")
    if not is_valid_ca(ca):
        raise ValueError("invalid ca format")
    return ca
