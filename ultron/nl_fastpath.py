"""Deterministic NL routing without an LLM call.

Why: Gemma-class models are slow and unreliable for obvious intents
(``summarize #123``, ``ping``, remember/forget). Code-first fast-path saves
tokens and latency; the LLM router remains the fallback.

How used: ``UltronBot._handle_nl_chat_message`` / redmine router calls
``try_nl_fastpath`` before ``run_nl_router``. Compound/Amvara intents are
classified by the prefilter *before* the redmine router, so this module never
sees those messages.
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

# Polite / request prefixes before a summary verb (high-confidence only).
_SUMMARY_PREFIX = (
    r"(?:(?:please|por\s+favor|can\s+you|could\s+you|would\s+you|"
    r"me\s+puedes|podr[ií]as?|dame|haz(?:me)?|quiero)\s+)?"
    r"(?:(?:un|una|a|el|la|the)\s+)?"
)

# summarize / resume ticket #N  OR  resumen del ticket 123
_SUMMARY_RE = re.compile(
    rf"^\s*{_SUMMARY_PREFIX}"
    r"(?:summar(?:y|ize|ise)|resum(?:e|en|ir)|sumariz(?:a|ar))"
    r"(?:\s+(?:of|del|de|the|el|la|este|esta|for|para))?"
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

# Nostalgia / storytelling — must NOT become durable memory writes.
_REMEMBER_NOSTALGIA_RE = re.compile(
    r"^\s*(?:remember|recuerda(?:\s+que)?|memoriza|te\s+acuerdas)\s+"
    r"(?:when|the\s+time|how\s+we|that\s+time|"
    r"cuando|aquella?\s+vez|el\s+d[ií]a)\b",
    re.IGNORECASE,
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
    r"^\s*(?:forget|olvida(?:r)?)\s+(?:key\s+|la\s+clave\s+)?"
    r"([a-zA-Z][a-zA-Z0-9_.-]{0,63})\s*$",
    re.IGNORECASE,
)

# show memory / muestra la memoria (allow accented muéstrame)
_SHOW_MEMORY_RE = re.compile(
    r"^\s*(?:(?:show|list|ver|mu[eé]stra(?:me)?)\s+(?:(?:la|el|mi|my|the)\s+)?)?"
    r"(?:my\s+)?(?:memory|memoria)\b|"
    r"^\s*(?:qu[eé]\s+recuerdas|what\s+do\s+you\s+remember)\s*$",
    re.IGNORECASE,
)

# Negation near a summary request → fall through to LLM (prefer miss over wrong cmd).
_SUMMARY_NEGATION_RE = re.compile(
    r"\b(?:not|n't|no|nunca|never|dont|don't|ignore|without|sin)\b",
    re.IGNORECASE,
)

_SUMMARY_VERB_RE = re.compile(
    r"\b(?:summar(?:y|ize|ise)|resum(?:e|en|ir)|sumariz)",
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


def _strip_reply_context(user_text: str) -> str:
    """Keep only the user half after a replied-to excerpt separator."""
    ut = (user_text or "").strip()
    if "\n\n---\n\n" in ut:
        return ut.split("\n\n---\n\n", 1)[-1].strip()
    return ut


def try_nl_fastpath(user_text: str) -> NLFastpathOutcome | None:
    """Return a deterministic outcome when the intent is obvious; else None.

    Does not call the LLM. Callers should fall back to ``run_nl_router``.
    """
    ut = _strip_reply_context(user_text)
    if not ut:
        return None

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

    # Nostalgia / storytelling must not become memory writes.
    if _REMEMBER_NOSTALGIA_RE.match(ut):
        return None

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

    # Single issue id + clear summary verb (short messages only).
    # Skip when negation is present — prefer LLM over a wrong summary invoke.
    ids = extract_issue_ids(ut)
    if (
        len(ids) == 1
        and len(ut) <= 80
        and _SUMMARY_VERB_RE.search(ut)
        and not _SUMMARY_NEGATION_RE.search(ut)
    ):
        return NLInvoke(command="summary", args={"issue_id": ids[0]})

    return None
