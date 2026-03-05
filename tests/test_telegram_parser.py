from src.bot.telegram_parser import extract_ca


def test_extract_ca_with_prefix():
    ca = "So11111111111111111111111111111111111111112"
    text = f"新币来了 CA: {ca} 速看"
    assert extract_ca(text) == ca


def test_extract_ca_plain_text():
    ca = "9xQeWvG816bUx9EPf2n1sM6RzV8Y9xQeWvG816bUx9EP"
    text = f"{ca}"
    assert extract_ca(text) == ca


def test_extract_ca_invalid_text_returns_none():
    assert extract_ca("这段文本没有合规的 Solana CA, CA: not-a-valid-address") is None
