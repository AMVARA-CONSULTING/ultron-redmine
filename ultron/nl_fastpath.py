"""Deterministic NL routing without an LLM call.

Why: Gemma-class models are slow and unreliable for obvious intents
(``summarize #123``, ``ping``, remember/forget). Code-first fast-path saves
tokens and latency; the LLM router remains the fallback.

How used: ``UltronBot._handle_nl_chat_message`` / redmine router calls
``try_nl_fastpath`` before ``run_nl_router``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from ultron.amvara.prefilter import extract_issue_ids
from ultron.nl_router import NLInvoke, NLRouterOutcome

# Bare ping/help/status (whole message after mention strip).
_EXACT_CMD = re.compile(
    r"^\s*(ping|help|status|ayuda|estado)\s*[.!?]*\s*$",
    re.IGNORECASE,
)

# summarize / resume ticket #N  OR  resumen del ticket 123
_SUMMARY_RE = re.compile(
    r"^\s*(?:(?:please|por\s+favor)\s+)?"
    r"(?:summar(?:y|ize|ise)|resum(?:e|en|ir)|sumariz(?:a|ar))"
    r"(?:\s+(?:of|del|de|the|el|la|este|esta))?"
    r"(?:\s+(?:ticket|issue|incidente|tarea))?"
    r"\s*#?\s*(\d{1,9})\s*[.!?]*\s*$",
    re.IGNORECASE,
)

# #123 alone or "ticket 123" / "issue #123" → summary
_BARE_ISSUE_RE = re.compile(
    r"^\s*(?:(?:ticket|issue|incidente|tarea)\s+)?#?\s*(\d{1,9})\s*[.!?]*\s*$",
    re.IGNORECASE,
)

# ask about issue N: question  /  pregunta sobre #N …
_ASK_RE = re.compile(
    r"^\s*(?:ask(?:\s+about)?|pregunta(?:r)?(?:\s+sobre)?|"
    r"qu[eé]\s+(?:sabes|hay)|what\s+(?:about|is))"
    r"(?:\s+(?:ticket|issue|incidente|tarea))?"
    r"\s*#?\s*(\d{1,9})\s*[:\-]?\s+(.+?)\s*$",
    re.IGNORECASE | re.DOTALL,
)

# remember key: value  /  recuerda que …
_REMEMBER_KEY_RE = re.compile(
    r"^\s*(?:remember|recuerda(?:\s+que)?|memoriza)\s+"
    r"(?:(?:that|que)\s+)?"
    r"(?:key\s+)?([a-zA-Z][a-zA-Z0-9_.-]{0,63})\s*[:=]\s*(.+?)\s*$",
    re.IGNORECASE | re.DOTALL,
)
_REMEMBER_FREE_RE = re.compile(
    r"^\s*(?:remember|recuerda(?:\s+que)?|memoriza)\s+(?:that\s+|que\s+)?(.+?)\s*$",
    re.IGNORECASE | re.DOTALL,
)

# forget key / olvida todo
_FORGET_ALL_RE = re.compile(
    r"^\s*(?:forget|olvida(?:r)?)\s+(?:all|todo|everything)\s*$",
    re.IGNORECASE,
)
_FORGET_KEY_RE = re.compile(
    r"^\s*(?:forget|olvida(?:r)?)\s+(?:key\s+)?([a-zA-Z][a-zA-Z0-9_.-]{0,63})\s*$",
    re.IGNORECASE,
)

# show memory
_SHOW_MEMORY_RE = re.compile(
    r"^\s*(?:(?:show|list|ver|muestra(?:me)?)\s+)?(?:my\s+)?memory\b|"
    r"^\s*(?:qu[eé]\s+recuerdas|what\s+do\s+you\s+remember)\s*$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class NLMemoryUpdate:
    """Fast-path: persist a standing note for the Discord user."""

    key: str
    content: str


@dataclass(frozen=True)
class NLMemoryClear:
    """Fast-path: clear one key or all memory for the Discord user."""

    key: str | None
    clear_all: bool


@dataclass(frozen=True)
class NLMemoryShow:
    """Fast-path: list the user's durable memory."""


NLFastpathOutcome = NLRouterOutcome | NLMemoryUpdate | NLMemoryClear | NLMemoryShow


def _slug_key_from_text(text: str) -> str:
    """Build a stable memory key from free-form remember text."""
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9]*", text)
    if not words:
        return "note"
    base = "_".join(w.lower() for w in words[:4])
    return base[:64] or "note"


def try_nl_fastpath(user_text: str) -> NLFastpathOutcome | None:
    """Return a deterministic outcome when the intent is obvious; else None.

    Does not call the LLM. Callers should fall back to ``run_nl_router``.
    """
    ut = (user_text or "").strip()
    if not ut:
        return None

    # Drop a leading replied-to block if present (--- separator from reply context).
    if "\n\n---\n\n" in ut:
        ut = ut.split("\n\n---\n\n", 1)[-1].strip()

    m = _EXACT_CMD.match(ut)
    if m:
        cmd = m.group(1).casefold()
        if cmd in ("ayuda",):
            cmd = "help"
        if cmd in ("estado",):
            cmd = "status"
        return NLInvoke(command=cmd, args={})

    if _SHOW_MEMORY_RE.search(ut) and len(ut) < 80:
        return NLMemoryShow()

    if _FORGET_ALL_RE.match(ut):
        return NLMemoryClear(key=None, clear_all=True)
    m = _FORGET_KEY_RE.match(ut)
    if m:
        return NLMemoryClear(key=m.group(1), clear_all=False)

    m = _REMEMBER_KEY_RE.match(ut)
    if m:
        return NLMemoryUpdate(key=m.group(1).strip(), content=m.group(2).strip())
    m = _REMEMBER_FREE_RE.match(ut)
    if m:
        content = m.group(1).strip()
        if content:
            return NLMemoryUpdate(key=_slug_key_from_text(content), content=content)

    m = _SUMMARY_RE.match(ut)
    if m:
        return NLInvoke(command="summary", args={"issue_id": int(m.group(1))})

    m = _ASK_RE.match(ut)
    if m:
        return NLInvoke(
            command="ask_issue",
            args={"issue_id": int(m.group(1)), "question": m.group(2).strip()},
        )

    m = _BARE_ISSUE_RE.match(ut)
    if m:
        return NLInvoke(command="summary", args={"issue_id": int(m.group(1))})

    # Single issue id + clear summary verb somewhere (short messages only).
    ids = extract_issue_ids(ut)
    if len(ids) == 1 and len(ut) <= 80:
        if re.search(
            r"\b(summar(?:y|ize|ise)|resum(?:e|en|ir)|sumariz)",
            ut,
            re.IGNORECASE,
        ):
            return NLInvoke(command="summary", args={"issue_id": ids[0]})

    return None
