from __future__ import annotations

import stat
from pathlib import Path

import pytest

from ultron.config import CursorAgentConfig
from ultron.cursor_agent import resolve_cursor_agent_bin


def _make_executable(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("#!/bin/sh\n", encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


def test_resolve_prefers_env_override(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    env_bin = _make_executable(tmp_path / "env-cursor-agent")
    cfg_bin = _make_executable(tmp_path / "cfg-cursor-agent")
    monkeypatch.setenv("ULTRON_CURSOR_AGENT_BIN", str(env_bin))
    monkeypatch.setattr("ultron.cursor_agent.shutil.which", lambda _name: str(cfg_bin))

    got = resolve_cursor_agent_bin(CursorAgentConfig(bin_path=str(cfg_bin)))
    assert got == str(env_bin.resolve())


def test_resolve_raises_on_non_executable_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bad = tmp_path / "not-exec"
    bad.write_text("x", encoding="utf-8")
    bad.chmod(stat.S_IRUSR | stat.S_IWUSR)
    monkeypatch.setenv("ULTRON_CURSOR_AGENT_BIN", str(bad))

    with pytest.raises(RuntimeError, match="ULTRON_CURSOR_AGENT_BIN is not executable"):
        resolve_cursor_agent_bin(CursorAgentConfig())


def test_resolve_prefers_bin_path_when_executable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cfg_bin = _make_executable(tmp_path / "cfg-cursor-agent")
    monkeypatch.delenv("ULTRON_CURSOR_AGENT_BIN", raising=False)
    monkeypatch.setattr("ultron.cursor_agent.shutil.which", lambda _name: None)
    monkeypatch.setattr("ultron.cursor_agent.Path.home", lambda: tmp_path / "no-home")

    got = resolve_cursor_agent_bin(CursorAgentConfig(bin_path=str(cfg_bin)))
    assert got == str(cfg_bin.resolve())


def test_resolve_raises_on_non_executable_bin_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bad = tmp_path / "cfg-not-exec"
    bad.write_text("x", encoding="utf-8")
    bad.chmod(stat.S_IRUSR | stat.S_IWUSR)
    monkeypatch.delenv("ULTRON_CURSOR_AGENT_BIN", raising=False)

    with pytest.raises(RuntimeError, match="cursor_agent.bin_path is not executable"):
        resolve_cursor_agent_bin(CursorAgentConfig(bin_path=str(bad)))


def test_resolve_falls_through_to_which(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path_bin = _make_executable(tmp_path / "path-cursor-agent")
    monkeypatch.delenv("ULTRON_CURSOR_AGENT_BIN", raising=False)
    monkeypatch.setattr(
        "ultron.cursor_agent.shutil.which",
        lambda name: str(path_bin) if name == "cursor-agent" else None,
    )

    got = resolve_cursor_agent_bin(CursorAgentConfig())
    assert got == str(path_bin)


def test_resolve_falls_through_to_local_bin(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    local_bin = _make_executable(tmp_path / ".local" / "bin" / "cursor-agent")
    monkeypatch.delenv("ULTRON_CURSOR_AGENT_BIN", raising=False)
    monkeypatch.setattr("ultron.cursor_agent.shutil.which", lambda _name: None)
    monkeypatch.setattr("ultron.cursor_agent.Path.home", lambda: tmp_path)

    got = resolve_cursor_agent_bin(CursorAgentConfig())
    assert got == str(local_bin.resolve())


def test_resolve_missing_raises_clear_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("ULTRON_CURSOR_AGENT_BIN", raising=False)
    monkeypatch.setattr("ultron.cursor_agent.shutil.which", lambda _name: None)
    monkeypatch.setattr("ultron.cursor_agent.Path.home", lambda: tmp_path)

    with pytest.raises(RuntimeError, match="cursor-agent not found on PATH"):
        resolve_cursor_agent_bin(CursorAgentConfig())
