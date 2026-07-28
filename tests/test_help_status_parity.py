"""Help text and /status parity for Ultron 3.0 memory / confirm / fast-path."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

from ultron.bot import _HELP_TEXT, _format_status_message
from ultron.config import (
    AppConfig,
    DiscordConfig,
    EnvironmentBindings,
    LoggingConfig,
    ReportsConfig,
)
from ultron.llm import NullLLMBackend
from ultron.settings import EnvSettings
from ultron.user_memory import UserMemoryStore


def test_help_text_lists_memory_confirm_and_fastpath() -> None:
    help_l = _HELP_TEXT.lower()
    assert "/remember" in _HELP_TEXT
    assert "/forget" in _HELP_TEXT
    assert "/memory" in _HELP_TEXT
    assert "clear_all" in help_l
    assert "confirm" in help_l
    assert "fast-path" in help_l or "fast path" in help_l
    for cmd in ("/new_ticket", "/log_time", "/note"):
        assert cmd in _HELP_TEXT


def test_format_status_includes_user_memory_line(tmp_path: Path) -> None:
    store = UserMemoryStore(tmp_path, min_free_bytes=0)
    store.update(10, "pref", "value")
    env = EnvSettings(
        discord_token="x",
        discord_guild_id=None,
        discord_application_id=None,
        redmine_url="https://redmine.example/",
        redmine_api_key="k",
        llm_enabled=False,
        llm_base_url="",
        llm_api_key="",
        llm_model="(none)",
        config_path="config.yaml",
        state_dir=tmp_path,
        bot_owner_contact=None,
        discord_admin_ids=frozenset(),
        discord_message_content_intent=False,
        ultron_nl_commands=False,
        environment_bindings=EnvironmentBindings(),
        ultron_project_root=tmp_path,
        self_upgrade_prompt_path=None,
        self_upgrade_timeout_seconds=1800,
        self_repair_enabled=False,
        systemd_unit="ultron.service",
    )
    app_cfg = AppConfig(
        timezone="UTC",
        discord=DiscordConfig(nl_commands=False),
        reports=ReportsConfig(),
        report_schedule=(),
        logging=LoggingConfig(),
    )
    bot = SimpleNamespace(
        latency=0.05,
        user=SimpleNamespace(name="UltronTest", id=999),
        user_memory=store,
    )
    body = _format_status_message(
        env=env,
        app_cfg=app_cfg,
        llm=NullLLMBackend(),
        bot=bot,  # type: ignore[arg-type]
        ready_at_utc=datetime.now(timezone.utc),
        guild=None,
    )
    assert "user_memory:** ready (1 files)" in body
    assert "redmine.example" in body
