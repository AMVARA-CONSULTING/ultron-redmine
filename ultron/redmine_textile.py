"""Format Redmine journal note bodies as Textile (not Markdown).

Redmine journals on this deployment render Textile. Markdown constructs such as
``**bold**``, fenced `` ``` `` blocks, and Discord-only markup show up literally
in the UI. Prefer these helpers when Ultron writes ``add_note`` payloads.
"""

from __future__ import annotations

import re

_FENCE_RE = re.compile(r"```[\s\S]*?```")
_MD_STRONG_RE = re.compile(r"\*\*(.+?)\*\*")
_MD_INLINE_CODE_RE = re.compile(r"`([^`\n]+)`")


def textile_strong(text: str) -> str:
    """Classic Redmine Textile strong: *text*."""
    return f"*{text}*"


def textile_em(text: str) -> str:
    """Classic Redmine Textile emphasis: _text_."""
    return f"_{text}_"


def textile_code(text: str) -> str:
    """Inline code as Textile @code@ (HTML <code> if @ appears in the value)."""
    raw = str(text)
    if "@" in raw or "<" in raw or ">" in raw:
        escaped = (
            raw.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        )
        return f"<code>{escaped}</code>"
    return f"@{raw}@"


def textile_pre(text: str) -> str:
    """Multi-line log / shot tail as an HTML pre block (safe in Redmine Textile)."""
    safe = str(text).replace("</pre>", "&lt;/pre&gt;")
    return f"<pre>\n{safe}\n</pre>"


def textile_labeled(label: str, value: str) -> str:
    """One line: *Label:* value."""
    return f"{textile_strong(label)} {value}"


def textile_bullet_list(items: list[str]) -> str:
    """Unordered Textile list (* item per line)."""
    return "\n".join(f"* {item}" for item in items if str(item).strip())


def has_markdown_artifacts(text: str) -> bool:
    """True if text still looks like Markdown fences or **strong**."""
    if "```" in text:
        return True
    if "**" in text:
        return True
    return False


def scrub_markdown_to_textile(text: str) -> str:
    """Best-effort convert common Markdown leftovers into Textile / <pre>.

    Intended as a safety net for LLM-polished notes, not a full Markdown parser.
    """
    if not text:
        return text

    def _fence_to_pre(match: re.Match[str]) -> str:
        block = match.group(0)
        inner = block.strip("`")
        # Drop optional language tag on the first line.
        if "\n" in inner:
            first, rest = inner.split("\n", 1)
            if first.strip() and " " not in first.strip() and len(first.strip()) < 20:
                inner = rest
            else:
                inner = inner
        else:
            # Single-line fence → inline code when short.
            return textile_code(inner.strip()) if len(inner) < 120 else textile_pre(inner)
        return textile_pre(inner)

    out = _FENCE_RE.sub(_fence_to_pre, text)
    out = _MD_STRONG_RE.sub(lambda m: textile_strong(m.group(1)), out)
    out = _MD_INLINE_CODE_RE.sub(lambda m: textile_code(m.group(1)), out)
    # Leftover lone ** markers (unbalanced) → drop.
    out = out.replace("**", "")
    return out
