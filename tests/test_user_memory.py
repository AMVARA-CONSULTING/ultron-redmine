"""Tests for per-user durable memory with disk-space growth guards."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from ultron.user_memory import (
    MemoryDiskFullError,
    MemoryValidationError,
    UserMemoryStore,
)


def test_update_list_forget_roundtrip(tmp_path: Path) -> None:
    store = UserMemoryStore(tmp_path, min_free_bytes=0)
    store.update(42, "preferred_project", "10_AMVARA")
    entries = store.list_entries(42)
    assert entries["preferred_project"] == "10_AMVARA"
    block = store.format_for_prompt(42)
    assert "preferred_project" in block
    assert "10_AMVARA" in block
    msg = store.clear(42, key="preferred_project")
    assert "Forgot" in msg
    assert store.list_entries(42) == {}


def test_rejects_bad_key(tmp_path: Path) -> None:
    store = UserMemoryStore(tmp_path, min_free_bytes=0)
    with pytest.raises(MemoryValidationError):
        store.update(1, "1bad", "x")


def test_max_entries(tmp_path: Path) -> None:
    store = UserMemoryStore(tmp_path, min_free_bytes=0, max_entries=2)
    store.update(7, "a", "one")
    store.update(7, "b", "two")
    with pytest.raises(MemoryValidationError):
        store.update(7, "c", "three")


def test_growth_blocked_when_disk_low(tmp_path: Path) -> None:
    store = UserMemoryStore(tmp_path, min_free_bytes=10**15)
    with pytest.raises(MemoryDiskFullError):
        store.update(9, "pref", "hello")


def test_shrink_allowed_when_disk_low(tmp_path: Path) -> None:
    store = UserMemoryStore(tmp_path, min_free_bytes=0)
    store.update(9, "pref", "hello world")
    store.min_free_bytes = 10**15
    # Clearing shrinks — must still work.
    msg = store.clear(9, key="pref")
    assert "Forgot" in msg


def test_assert_can_grow_file_cap(tmp_path: Path) -> None:
    store = UserMemoryStore(tmp_path, min_free_bytes=0, max_file_bytes=2048)
    with patch.object(store, "free_disk_bytes", return_value=10**12):
        with pytest.raises(MemoryDiskFullError):
            store.assert_can_grow(current_bytes=0, new_bytes=4096)
