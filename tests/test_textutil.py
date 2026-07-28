"""Tests for issue formatting helpers."""

from __future__ import annotations

from ultron.textutil import format_issue_for_summary, format_issue_metadata_header


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
    issue = {
        "id": 1,
        "subject": "Big",
        "description": "D" * 9000,
        "status": {"name": "New"},
        "tracker": {"name": "Bug"},
        "project": {"name": "P"},
        "assigned_to": {"name": "A"},
        "author": {"name": "B"},
        "created_on": "t0",
        "updated_on": "t1",
        "journals": [
            {"user": {"name": "u"}, "created_on": "t", "notes": "N" * 2000}
            for _ in range(40)
        ],
    }
    text = format_issue_for_summary(issue, max_total_chars=5000)
    assert len(text) <= 5000
    assert "Journal" in text
