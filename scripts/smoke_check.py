#!/usr/bin/env python3
"""Connectivity + Ultron 3.0 offline checks (no Discord).

Run from repo root::

    python scripts/smoke_check.py

Always runs offline checks (version ≥ 3.0.0, ``UserMemoryStore``, NL fast-path,
write-confirm helpers). Optionally probes Redmine/LLM when ``.env`` has credentials.
"""
from __future__ import annotations

import asyncio
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

from ultron.llm import LLMBackend, NullLLMBackend, format_llm_endpoint
from ultron.llm_cursor_fallback import LLMWithCursorAgentFallback, llm_chain_client

_MIN_VERSION = (3, 0, 0)


def _parse_semver(version: str) -> tuple[int, int, int]:
    """Parse ``major.minor.patch`` from a version string (ignore pre/build tags)."""
    core = version.strip().split("+", 1)[0].split("-", 1)[0]
    parts = re.split(r"[^\d]+", core)
    nums = [int(p) for p in parts if p.isdigit()]
    while len(nums) < 3:
        nums.append(0)
    return nums[0], nums[1], nums[2]


def check_ultron30_offline() -> bool:
    """Validate Ultron 3.0 memory / fast-path / confirm pieces without Discord.

    Returns True when all offline checks pass.
    """
    ok = True

    try:
        from ultron import __version__
        from ultron.nl_fastpath import NLInvoke, NLMemoryUpdate, try_nl_fastpath
        from ultron.user_memory import UserMemoryStore
        from ultron.write_confirm import (
            ConfirmResult,
            author_may_confirm,
            format_write_abort_message,
            format_write_confirm_prompt,
        )
    except Exception as e:
        print(f"FAIL Ultron 3.0 offline: import error: {e}")
        return False

    ver = _parse_semver(__version__)
    if ver < _MIN_VERSION:
        print(f"FAIL version: {__version__!r} < 3.0.0")
        ok = False
    else:
        print(f"OK version: {__version__} (>= 3.0.0)")

    try:
        with tempfile.TemporaryDirectory(prefix="ultron-smoke-mem-") as tmp:
            store = UserMemoryStore(tmp, min_free_bytes=0)
            store.update(42, "preferred_project", "10_AMVARA")
            entries = store.list_entries(42)
            if entries.get("preferred_project") != "10_AMVARA":
                raise AssertionError(f"unexpected entries: {entries!r}")
            block = store.format_for_prompt(42)
            if "preferred_project" not in block or "10_AMVARA" not in block:
                raise AssertionError(f"prompt block missing prefs: {block!r}")
            store.clear(42, key="preferred_project")
            if store.list_entries(42):
                raise AssertionError("expected empty memory after forget")
            status = store.status_line()
            if "user_memory" not in status:
                raise AssertionError(f"bad status line: {status!r}")
        print("OK user_memory: UserMemoryStore update/list/forget/prompt")
    except Exception as e:
        print(f"FAIL user_memory: {e}")
        ok = False

    try:
        summary = try_nl_fastpath("summarize #7001")
        if not isinstance(summary, NLInvoke) or summary.command != "summary":
            raise AssertionError(f"expected summary invoke, got {summary!r}")
        if int(summary.args.get("issue_id", -1)) != 7001:
            raise AssertionError(f"bad issue_id: {summary!r}")
        remember = try_nl_fastpath("remember preferred_project: 10_AMVARA")
        if not isinstance(remember, NLMemoryUpdate):
            raise AssertionError(f"expected NLMemoryUpdate, got {remember!r}")
        if remember.key != "preferred_project" or "10_AMVARA" not in remember.content:
            raise AssertionError(f"bad remember outcome: {remember!r}")
        if try_nl_fastpath("please invent a poem about servers") is not None:
            raise AssertionError("non-fastpath text should return None")
        print("OK nl_fastpath: summarize + remember + miss")
    except Exception as e:
        print(f"FAIL nl_fastpath: {e}")
        ok = False

    try:
        prompt = format_write_confirm_prompt("Log 0.1h on #1")
        if "Confirm Redmine write" not in prompt or "Log 0.1h" not in prompt:
            raise AssertionError(f"bad confirm prompt: {prompt!r}")
        if not author_may_confirm(author_id=1, clicker_id=1):
            raise AssertionError("author should confirm own write")
        if author_may_confirm(author_id=1, clicker_id=2):
            raise AssertionError("other user must not confirm")
        abort = format_write_abort_message(
            ConfirmResult.CANCEL, nothing_written="no time was logged"
        )
        if "Cancelled" not in abort or "no time was logged" not in abort:
            raise AssertionError(f"bad abort message: {abort!r}")
        print("OK write_confirm: prompt + author check + abort copy")
    except Exception as e:
        print(f"FAIL write_confirm: {e}")
        ok = False

    return ok


async def report_llm(llm: LLMBackend) -> None:
    """Ping the chain primary (unwrap cursor-agent fallback). Print OK / SKIP."""
    if isinstance(llm, NullLLMBackend):
        print("SKIP LLM: not configured")
        return
    chain = llm_chain_client(llm)
    if chain is None:
        print(f"SKIP LLM: unexpected backend {type(llm).__name__}")
        return
    await chain.ping_primary()
    ep = format_llm_endpoint(chain.primary_base_url)
    fb = " + cursor-agent LLM fallback" if isinstance(llm, LLMWithCursorAgentFallback) else ""
    print(f"OK LLM: chain primary model={chain.model!r} @ {ep}{fb}")


def main() -> int:
    load_dotenv(ROOT / ".env")

    ok = check_ultron30_offline()

    try:
        from ultron.settings import load_env

        env = load_env()
    except RuntimeError as e:
        print(f"FAIL bootstrap: {e}")
        return 1

    redmine_url = env.redmine_url.rstrip("/")
    redmine_key = env.redmine_api_key

    if not redmine_url or not redmine_key:
        print("SKIP Redmine: missing URL or API key (via config environment_bindings)")
    else:
        import httpx

        try:
            r = httpx.get(
                f"{redmine_url}/issues.json",
                params={"limit": 1},
                headers={"X-Redmine-API-Key": redmine_key},
                timeout=30.0,
            )
            r.raise_for_status()
            n = len(r.json().get("issues", []))
            print(f"OK Redmine: GET /issues.json limit=1 -> {r.status_code}, issues in page: {n}")
        except Exception as e:
            print(f"FAIL Redmine: {e}")
            ok = False

    if not env.llm_enabled:
        print("SKIP LLM: not configured (no enabled llm_chain in config.yaml)")
        return 0 if ok else 1

    async def llm_ping() -> None:
        from ultron.config import load_config
        from ultron.startup_llm import build_llm_backend

        cfg_path = Path(env.config_path).expanduser()
        if not cfg_path.is_file():
            print(f"SKIP LLM: config file not found ({cfg_path})")
            return
        cfg = load_config(cfg_path)
        built = build_llm_backend(env, cfg)
        await report_llm(built.backend)

    try:
        asyncio.run(llm_ping())
    except Exception as e:
        print(f"FAIL LLM: {e}")
        ok = False

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
