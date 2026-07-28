"""Unit tests for Redmine write Confirm/Cancel helpers (no live Discord)."""

from __future__ import annotations

import asyncio

from ultron.write_confirm import (
    ConfirmResult,
    WriteConfirmView,
    author_may_confirm,
    crop_issue_subject,
    format_issue_confirm_heading,
    format_write_abort_message,
    format_write_confirm_prompt,
)


def test_author_may_confirm_only_requester() -> None:
    assert author_may_confirm(author_id=42, clicker_id=42) is True
    assert author_may_confirm(author_id=42, clicker_id=99) is False
    assert author_may_confirm(author_id=1, clicker_id=1) is True


def test_format_write_confirm_prompt_truncates() -> None:
    long = "x" * 2000
    out = format_write_confirm_prompt(long)
    assert out.startswith("**Confirm Redmine write**")
    assert "Press **Confirm**" in out
    assert "…" in out
    assert len(out) < 2000


def test_format_write_confirm_prompt_empty() -> None:
    out = format_write_confirm_prompt("  ")
    assert "(no details)" in out


def test_format_write_abort_cancel_vs_timeout() -> None:
    cancel = format_write_abort_message(
        ConfirmResult.CANCEL, nothing_written="note was not posted"
    )
    timeout = format_write_abort_message(
        ConfirmResult.TIMEOUT, nothing_written="no time logged"
    )
    assert cancel.startswith("**Cancelled**")
    assert "note was not posted" in cancel
    assert "Nothing was written to Redmine" in cancel
    assert timeout.startswith("**Timed out**")
    assert "no time logged" in timeout
    assert "Nothing was written to Redmine" in timeout


def test_crop_issue_subject() -> None:
    assert crop_issue_subject(None) == ""
    assert crop_issue_subject("  Hello  ") == "Hello"
    assert crop_issue_subject("a\nb") == "a b"
    long = "Z" * 100
    cropped = crop_issue_subject(long, max_chars=10)
    assert len(cropped) == 10
    assert cropped.endswith("…")


def test_format_issue_confirm_heading_with_subject() -> None:
    with_subj = format_issue_confirm_heading(
        action="Add note", issue_id=7406, subject="Fix login"
    )
    assert "**Add note** on issue **#7406**" in with_subj
    assert "**Subject:** Fix login" in with_subj
    bare = format_issue_confirm_heading(action="Log time", issue_id=1, subject="")
    assert bare == "**Log time** on issue **#1**"
    assert "Subject" not in bare


def test_write_confirm_view_timeout_sets_result() -> None:
    async def _run() -> None:
        view = WriteConfirmView(author_id=7, timeout=30.0)
        await view.on_timeout()
        result = await asyncio.wait_for(view.wait_result(), timeout=1.0)
        assert result == ConfirmResult.TIMEOUT
        assert view.result == ConfirmResult.TIMEOUT
        assert view._settled is True
        for child in view.children:
            assert getattr(child, "disabled", False) is True

    asyncio.run(_run())


def test_write_confirm_view_double_finish_ignored() -> None:
    async def _run() -> None:
        view = WriteConfirmView(author_id=7, timeout=30.0)
        view._finish(ConfirmResult.CANCEL)
        view._finish(ConfirmResult.APPROVE)
        assert view.result == ConfirmResult.CANCEL
        assert await view.wait_result() == ConfirmResult.CANCEL

    asyncio.run(_run())
