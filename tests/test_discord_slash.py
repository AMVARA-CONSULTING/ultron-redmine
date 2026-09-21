"""Tests for discord_slash edit_or_followup and DeferredInteractionGuard."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import discord
import pytest

from ultron.discord_slash import (
    DeferredInteractionGuard,
    _LONG_RUNNING_MSG,
    edit_or_followup,
)


def _fake_response(*, status: int = 404, reason: str = "Not Found") -> SimpleNamespace:
    return SimpleNamespace(status=status, reason=reason)


def _http_exc(
    *,
    status: int = 400,
    code: int | None = None,
    message: str = "error",
) -> discord.HTTPException:
    body: str | dict[str, object]
    if code is not None:
        body = {"code": code, "message": message}
    else:
        body = message
    return discord.HTTPException(_fake_response(status=status), body)


def _unknown_interaction() -> discord.NotFound:
    return discord.NotFound(
        _fake_response(status=404),
        {"code": 10062, "message": "Unknown interaction"},
    )


def _make_interaction() -> MagicMock:
    interaction = MagicMock(spec=discord.Interaction)
    interaction.edit_original_response = AsyncMock()
    interaction.followup = MagicMock()
    interaction.followup.send = AsyncMock()
    return interaction


def test_edit_or_followup_edits_original() -> None:
    interaction = _make_interaction()

    async def _run() -> bool:
        return await edit_or_followup(interaction, "done")

    assert asyncio.run(_run()) is True
    interaction.edit_original_response.assert_awaited_once_with(content="done")
    interaction.followup.send.assert_not_awaited()


def test_edit_or_followup_fallback_on_unknown_interaction() -> None:
    interaction = _make_interaction()
    interaction.edit_original_response = AsyncMock(side_effect=_unknown_interaction())

    async def _run() -> bool:
        return await edit_or_followup(interaction, "via followup", ephemeral=True)

    assert asyncio.run(_run()) is True
    interaction.followup.send.assert_awaited_once_with("via followup", ephemeral=True)


def test_edit_or_followup_fallback_on_401() -> None:
    interaction = _make_interaction()
    interaction.edit_original_response = AsyncMock(
        side_effect=_http_exc(status=401, message="Unauthorized"),
    )

    async def _run() -> bool:
        return await edit_or_followup(interaction, "ok")

    assert asyncio.run(_run()) is True
    interaction.followup.send.assert_awaited_once()


def test_edit_or_followup_fallback_on_code_50027() -> None:
    interaction = _make_interaction()
    interaction.edit_original_response = AsyncMock(
        side_effect=_http_exc(status=400, code=50027, message="Invalid Webhook Token"),
    )

    async def _run() -> bool:
        return await edit_or_followup(interaction, "ok")

    assert asyncio.run(_run()) is True
    interaction.followup.send.assert_awaited_once()


def test_edit_or_followup_returns_false_when_both_dead() -> None:
    interaction = _make_interaction()
    interaction.edit_original_response = AsyncMock(side_effect=_unknown_interaction())
    interaction.followup.send = AsyncMock(side_effect=_unknown_interaction())

    async def _run() -> bool:
        return await edit_or_followup(interaction, "lost")

    assert asyncio.run(_run()) is False


def test_edit_or_followup_returns_false_on_followup_401() -> None:
    interaction = _make_interaction()
    interaction.edit_original_response = AsyncMock(
        side_effect=_http_exc(status=401, message="Unauthorized"),
    )
    interaction.followup.send = AsyncMock(
        side_effect=_http_exc(status=401, message="Unauthorized"),
    )

    async def _run() -> bool:
        return await edit_or_followup(interaction, "lost")

    assert asyncio.run(_run()) is False


def test_edit_or_followup_returns_false_on_followup_50027() -> None:
    interaction = _make_interaction()
    interaction.edit_original_response = AsyncMock(
        side_effect=_http_exc(status=400, code=50027, message="Invalid Webhook Token"),
    )
    interaction.followup.send = AsyncMock(
        side_effect=_http_exc(status=400, code=50027, message="Invalid Webhook Token"),
    )

    async def _run() -> bool:
        return await edit_or_followup(interaction, "lost")

    assert asyncio.run(_run()) is False


def test_edit_or_followup_reraises_unexpected_http_error() -> None:
    interaction = _make_interaction()
    interaction.edit_original_response = AsyncMock(
        side_effect=_http_exc(status=500, code=0, message="Internal Server Error"),
    )

    async def _run() -> bool:
        return await edit_or_followup(interaction, "boom")

    with pytest.raises(discord.HTTPException):
        asyncio.run(_run())
    interaction.followup.send.assert_not_awaited()


def test_edit_or_followup_reraises_unexpected_followup_error() -> None:
    interaction = _make_interaction()
    interaction.edit_original_response = AsyncMock(side_effect=_unknown_interaction())
    interaction.followup.send = AsyncMock(
        side_effect=_http_exc(status=500, code=0, message="Internal Server Error"),
    )

    async def _run() -> bool:
        return await edit_or_followup(interaction, "boom")

    with pytest.raises(discord.HTTPException):
        asyncio.run(_run())


def test_edit_or_followup_truncates_to_2000() -> None:
    interaction = _make_interaction()
    long_text = "x" * 2500

    async def _run() -> bool:
        return await edit_or_followup(interaction, long_text)

    assert asyncio.run(_run()) is True
    interaction.edit_original_response.assert_awaited_once_with(content="x" * 2000)


def test_deferred_guard_posts_long_running_notice() -> None:
    interaction = _make_interaction()

    async def _run() -> DeferredInteractionGuard:
        guard = DeferredInteractionGuard(interaction, warn_after_seconds=0.01)
        await guard.start()
        await asyncio.sleep(0.05)
        return guard

    guard = asyncio.run(_run())
    assert guard.use_feedback is True
    interaction.edit_original_response.assert_awaited_once_with(content=_LONG_RUNNING_MSG)
    guard.stop()


def test_deferred_guard_stop_cancels_warn() -> None:
    interaction = _make_interaction()

    async def _run() -> DeferredInteractionGuard:
        guard = DeferredInteractionGuard(interaction, warn_after_seconds=0.05)
        await guard.start()
        guard.stop()
        await asyncio.sleep(0.1)
        return guard

    guard = asyncio.run(_run())
    assert guard.use_feedback is False
    interaction.edit_original_response.assert_not_awaited()
