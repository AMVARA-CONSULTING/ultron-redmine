"""summary_note prompt is one journal; missing notes do not fall back to the ticket."""

from __future__ import annotations

import asyncio

from ultron.workflows import JournalNoteNotFound, summarize_journal_note


class _FakeRedmine:
    def __init__(self, issue: dict) -> None:
        self._issue = issue

    async def get_issue(self, issue_id: int) -> dict:
        return self._issue


class _FakeLLM:
    model = "test-model"

    def __init__(self) -> None:
        self.system = ""
        self.user = ""

    async def complete(self, *, system: str, user: str, **_kwargs: object) -> str:
        self.system = system
        self.user = user
        return "note summary"


def _issue() -> dict:
    return {
        "id": 10,
        "subject": "Gate deploy",
        "description": "SECRET-DESC-SHOULD-NOT-APPEAR",
        "journals": [
            {"id": 2, "user": {"name": "Ada"}, "created_on": "2026-01-02", "notes": "FIRST-NOTE"},
            {"id": 4, "user": {"name": "Cy"}, "created_on": "2026-01-04", "notes": "LAST-NOTE"},
        ],
    }


def test_summarize_journal_note_prompt_is_one_note() -> None:
    llm = _FakeLLM()

    async def _run() -> str:
        return await summarize_journal_note(
            redmine=_FakeRedmine(_issue()),
            llm=llm,  # type: ignore[arg-type]
            issue_id=10,
            selector="1",
            issue_metadata_header=False,
        )

    out = asyncio.run(_run())
    assert out == "note summary"
    assert "FIRST-NOTE" in llm.user
    assert "Journal id: 2" in llm.user
    assert "SECRET-DESC-SHOULD-NOT-APPEAR" not in llm.user
    assert "LAST-NOTE" not in llm.user
    assert "Summarize that note only" in llm.system


def test_summarize_journal_note_missing_does_not_call_llm() -> None:
    llm = _FakeLLM()

    async def _run() -> None:
        await summarize_journal_note(
            redmine=_FakeRedmine(_issue()),
            llm=llm,  # type: ignore[arg-type]
            issue_id=10,
            selector="9",
            issue_metadata_header=False,
        )

    try:
        asyncio.run(_run())
    except JournalNoteNotFound as e:
        assert "2 notes" in str(e)
    else:
        raise AssertionError("expected JournalNoteNotFound")
    assert llm.user == ""
