"""Tests for Discord markdown helpers."""

from __future__ import annotations

import warnings

import discord.utils

from ultron.discord_format import escape_markdown


def test_escape_markdown_matches_discord_utils_defaults() -> None:
    samples = [
        "plain",
        "has *stars* and _underscores_",
        "code `x` and ~~strike~~",
        "spoiler ||secret||",
        "# heading\n- list",
        "> quote",
        "[link](https://example.com)",
        "see https://example.com/a_b_c for details",
        r"already \*escaped\*",
    ]
    for text in samples:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            expected = discord.utils.escape_markdown(text)
        assert escape_markdown(text) == expected, text


def test_escape_markdown_no_deprecation_warning() -> None:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", DeprecationWarning)
        assert escape_markdown("a *b* _c_") == r"a \*b\* \_c\_"
    assert not any(issubclass(w.category, DeprecationWarning) for w in caught)
