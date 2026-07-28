"""Discord confirm/cancel UI for Redmine-mutating writes.

Why: small models often invent wrong issue ids, hours, or note text. Requiring
an explicit Confirm from the same Discord user before ``note`` / ``new_ticket`` /
``log_time`` reduces accidental writes (same idea as My.ai write confirmation).

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


class ConfirmResult(str, Enum):
    """Outcome of a write-confirmation prompt."""

    APPROVE = "approve"
    CANCEL = "cancel"
    TIMEOUT = "timeout"


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

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Reject clicks from anyone other than the requester."""
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "Only the person who requested this write can confirm it.",
                ephemeral=True,
            )
            return False
        return True

    def _finish(self, result: ConfirmResult) -> None:
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
        """Mark timeout when the user never clicked."""
        if self.result is None:
            self.result = ConfirmResult.TIMEOUT
            self._event.set()

    async def wait_result(self) -> ConfirmResult:
        """Block until a button is pressed or the view times out."""
        await self._event.wait()
        return self.result or ConfirmResult.TIMEOUT


def format_write_confirm_prompt(summary: str) -> str:
    """User-visible confirm message body."""
    body = (summary or "").strip() or "(no details)"
    if len(body) > 1500:
        body = body[:1500] + "…"
    return (
        "**Confirm Redmine write**\n\n"
        f"{body}\n\n"
        "Press **Confirm** to apply, or **Cancel** to abort."
    )


async def ask_write_confirm(
    *,
    channel: discord.abc.Messageable,
    author_id: int,
    summary: str,
    edit_message: discord.Message | None = None,
    timeout: float = _DEFAULT_TIMEOUT_SECONDS,
) -> ConfirmResult:
    """Show Confirm/Cancel and wait for the author (or timeout).

    Prefers editing ``edit_message`` (NL status bubble); otherwise sends a new
    message in ``channel``. Clears buttons when done.
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
            await prompt_msg.edit(view=None)
    except discord.HTTPException:
        pass
    return result
