"""Unit tests for whitelist / pending-token state_store (hermetic, tmp_path)."""

from __future__ import annotations

import json
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

import ultron.state_store as ss
from ultron.state_store import (
    ADMINS_FILE,
    PENDING_FILE,
    TOKEN_TTL_SECONDS,
    WHITELIST_FILE,
    consume_token_add_whitelist,
    is_admin,
    is_user_whitelisted,
    register_pending_token,
    remove_user_from_whitelist,
)


@pytest.fixture(autouse=True)
def _reset_state_caches() -> None:
    """Clear module-level whitelist/admins mtime caches between tests."""
    ss._whitelist_mtime = None
    ss._whitelist_ids = None
    ss._admins_mtime = None
    ss._admins_ids = None
    yield
    ss._whitelist_mtime = None
    ss._whitelist_ids = None
    ss._admins_mtime = None
    ss._admins_ids = None


def test_register_and_consume_happy_path(tmp_path: Path) -> None:
    token = register_pending_token(tmp_path, 42)
    assert isinstance(token, str) and len(token) > 16
    uid = consume_token_add_whitelist(tmp_path, token)
    assert uid == 42
    assert is_user_whitelisted(tmp_path, 42) is True
    pending = json.loads((tmp_path / PENDING_FILE).read_text(encoding="utf-8"))
    assert token not in pending


def test_consume_unknown_empty_expired(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="empty token"):
        consume_token_add_whitelist(tmp_path, "   ")
    with pytest.raises(ValueError, match="unknown token"):
        consume_token_add_whitelist(tmp_path, "no-such-token")

    token = register_pending_token(tmp_path, 7)
    pending_path = tmp_path / PENDING_FILE
    pending = json.loads(pending_path.read_text(encoding="utf-8"))
    pending[token]["expires_at"] = time.time() - 1
    pending_path.write_text(json.dumps(pending), encoding="utf-8")
    with pytest.raises(ValueError, match="token expired"):
        consume_token_add_whitelist(tmp_path, token)
    assert is_user_whitelisted(tmp_path, 7) is False


def test_register_replaces_prior_pending_for_same_user(tmp_path: Path) -> None:
    first = register_pending_token(tmp_path, 99)
    second = register_pending_token(tmp_path, 99)
    assert first != second
    pending = json.loads((tmp_path / PENDING_FILE).read_text(encoding="utf-8"))
    assert first not in pending
    assert second in pending
    with pytest.raises(ValueError, match="unknown token"):
        consume_token_add_whitelist(tmp_path, first)
    assert consume_token_add_whitelist(tmp_path, second) == 99


def test_is_user_whitelisted_missing_valid_and_mtime_refresh(tmp_path: Path) -> None:
    assert is_user_whitelisted(tmp_path, 1) is False

    wl = tmp_path / WHITELIST_FILE
    wl.write_text(json.dumps([10, 20]), encoding="utf-8")
    assert is_user_whitelisted(tmp_path, 10) is True
    assert is_user_whitelisted(tmp_path, 99) is False

    # Cache hit path (same mtime)
    assert is_user_whitelisted(tmp_path, 10) is True

    # Change file so mtime updates and cache refreshes
    time.sleep(0.02)
    wl.write_text(json.dumps([99]), encoding="utf-8")
    assert is_user_whitelisted(tmp_path, 10) is False
    assert is_user_whitelisted(tmp_path, 99) is True


def test_is_admin_env_file_missing_and_mtime_refresh(tmp_path: Path) -> None:
    env_admins = frozenset({111})
    assert is_admin(tmp_path, 111, env_admins) is True
    assert is_admin(tmp_path, 222, env_admins) is False

    admins = tmp_path / ADMINS_FILE
    admins.write_text(json.dumps([222]), encoding="utf-8")
    assert is_admin(tmp_path, 222, frozenset()) is True
    assert is_admin(tmp_path, 333, frozenset()) is False

    time.sleep(0.02)
    admins.write_text(json.dumps([333]), encoding="utf-8")
    assert is_admin(tmp_path, 222, frozenset()) is False
    assert is_admin(tmp_path, 333, frozenset()) is True


def test_non_list_whitelist_and_admins_treated_as_empty(tmp_path: Path) -> None:
    (tmp_path / WHITELIST_FILE).write_text(json.dumps({"ids": [1]}), encoding="utf-8")
    assert is_user_whitelisted(tmp_path, 1) is False

    (tmp_path / ADMINS_FILE).write_text(json.dumps({"ids": [2]}), encoding="utf-8")
    assert is_admin(tmp_path, 2, frozenset()) is False


def test_whitelist_skips_non_int_entries(tmp_path: Path) -> None:
    (tmp_path / WHITELIST_FILE).write_text(
        json.dumps([1, "2", "nope", None, 3]),
        encoding="utf-8",
    )
    assert is_user_whitelisted(tmp_path, 1) is True
    assert is_user_whitelisted(tmp_path, 2) is True
    assert is_user_whitelisted(tmp_path, 3) is True


def test_remove_user_from_whitelist(tmp_path: Path) -> None:
    (tmp_path / WHITELIST_FILE).write_text(json.dumps([5, 6]), encoding="utf-8")
    assert remove_user_from_whitelist(tmp_path, 5) is True
    assert is_user_whitelisted(tmp_path, 5) is False
    assert is_user_whitelisted(tmp_path, 6) is True
    assert remove_user_from_whitelist(tmp_path, 5) is False


def test_token_ttl_constant() -> None:
    assert TOKEN_TTL_SECONDS == 300


def test_cmd_add_token_success_and_bad_token(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from ultron.cli import cmd_add_token

    token = register_pending_token(tmp_path, 55)
    monkeypatch.setattr(
        "ultron.cli.load_env",
        lambda: SimpleNamespace(state_dir=tmp_path),
    )
    assert cmd_add_token(token) == 0
    out = capsys.readouterr().out
    assert "55" in out
    assert is_user_whitelisted(tmp_path, 55) is True

    assert cmd_add_token("bogus-token") == 1
    err = capsys.readouterr().err
    assert "unknown token" in err
