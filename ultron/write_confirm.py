"""Discord confirm/cancel UI for Redmine-mutating writes.

Why: small models often invent wrong issue ids or hours. Requiring an explicit
Confirm from the same Discord user before ``new_ticket`` / ``log_time`` reduces
accidental writes (same idea as My.ai write confirmation). ``/note`` posts
immediately without Confirm.

How used: NL dispatch and slash handlers call ``ask_write_confirm`` with a short
summary; only ``APPROVE`` proceeds to the Redmine API.
"""

from __future__ import annotations

import asyncio
import logging
from enum import Enum

import discord

logger = logging.getLogger(__name__)

_DEFAULT_TIMEOUT_SECONDS = 120.0
_MAX_SUMMARY_CHARS = 1500
_MAX_SUBJECT_CHARS = 80


class ConfirmResult(str, Enum):
    """Outcome of a write-confirmation prompt."""

    APPROVE = "approve"
    CANCEL = "cancel"
    TIMEOUT = "timeout"


def author_may_confirm(*, author_id: int, clicker_id: int) -> bool:
    """Return True when the clicker is the user who requested the write."""
    return int(clicker_id) == int(author_id)


def crop_issue_subject(subject: str | None, *, max_chars: int = _MAX_SUBJECT_CHARS) -> str:
    """Short subject for confirm summaries (empty if missing)."""
    s = (subject or "").replace("\n", " ").strip()
    if not s:
        return ""
    if len(s) > max_chars:
        return s[: max_chars - 1] + "…"
    return s


def format_issue_confirm_heading(
    *,
    action: str,
    issue_id: int,
    subject: str | None = None,
) -> str:
    """First line(s) for log_time (and similar) confirms, optionally with subject."""
    head = f"**{action}** on issue **#{int(issue_id)}**"
    cropped = crop_issue_subject(subject)
    if cropped:
        return f"{head}\n**Subject:** {cropped}"
    return head


def format_write_confirm_prompt(summary: str) -> str:
    """User-visible confirm message body."""
    body = (summary or "").strip() or "(no details)"
    if len(body) > _MAX_SUMMARY_CHARS:
        body = body[:_MAX_SUMMARY_CHARS] + "…"
    return (
        "**Confirm Redmine write**\n\n"
        f"{body}\n\n"
        "Press **Confirm** to apply, or **Cancel** to abort."
    )


def format_write_abort_message(result: ConfirmResult, *, nothing_written: str) -> str:
    """Clear Cancel / Timeout text stating Redmine was not mutated.

    ``nothing_written`` is a short clause such as ``note was not posted`` or
    ``no time was logged`` (no trailing period).
    """
    detail = (nothing_written or "nothing was written").strip().rstrip(".")
    if result == ConfirmResult.TIMEOUT:
        return (
            f"**Timed out** — {detail}. "
            "Nothing was written to Redmine."
        )
    return f"**Cancelled** — {detail}. Nothing was written to Redmine."


class WriteConfirmView(discord.ui.View):
    """Two-button view; only ``author_id`` may click."""

    def __init__(
        self,
        *,
        author_id: int,
        timeout: float = _DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        """Build Confirm/Cancel buttons scoped to one Discord user."""
        super().__init__(timeout=timeout)
        self.author_id = int(author_id)
        self.result: ConfirmResult | None = None
        self._event = asyncio.Event()
        self._settled = False

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Reject clicks from anyone other than the requester."""
        if not author_may_confirm(
            author_id=self.author_id,
            clicker_id=interaction.user.id,
        ):
            await interaction.response.send_message(
                "Only the person who requested this write can confirm it.",
                ephemeral=True,
            )
            return False
        if self._settled:
            await interaction.response.send_message(
                "This confirmation was already handled.",
                ephemeral=True,
            )
            return False
        return True

    def _finish(self, result: ConfirmResult) -> None:
        if self._settled:
            return
        self._settled = True
        self.result = result
        self._event.set()
        self.stop()

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.success)
    async def confirm_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        """Approve the pending Redmine write."""
        await interaction.response.defer()
        self._finish(ConfirmResult.APPROVE)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        """Cancel the pending Redmine write."""
        await interaction.response.defer()
        self._finish(ConfirmResult.CANCEL)

    async def on_timeout(self) -> None:
        """Mark timeout when the user never clicked; disable leftover buttons."""
        if self.result is None and not self._settled:
            self._settled = True
            self.result = ConfirmResult.TIMEOUT
            for child in self.children:
                if isinstance(child, discord.ui.Button):
                    child.disabled = True
            self._event.set()

    async def wait_result(self) -> ConfirmResult:
        """Block until a button is pressed or the view times out."""
        await self._event.wait()
        return self.result or ConfirmResult.TIMEOUT


async def ask_write_confirm(
    *,
    channel: discord.abc.Messageable,
    author_id: int,
    summary: str,
    edit_message: discord.Message | None = None,
    timeout: float = _DEFAULT_TIMEOUT_SECONDS,
    abort_nothing_written: str | None = None,
) -> ConfirmResult:
    """Show Confirm/Cancel and wait for the author (or timeout).

    Prefers editing ``edit_message`` (NL status bubble); otherwise sends a new
    message in ``channel``. Clears buttons when done. On Cancel/Timeout, replaces
    the prompt with ``format_write_abort_message`` when ``abort_nothing_written``
    is set (callers may still overwrite with a more specific line).
    """
    view = WriteConfirmView(author_id=author_id, timeout=timeout)
    content = format_write_confirm_prompt(summary)
    prompt_msg: discord.Message | None = None
    try:
        if edit_message is not None:
            prompt_msg = await edit_message.edit(content=content, view=view)
            if prompt_msg is None:
                prompt_msg = edit_message
        else:
            prompt_msg = await channel.send(content=content, view=view)
    except discord.HTTPException as exc:
        logger.warning("write confirm prompt failed: %s", exc)
        return ConfirmResult.CANCEL

    result = await view.wait_result()
    try:
        if prompt_msg is not None:
            if result != ConfirmResult.APPROVE and abort_nothing_written:
                await prompt_msg.edit(
                    content=format_write_abort_message(
                        result, nothing_written=abort_nothing_written
                    ),
                    view=None,
                )
            else:
                await prompt_msg.edit(view=None)
    except discord.HTTPException:
        pass
    return result
