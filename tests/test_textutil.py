"""Tests for issue formatting helpers."""

from __future__ import annotations

from ultron.nl_router import NL_ROUTER_SYSTEM, _router_system_with_memory
from ultron.textutil import (
    ISSUE_SUMMARY_MAX_DESCRIPTION_CHARS,
    ISSUE_SUMMARY_MAX_JOURNAL_NOTES,
    ISSUE_SUMMARY_MAX_NOTE_CHARS,
    ISSUE_SUMMARY_MAX_TOTAL_CHARS,
    format_issue_for_summary,
    format_issue_metadata_header,
)
from ultron.user_memory import MEMORY_PROMPT_MAX_CHARS
from ultron.workflows import SUMMARY_SYSTEM, _memory_prefix


def _fat_issue(*, journal_count: int = 50, note_len: int = 5000, desc_len: int = 20_000) -> dict:
    """Synthetic oversized ticket used to lock truncation invariants."""
    return {
        "id": 99,
        "subject": "Fat ticket " + ("X" * 200),
        "description": "D" * desc_len,
        "status": {"name": "New"},
        "tracker": {"name": "Bug"},
        "project": {"name": "P"},
        "assigned_to": {"name": "A"},
        "author": {"name": "B"},
        "created_on": "t0",
        "updated_on": "t1",
        "journals": [
            {"user": {"name": "u"}, "created_on": "t", "notes": "N" * note_len}
            for _ in range(journal_count)
        ],
    }


def test_format_issue_metadata_header_counts_notes_and_spent_hours() -> None:
    issue = {
        "journals": [
            {"notes": "first"},
            {"notes": ""},
            {"notes": "   "},
            {"notes": "second"},
        ],
        "spent_hours": 3.5,
        "updated_on": "2026-04-01T12:00:00Z",
    }
    line = format_issue_metadata_header(issue)
    assert "**Notes:** 2" in line
    assert "**Total time logged:** 3.50 h" in line
    assert "**Last updated:** 2026-04-01T12:00:00Z" in line


def test_format_issue_metadata_header_missing_spent_hours() -> None:
    issue = {"journals": [], "updated_on": "x"}
    line = format_issue_metadata_header(issue)
    assert "**Notes:** 0" in line
    assert "**Total time logged:** 0 h" in line


def test_format_issue_for_summary_truncates() -> None:
    text = format_issue_for_summary(_fat_issue(), max_total_chars=5000)
    assert len(text) <= 5000
    assert "Journal" in text
    assert "truncated" in text.lower()


def test_format_issue_for_summary_default_total_cap() -> None:
    """Fat tickets must stay within the Gemma-oriented default total budget."""
    text = format_issue_for_summary(_fat_issue())
    assert len(text) <= ISSUE_SUMMARY_MAX_TOTAL_CHARS
    # Description field capped before the total backstop.
    assert "D" * (ISSUE_SUMMARY_MAX_DESCRIPTION_CHARS + 1) not in text
    # Only the most recent journal notes are kept.
    assert text.count("- [t] u:") <= ISSUE_SUMMARY_MAX_JOURNAL_NOTES


def test_format_issue_for_summary_per_note_cap() -> None:
    text = format_issue_for_summary(_fat_issue(journal_count=3, note_len=5000, desc_len=10))
    # Each journal line body is capped (prefix + note[:max_note_chars]).
    for line in text.splitlines():
        if line.startswith("- ["):
            # "- [t] u: " is 9 chars; note body follows.
            body = line.split(": ", 1)[-1]
            assert len(body) <= ISSUE_SUMMARY_MAX_NOTE_CHARS


def test_prompt_budget_ballpark_chars() -> None:
    """Documented operator ballparks: router system + memory; summary user + memory."""
    assert len(NL_ROUTER_SYSTEM) < 4000
    assert len(SUMMARY_SYSTEM) < 400
    mem = "M" * MEMORY_PROMPT_MAX_CHARS
    router = _router_system_with_memory(mem)
    assert len(router) <= len(NL_ROUTER_SYSTEM) + MEMORY_PROMPT_MAX_CHARS + 10
    body = format_issue_for_summary(_fat_issue())
    prefix = _memory_prefix(mem)
    user_prompt = (
        f"{prefix}"
        f"Summarize this Redmine ticket as requested by a teammate.\n\n{body}"
    )
    # Memory appears once in the summary user prompt (not duplicated).
    assert user_prompt.count(prefix) == 1
    assert len(user_prompt) <= MEMORY_PROMPT_MAX_CHARS + 20 + ISSUE_SUMMARY_MAX_TOTAL_CHARS + 80
