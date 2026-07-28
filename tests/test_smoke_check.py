from __future__ import annotations

import asyncio
import importlib.util
from pathlib import Path
from unittest.mock import AsyncMock

from ultron.config import (
    AppConfig,
    CursorAgentConfig,
    DiscordConfig,
    LLMProviderResolved,
    LoggingConfig,
    ReportsConfig,
)
from ultron.llm import LLMChainClient, NullLLMBackend
from ultron.llm_cursor_fallback import LLMWithCursorAgentFallback

_ROOT = Path(__file__).resolve().parents[1]


def _load_smoke_check():
    path = _ROOT / "scripts" / "smoke_check.py"
    spec = importlib.util.spec_from_file_location("ultron_smoke_check", path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _app() -> AppConfig:
    return AppConfig(
        timezone="UTC",
        discord=DiscordConfig(),
        reports=ReportsConfig(),
        report_schedule=(),
        logging=LoggingConfig(),
        cursor_agent=CursorAgentConfig(
            enabled=True,
            llm_fallback_enabled=True,
            llm_fallback_timeout_seconds=60.0,
        ),
    )


def _chain() -> LLMChainClient:
    return LLMChainClient.from_resolved(
        (
            LLMProviderResolved(
                base_url="http://127.0.0.1:11434/v1",
                models=("gemma",),
                api_key="ollama",
                timeout_seconds=10.0,
                max_retries=0,
                name="ollama",
            ),
        )
    )


def test_report_llm_unwraps_cursor_fallback(capsys) -> None:
    smoke = _load_smoke_check()
    chain = _chain()
    chain.ping_primary = AsyncMock(return_value=None)  # type: ignore[method-assign]
    wrapped = LLMWithCursorAgentFallback(
        primary=chain,
        app_cfg=_app(),
        state_dir=Path("/tmp"),
        workspace=Path("/tmp"),
        timeout_seconds=60.0,
    )

    asyncio.run(smoke.report_llm(wrapped))
    out = capsys.readouterr().out
    assert "unexpected backend" not in out
    assert "OK LLM:" in out
    assert "gemma" in out
    assert "cursor-agent LLM fallback" in out
    chain.ping_primary.assert_awaited_once()


def test_report_llm_bare_chain(capsys) -> None:
    smoke = _load_smoke_check()
    chain = _chain()
    chain.ping_primary = AsyncMock(return_value=None)  # type: ignore[method-assign]

    asyncio.run(smoke.report_llm(chain))
    out = capsys.readouterr().out
    assert "OK LLM:" in out
    assert "cursor-agent LLM fallback" not in out
    chain.ping_primary.assert_awaited_once()


def test_report_llm_null_skips(capsys) -> None:
    smoke = _load_smoke_check()
    asyncio.run(smoke.report_llm(NullLLMBackend()))
    out = capsys.readouterr().out
    assert out.strip() == "SKIP LLM: not configured"


def test_report_llm_unknown_backend(capsys) -> None:
    smoke = _load_smoke_check()

    class WeirdBackend:
        model = "x"

        async def complete(self, **kwargs):  # noqa: ANN003
            return ""

    asyncio.run(smoke.report_llm(WeirdBackend()))  # type: ignore[arg-type]
    out = capsys.readouterr().out
    assert "SKIP LLM: unexpected backend WeirdBackend" in out


def test_parse_semver() -> None:
    smoke = _load_smoke_check()
    assert smoke._parse_semver("3.0.6") == (3, 0, 6)
    assert smoke._parse_semver("3.0.0+local") == (3, 0, 0)
    assert smoke._parse_semver("2.9.9") == (2, 9, 9)


def test_check_ultron30_offline(capsys) -> None:
    smoke = _load_smoke_check()
    assert smoke.check_ultron30_offline() is True
    out = capsys.readouterr().out
    assert "OK version:" in out
    assert "OK user_memory:" in out
    assert "OK nl_fastpath:" in out
    assert "OK write_confirm:" in out
    assert "FAIL" not in out
