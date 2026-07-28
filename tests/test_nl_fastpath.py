"""Tests for deterministic NL fast-path (no LLM)."""

from __future__ import annotations

from ultron.nl_fastpath import (
    NLMemoryClear,
    NLMemoryShow,
    NLMemoryUpdate,
    try_nl_fastpath,
)
from ultron.nl_router import NLInvoke


def test_summary_patterns() -> None:
    out = try_nl_fastpath("summarize ticket 7001")
    assert isinstance(out, NLInvoke)
    assert out.command == "summary"
    assert out.args["issue_id"] == 7001

    out2 = try_nl_fastpath("resume #1234")
    assert isinstance(out2, NLInvoke)
    assert out2.args["issue_id"] == 1234

    out3 = try_nl_fastpath("#99")
    assert isinstance(out3, NLInvoke)
    assert out3.command == "summary"
    assert out3.args["issue_id"] == 99


def test_exact_commands() -> None:
    assert try_nl_fastpath("ping").command == "ping"  # type: ignore[union-attr]
    assert try_nl_fastpath("ayuda").command == "help"  # type: ignore[union-attr]


def test_ask_issue() -> None:
    out = try_nl_fastpath("ask about issue 55: who owns this?")
    assert isinstance(out, NLInvoke)
    assert out.command == "ask_issue"
    assert out.args["issue_id"] == 55
    assert "owns" in out.args["question"]


def test_remember_forget_show() -> None:
    up = try_nl_fastpath("remember preferred_project: 10_AMVARA")
    assert isinstance(up, NLMemoryUpdate)
    assert up.key == "preferred_project"
    assert up.content == "10_AMVARA"

    free = try_nl_fastpath("recuerda que default language is Spanish")
    assert isinstance(free, NLMemoryUpdate)
    assert "Spanish" in free.content

    forget = try_nl_fastpath("forget preferred_project")
    assert isinstance(forget, NLMemoryClear)
    assert forget.key == "preferred_project"

    show = try_nl_fastpath("show memory")
    assert isinstance(show, NLMemoryShow)


def test_non_match_falls_through() -> None:
    assert try_nl_fastpath("please invent a poem about servers") is None
