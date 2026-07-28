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


def test_summary_spanish_and_polite() -> None:
    for text, issue_id in (
        ("dame un resumen del ticket 42", 42),
        ("hazme un resumen de #55", 55),
        ("me puedes resumir #8", 8),
        ("podrias resumir el ticket 3", 3),
        ("can you summarize #123 please", 123),
        ("could you summarize ticket 5?", 5),
        ("quiero un resumen de #55", 55),
    ):
        out = try_nl_fastpath(text)
        assert isinstance(out, NLInvoke), text
        assert out.command == "summary"
        assert out.args["issue_id"] == issue_id


def test_exact_commands() -> None:
    assert try_nl_fastpath("ping").command == "ping"  # type: ignore[union-attr]
    assert try_nl_fastpath("ayuda").command == "help"  # type: ignore[union-attr]
    assert try_nl_fastpath("estado").command == "status"  # type: ignore[union-attr]


def test_ask_issue() -> None:
    out = try_nl_fastpath("ask about issue 55: who owns this?")
    assert isinstance(out, NLInvoke)
    assert out.command == "ask_issue"
    assert out.args["issue_id"] == 55
    assert "owns" in out.args["question"]

    es = try_nl_fastpath("pregunta sobre #12: quién es el assignee?")
    assert isinstance(es, NLInvoke)
    assert es.command == "ask_issue"
    assert es.args["issue_id"] == 12


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

    forget_es = try_nl_fastpath("olvida la clave preferred_project")
    assert isinstance(forget_es, NLMemoryClear)
    assert forget_es.key == "preferred_project"

    show = try_nl_fastpath("show memory")
    assert isinstance(show, NLMemoryShow)

    for text in (
        "muéstrame la memoria",
        "muestra mi memoria",
        "ver memoria",
        "qué recuerdas",
    ):
        assert isinstance(try_nl_fastpath(text), NLMemoryShow), text


def test_remember_nostalgia_falls_through() -> None:
    """Conversational 'remember when…' must not become a memory write."""
    for text in (
        "remember when we shipped the bot",
        "remember the time we fixed prod",
        "remember how we deployed this",
        "recuerda cuando desplegamos",
        "te acuerdas cuando arreglamos prod",
    ):
        assert try_nl_fastpath(text) is None, text


def test_summary_negation_falls_through() -> None:
    """Incidental #N + summary wording with negation → LLM, not summary."""
    for text in (
        "I do not want a summary of #123 right now",
        "no quiero un resumen de #99 ahora",
        "not a summary of ticket 5",
        "ignore summary for #1",
    ):
        assert try_nl_fastpath(text) is None, text


def test_long_prose_with_incidental_issue_falls_through() -> None:
    assert try_nl_fastpath("Please invent a poem about #123 and servers") is None
    assert (
        try_nl_fastpath(
            "While reading docs about ticket #7001 I wondered about architecture"
        )
        is None
    )


def test_compound_style_message_falls_through() -> None:
    """Amvara+Redmine compounds belong to prefilter; fast-path must return None."""
    assert (
        try_nl_fastpath("Can you look at ticket #7001 and also check amvara1?") is None
    )


def test_reply_context_separator_keeps_user_half() -> None:
    out = try_nl_fastpath("Bot said something long about the outage\n\n---\n\nsummarize #42")
    assert isinstance(out, NLInvoke)
    assert out.command == "summary"
    assert out.args["issue_id"] == 42

    # User half is nostalgia → still fall through after strip.
    assert (
        try_nl_fastpath("Earlier reply excerpt\n\n---\n\nremember when we were young")
        is None
    )


def test_non_match_falls_through() -> None:
    assert try_nl_fastpath("please invent a poem about servers") is None
