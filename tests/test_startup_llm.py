from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from ultron.config import (
    AppConfig,
    CursorAgentConfig,
    DiscordConfig,
    EnvironmentBindings,
    LLMProviderResolved,
    LLMProviderSpec,
    LoggingConfig,
    ReportsConfig,
)
from ultron.llm import LLMChainClient, NullLLMBackend
from ultron.llm_cursor_fallback import LLMWithCursorAgentFallback
from ultron.settings import EnvSettings
from ultron.startup_llm import build_llm_backend


def _env(tmp_path: Path, *, project_root: Path | None = None) -> EnvSettings:
    root = project_root if project_root is not None else tmp_path
    return EnvSettings(
        discord_token="t",
        discord_guild_id=None,
        discord_application_id=None,
        redmine_url="https://redmine.example",
        redmine_api_key="k",
        llm_enabled=False,
        llm_base_url="",
        llm_api_key="",
        llm_model="(none)",
        config_path=str(tmp_path / "config.yaml"),
        state_dir=tmp_path / "data",
        bot_owner_contact=None,
        discord_admin_ids=frozenset(),
        discord_message_content_intent=False,
        ultron_nl_commands=False,
        environment_bindings=EnvironmentBindings(),
        ultron_project_root=root,
        self_upgrade_prompt_path=None,
        self_upgrade_timeout_seconds=600,
        self_repair_enabled=True,
        systemd_unit="ultron.service",
    )


def _app(
    *,
    llm_chain: tuple[LLMProviderSpec, ...] | None = None,
    cursor_enabled: bool = False,
    llm_fallback_enabled: bool = False,
    workspace: str = "",
    llm_fallback_timeout_seconds: float = 90.0,
) -> AppConfig:
    return AppConfig(
        timezone="UTC",
        discord=DiscordConfig(),
        reports=ReportsConfig(),
        report_schedule=(),
        logging=LoggingConfig(),
        llm_chain=llm_chain,
        cursor_agent=CursorAgentConfig(
            enabled=cursor_enabled,
            llm_fallback_enabled=llm_fallback_enabled,
            workspace=workspace,
            llm_fallback_timeout_seconds=llm_fallback_timeout_seconds,
        ),
    )


def _fake_resolved() -> tuple[LLMProviderResolved, ...]:
    return (
        LLMProviderResolved(
            base_url="http://127.0.0.1:11434/v1",
            models=("gemma",),
            api_key="ollama",
            timeout_seconds=10.0,
            max_retries=0,
            name="ollama",
        ),
    )


def test_build_llm_backend_null_when_no_chain(tmp_path: Path) -> None:
    built = build_llm_backend(_env(tmp_path), _app())
    assert isinstance(built.backend, NullLLMBackend)
    assert built.resolved_chain is None


def test_build_llm_backend_chain_client_when_chain_configured(tmp_path: Path) -> None:
    specs = (
        LLMProviderSpec(
            base_url="http://127.0.0.1:11434/v1",
            models=("gemma",),
            api_key_env="OLLAMA_KEY",
            timeout_seconds=10.0,
            max_retries=0,
            name="ollama",
        ),
    )
    resolved = _fake_resolved()
    with patch("ultron.startup_llm.resolve_llm_chain", return_value=resolved) as resolve:
        built = build_llm_backend(_env(tmp_path), _app(llm_chain=specs))

    resolve.assert_called_once_with(specs)
    assert isinstance(built.backend, LLMChainClient)
    assert built.resolved_chain is resolved
    assert built.backend.model == "gemma"


def test_build_llm_backend_wraps_cursor_fallback(tmp_path: Path) -> None:
    ws = tmp_path / "llm-ws"
    ws.mkdir()
    (tmp_path / "data").mkdir()
    built = build_llm_backend(
        _env(tmp_path),
        _app(
            cursor_enabled=True,
            llm_fallback_enabled=True,
            workspace=str(ws),
            llm_fallback_timeout_seconds=75.0,
        ),
    )
    assert isinstance(built.backend, LLMWithCursorAgentFallback)
    assert isinstance(built.backend.primary, NullLLMBackend)
    assert built.resolved_chain is None
    assert built.backend.workspace == ws.resolve()
    assert built.backend.timeout_seconds == 75.0
    assert built.backend.state_dir == (tmp_path / "data").resolve()


def test_build_llm_backend_default_workspace_under_state_dir(tmp_path: Path) -> None:
    (tmp_path / "data").mkdir()
    built = build_llm_backend(
        _env(tmp_path),
        _app(cursor_enabled=True, llm_fallback_enabled=True, workspace=""),
    )
    assert isinstance(built.backend, LLMWithCursorAgentFallback)
    assert built.backend.workspace == (tmp_path / "data" / "cursor-agent-llm").resolve()


def test_build_llm_backend_no_wrap_when_fallback_disabled(tmp_path: Path) -> None:
    built = build_llm_backend(
        _env(tmp_path),
        _app(cursor_enabled=True, llm_fallback_enabled=False),
    )
    assert isinstance(built.backend, NullLLMBackend)


def test_build_llm_backend_no_wrap_when_cursor_agent_disabled(tmp_path: Path) -> None:
    specs = (
        LLMProviderSpec(
            base_url="http://127.0.0.1:11434/v1",
            models=("gemma",),
            api_key_env="OLLAMA_KEY",
            timeout_seconds=10.0,
            max_retries=0,
            name="ollama",
        ),
    )
    resolved = _fake_resolved()
    with patch("ultron.startup_llm.resolve_llm_chain", return_value=resolved):
        built = build_llm_backend(
            _env(tmp_path),
            _app(llm_chain=specs, cursor_enabled=False, llm_fallback_enabled=True),
        )
    assert isinstance(built.backend, LLMChainClient)
    assert not isinstance(built.backend, LLMWithCursorAgentFallback)
    assert built.resolved_chain is resolved


def test_build_llm_backend_wraps_chain_when_both_enabled(tmp_path: Path) -> None:
    specs = (
        LLMProviderSpec(
            base_url="http://127.0.0.1:11434/v1",
            models=("gemma",),
            api_key_env="OLLAMA_KEY",
            timeout_seconds=10.0,
            max_retries=0,
            name="ollama",
        ),
    )
    resolved = _fake_resolved()
    ws = tmp_path / "ws"
    ws.mkdir()
    (tmp_path / "data").mkdir()
    with patch("ultron.startup_llm.resolve_llm_chain", return_value=resolved):
        built = build_llm_backend(
            _env(tmp_path),
            _app(
                llm_chain=specs,
                cursor_enabled=True,
                llm_fallback_enabled=True,
                workspace=str(ws),
            ),
        )
    assert isinstance(built.backend, LLMWithCursorAgentFallback)
    assert isinstance(built.backend.primary, LLMChainClient)
    assert built.resolved_chain is resolved
