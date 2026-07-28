from __future__ import annotations

from pathlib import Path

from ultron.redmine_textile import (
    has_markdown_artifacts,
    scrub_markdown_to_textile,
    textile_bullet_list,
    textile_code,
    textile_em,
    textile_labeled,
    textile_pre,
    textile_strong,
)
from ultron.self_upgrade import (
    AutoagentsShotResult,
    SelfUpgradeMode,
    SelfUpgradeOutcome,
    SelfUpgradeTrigger,
    _outcome_redmine_notes,
)
from ultron.workflows import NOTE_SYSTEM, _note_body_with_author


def test_textile_strong_code_pre() -> None:
    assert textile_strong("Why:") == "*Why:*"
    assert textile_code("gemma4") == "@gemma4@"
    # Values containing @ must not use Textile @…@ wrapping.
    assert not textile_code("a@b").startswith("@")
    assert "<code>" in textile_code("a@b")
    pre = textile_pre("line1\nline2")
    assert pre.startswith("<pre>\n")
    assert pre.endswith("\n</pre>")
    assert "```" not in pre
    assert "**" not in pre


def test_textile_em_and_list() -> None:
    assert textile_em("Note written by Ada from Discord") == (
        "_Note written by Ada from Discord_"
    )
    assert textile_bullet_list(["ok", "pip"]) == "* ok\n* pip"
    assert textile_labeled("Dump:", "done") == "*Dump:* done"


def test_scrub_markdown_to_textile() -> None:
    raw = "See **bold** and `path/file.py` then:\n```\nlog tail\n```\n"
    out = scrub_markdown_to_textile(raw)
    assert "**" not in out
    assert "```" not in out
    assert "*bold*" in out
    assert "@path/file.py@" in out
    assert "<pre>" in out
    assert not has_markdown_artifacts(out)


def test_outcome_redmine_notes_is_textile() -> None:
    shot = AutoagentsShotResult(
        session_id="sess-1",
        exit_code=0,
        stdout="agent did work\n**should not stay md**\n```\ncode\n```\n",
        stderr="",
        task_path=Path("FEAT-0-example.md"),
        duration_seconds=12.0,
    )
    outcome = SelfUpgradeOutcome(
        trigger=SelfUpgradeTrigger(
            mode=SelfUpgradeMode.OPERATOR,
            request="upgrade please",
        ),
        shot_result=shot,
        verify_ok=True,
        verify_steps=["pytest ok", "import ok"],
        verify_error=None,
        restarted=True,
        user_action=None,
        dump_ok=True,
        task_path=Path("FEAT-0-example.md"),
        redmine_issue_id=7406,
        redmine_note_ok=True,
    )
    notes = _outcome_redmine_notes(outcome, secret_literals=None)
    assert notes.startswith("Ultron self-upgrade report")
    assert "**" not in notes
    assert "```" not in notes
    assert "<pre>" in notes
    assert "*Why:*" in notes
    assert "*Verification (passed):*" in notes
    assert "* pytest ok" in notes
    assert "@sess-1@" in notes
    assert not has_markdown_artifacts(notes)


def test_outcome_redmine_notes_auto_repair() -> None:
    outcome = SelfUpgradeOutcome(
        trigger=SelfUpgradeTrigger(
            mode=SelfUpgradeMode.AUTO_REPAIR,
            request="",
            error_type="AttributeError",
            error_message="no foo",
            command="summary",
        ),
        shot_result=None,
        verify_ok=False,
        verify_steps=[],
        verify_error="boom",
        restarted=False,
        user_action="Check logs",
        failure_reason="verify failed",
    )
    notes = _outcome_redmine_notes(outcome, secret_literals=None)
    assert notes.startswith("Ultron self-repair report")
    assert "@AttributeError@" in notes
    assert "@/summary@" in notes
    assert "*Status:*" in notes
    assert "**" not in notes
    assert "```" not in notes


def test_note_system_requires_textile() -> None:
    assert "Textile" in NOTE_SYSTEM
    assert "Markdown" in NOTE_SYSTEM or "markdown" in NOTE_SYSTEM.lower()
    assert "```" in NOTE_SYSTEM  # forbidden example in prompt text is ok
    assert "Do NOT use Markdown" in NOTE_SYSTEM


def test_note_body_with_author_textile() -> None:
    body = _note_body_with_author(author_label="Ada", formatted="Hello ticket")
    assert body.startswith("_Note written by Ada from Discord_")
    assert "Hello ticket" in body
