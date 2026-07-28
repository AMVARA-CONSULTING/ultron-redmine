from __future__ import annotations

# Default prompt budgets for Gemma-class / local LLMs (see docs/OPERATIONS.md).
# Keep these tight: per-field caps usually land under the total; the total is a hard backstop.
ISSUE_SUMMARY_MAX_DESCRIPTION_CHARS = 4000
ISSUE_SUMMARY_MAX_JOURNAL_NOTES = 12
ISSUE_SUMMARY_MAX_NOTE_CHARS = 800
ISSUE_SUMMARY_MAX_TOTAL_CHARS = 8000


def format_issue_metadata_header(issue: dict) -> str:
    """One-line Discord markdown: note count, logged time, last update (Redmine issue JSON)."""
    journals = issue.get("journals") or []
    note_count = sum(1 for j in journals if str(j.get("notes") or "").strip())
    raw_spent = issue.get("spent_hours")
    if raw_spent is None:
        spent_str = "0 h"
    else:
        try:
            h = float(raw_spent)
            spent_str = f"{h:g} h" if h == int(h) else f"{h:.2f} h"
        except (TypeError, ValueError):
            spent_str = str(raw_spent)
    updated = issue.get("updated_on") or "—"
    return (
        f"**Notes:** {note_count}  ·  **Total time logged:** {spent_str}  ·  **Last updated:** {updated}"
    )


def chunk_discord(text: str, limit: int = 1900) -> list[str]:
    """Split text into chunks under Discord's ~2000 char message limit."""
    text = text.strip()
    if not text:
        return ["(empty)"]
    chunks: list[str] = []
    rest = text
    while rest:
        if len(rest) <= limit:
            chunks.append(rest)
            break
        cut = rest.rfind("\n", 0, limit)
        if cut < limit // 2:
            cut = limit
        chunks.append(rest[:cut].strip())
        rest = rest[cut:].lstrip()
    return chunks


def format_issue_for_summary(
    issue: dict,
    *,
    max_description_chars: int = ISSUE_SUMMARY_MAX_DESCRIPTION_CHARS,
    max_journal_notes: int = ISSUE_SUMMARY_MAX_JOURNAL_NOTES,
    max_note_chars: int = ISSUE_SUMMARY_MAX_NOTE_CHARS,
    max_total_chars: int = ISSUE_SUMMARY_MAX_TOTAL_CHARS,
) -> str:
    """Render a Redmine issue for LLM prompts (compact defaults for small models).

    Why: Gemma-class context windows fill quickly; aggressive truncation keeps
    summary/ask prompts useful without drowning the model in old journals.
    Length is always ≤ ``max_total_chars`` (hard backstop after per-field caps).
    """
    lines: list[str] = []
    lines.append(f"#{(issue.get('id'))}: {issue.get('subject', '')}")
    if issue.get("description"):
        lines.append("")
        lines.append("## Description")
        lines.append(str(issue["description"])[:max_description_chars])
    status = issue.get("status") or {}
    tracker = issue.get("tracker") or {}
    project = issue.get("project") or {}
    assignee = issue.get("assigned_to") or {}
    author = issue.get("author") or {}
    lines.append("")
    lines.append(
        f"Project: {project.get('name', '')} | Tracker: {tracker.get('name', '')} | "
        f"Status: {status.get('name', '')} | Priority: {(issue.get('priority') or {}).get('name', '')}"
    )
    lines.append(f"Author: {author.get('name', '')} | Assigned: {assignee.get('name', '—')}")
    lines.append(f"Created: {issue.get('created_on', '')} | Updated: {issue.get('updated_on', '')}")

    journals = issue.get("journals") or []
    if journals:
        lines.append("")
        lines.append("## Journal (recent)")
        noted = [j for j in journals if str(j.get("notes") or "").strip()]
        for j in noted[-max_journal_notes:]:
            user = (j.get("user") or {}).get("name", "")
            created = j.get("created_on", "")
            notes = (j.get("notes") or "").strip()
            lines.append(f"- [{created}] {user}: {notes[:max_note_chars]}")

    text = "\n".join(lines)
    if len(text) > max_total_chars:
        return text[: max_total_chars - 40] + "\n…(ticket truncated for LLM)"
    return text
