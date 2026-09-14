"""Unit tests for sanitize_for_discord redaction."""

from __future__ import annotations

from ultron.sanitize import sanitize_for_discord

# Synthetic Discord-shaped token (three MT… segments); not a real credential.
_FAKE_DISCORD_TOKEN = "MTabcdefghijklmnop.abcdefg.abcdefghijklmnop"


def test_empty_and_short_input_unchanged() -> None:
    assert sanitize_for_discord("") == ""
    assert sanitize_for_discord("ok") == "ok"
    assert sanitize_for_discord("short") == "short"


def test_non_secret_prose_unchanged() -> None:
    prose = "Issue #42 is done. Restart the bot after deploy."
    assert sanitize_for_discord(prose) == prose


def test_discord_shaped_token_redacted() -> None:
    text = f"bot token is {_FAKE_DISCORD_TOKEN} end"
    out = sanitize_for_discord(text)
    assert _FAKE_DISCORD_TOKEN not in out
    assert "[REDACTED]" in out


def test_bearer_header_redacted() -> None:
    token = "a" * 24
    text = f"Authorization: Bearer {token}"
    out = sanitize_for_discord(text)
    assert token not in out
    assert "Bearer [REDACTED]" in out


def test_kv_api_key_and_token_lines_redacted() -> None:
    text = "api_key: supersecretvalue\ntoken: anothersecret99"
    out = sanitize_for_discord(text)
    assert "supersecretvalue" not in out
    assert "anothersecret99" not in out
    assert "api_key: [REDACTED]" in out
    assert "token: [REDACTED]" in out


def test_env_assign_discord_and_redmine_redacted() -> None:
    text = (
        "DISCORD_TOKEN=my-discord-bot-token-value\n"
        "REDMINE_API_KEY=redmine-api-key-value-here"
    )
    out = sanitize_for_discord(text)
    assert "my-discord-bot-token-value" not in out
    assert "redmine-api-key-value-here" not in out
    assert "DISCORD_TOKEN=[REDACTED]" in out
    assert "REDMINE_API_KEY=[REDACTED]" in out


def test_openssh_and_rsa_private_key_blocks_redacted() -> None:
    openssh = (
        "-----BEGIN OPENSSH PRIVATE KEY-----\n"
        "b3BlbnNzaC1rZXktdjEAAAAABG5vbmU=\n"
        "-----END OPENSSH PRIVATE KEY-----"
    )
    rsa = (
        "-----BEGIN RSA PRIVATE KEY-----\n"
        "MIIEowIBAAKFAKEKEYMATERIALHERE==\n"
        "-----END RSA PRIVATE KEY-----"
    )
    for block in (openssh, rsa):
        out = sanitize_for_discord(f"key follows\n{block}\ndone")
        assert "BEGIN" not in out
        assert "PRIVATE KEY" not in out
        assert "[REDACTED]" in out


def test_secret_literals_replaced_when_long_enough() -> None:
    secret = "literal-secret-xyz"
    text = f"leak: {secret} in output"
    out = sanitize_for_discord(text, secret_literals=[secret])
    assert secret not in out
    assert out == "leak: [REDACTED] in output"


def test_secret_literals_shorter_than_eight_unchanged() -> None:
    short = "shortie"  # 7 chars
    text = f"value={short}"
    assert sanitize_for_discord(text, secret_literals=[short]) == text
