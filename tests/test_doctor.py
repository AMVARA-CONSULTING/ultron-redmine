from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock

import pytest

_MINIMAL = """\
timezone: UTC
discord: {}
reports: {}
report_schedule: []
logging: {}
"""


def test_doctor_fails_when_config_missing(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("CONFIG_PATH", str(tmp_path / "missing.yaml"))
    from ultron.doctor import run_doctor

    assert run_doctor() == 1


def test_doctor_ok_without_discord_redmine_or_llm(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    cfg = tmp_path / "c.yaml"
    cfg.write_text(_MINIMAL, encoding="utf-8")
    monkeypatch.setenv("CONFIG_PATH", str(cfg))
    for k in ("DISCORD_TOKEN", "REDMINE_URL", "REDMINE_API_KEY", "LLM_API_KEY"):
        monkeypatch.delenv(k, raising=False)

    from ultron.doctor import run_doctor

    assert run_doctor() == 0


def test_doctor_reports_user_memory_health(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    cfg = tmp_path / "c.yaml"
    cfg.write_text(_MINIMAL, encoding="utf-8")
    state = tmp_path / "state"
    mem = state / "user_memory"
    mem.mkdir(parents=True)
    (mem / "user_111.json").write_text('{"version":1,"entries":{}}\n', encoding="utf-8")
    (mem / "user_222.json").write_text('{"version":1,"entries":{}}\n', encoding="utf-8")
    (mem / "notes.txt").write_text("ignore", encoding="utf-8")

    monkeypatch.setenv("CONFIG_PATH", str(cfg))
    monkeypatch.setenv("ULTRON_STATE_DIR", str(state))
    for k in ("DISCORD_TOKEN", "REDMINE_URL", "REDMINE_API_KEY", "LLM_API_KEY"):
        monkeypatch.delenv(k, raising=False)

    from ultron.doctor import run_doctor

    assert run_doctor() == 0
    out = capsys.readouterr().out
    assert "User memory" in out
    assert "directory:         present" in out
    assert "writable:          yes" in out
    assert "user_*.json files: 2" in out
    assert "free disk:" in out
    assert " — OK" in out
    # Must not dump JSON entry contents / secrets from memory files.
    assert '"entries"' not in out
    assert "notes.txt" not in out


def test_doctor_user_memory_missing_dir(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    cfg = tmp_path / "c.yaml"
    cfg.write_text(_MINIMAL, encoding="utf-8")
    state = tmp_path / "empty_state"
    state.mkdir()

    monkeypatch.setenv("CONFIG_PATH", str(cfg))
    monkeypatch.setenv("ULTRON_STATE_DIR", str(state))
    for k in ("DISCORD_TOKEN", "REDMINE_URL", "REDMINE_API_KEY", "LLM_API_KEY"):
        monkeypatch.delenv(k, raising=False)

    from ultron.doctor import run_doctor

    assert run_doctor() == 0
    out = capsys.readouterr().out
    assert "directory:         missing" in out
    assert "user_*.json files: 0" in out
    # Read-only: doctor must not create user_memory/.
    assert not (state / "user_memory").exists()


def test_doctor_user_memory_disk_low(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    cfg = tmp_path / "c.yaml"
    cfg.write_text(_MINIMAL, encoding="utf-8")
    state = tmp_path / "state"
    (state / "user_memory").mkdir(parents=True)

    monkeypatch.setenv("CONFIG_PATH", str(cfg))
    monkeypatch.setenv("ULTRON_STATE_DIR", str(state))
    for k in ("DISCORD_TOKEN", "REDMINE_URL", "REDMINE_API_KEY", "LLM_API_KEY"):
        monkeypatch.delenv(k, raising=False)

    class _Usage:
        free = 1024
        used = 0
        total = 2048

    monkeypatch.setattr("ultron.user_memory.shutil.disk_usage", lambda _p: _Usage())

    from ultron.doctor import run_doctor

    assert run_doctor() == 0
    out = capsys.readouterr().out
    assert "LOW (growth blocked)" in out


def test_doctor_redmine_fail_when_configured(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    cfg = tmp_path / "c.yaml"
    cfg.write_text(_MINIMAL, encoding="utf-8")
    monkeypatch.setenv("CONFIG_PATH", str(cfg))
    monkeypatch.delenv("DISCORD_TOKEN", raising=False)
    monkeypatch.setenv("REDMINE_URL", "https://redmine.example")
    monkeypatch.setenv("REDMINE_API_KEY", "k")
    monkeypatch.delenv("LLM_API_KEY", raising=False)

    from ultron.redmine import RedmineError

    monkeypatch.setattr(
        "ultron.doctor.RedmineClient.verify_connection",
        AsyncMock(side_effect=RedmineError("test failure")),
    )

    from ultron.doctor import run_doctor

    assert run_doctor() == 1


def test_doctor_redmine_ok_mocked(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    cfg = tmp_path / "c.yaml"
    cfg.write_text(_MINIMAL, encoding="utf-8")
    monkeypatch.setenv("CONFIG_PATH", str(cfg))
    monkeypatch.delenv("DISCORD_TOKEN", raising=False)
    monkeypatch.setenv("REDMINE_URL", "https://redmine.example")
    monkeypatch.setenv("REDMINE_API_KEY", "k")
    monkeypatch.delenv("LLM_API_KEY", raising=False)

    monkeypatch.setattr("ultron.doctor.RedmineClient.verify_connection", AsyncMock(return_value=None))
    monkeypatch.setattr(
        "ultron.doctor.RedmineClient.fetch_current_user_label",
        AsyncMock(return_value="alice"),
    )

    from ultron.doctor import run_doctor

    assert run_doctor() == 0


def test_load_env_without_discord_or_redmine_when_optional(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    cfg = tmp_path / "c.yaml"
    cfg.write_text(_MINIMAL, encoding="utf-8")
    monkeypatch.setenv("CONFIG_PATH", str(cfg))
    monkeypatch.delenv("DISCORD_TOKEN", raising=False)
    monkeypatch.delenv("REDMINE_URL", raising=False)
    monkeypatch.delenv("REDMINE_API_KEY", raising=False)
    monkeypatch.delenv("LLM_API_KEY", raising=False)

    from ultron.settings import load_env

    env = load_env(require_discord=False, require_redmine=False)
    assert env.discord_token == ""
    assert env.redmine_url == ""
    assert env.redmine_api_key == ""
