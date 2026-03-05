import re

CA_RE = re.compile(r"(?:CA\s*[:：]\s*)?([1-9A-HJ-NP-Za-km-z]{32,48})")


def extract_ca(text: str) -> str | None:
    m = CA_RE.search(text or "")
    return m.group(1) if m else None
