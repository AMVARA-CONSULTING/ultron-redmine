"""Per-Discord-user durable memory (prefs / standing notes) as JSON files.

Why: small local models (e.g. Gemma) cannot rely on long chat history. Short
standing instructions per user improve routing and summaries without bloating
context. Growth is gated by free disk space so the bot cannot fill the volume.

How used: Discord slash ``/remember`` ``/forget`` ``/memory``, NL fast-path, and
injection into NL router / summary / ask / ol prompts via ``format_for_prompt``.
"""

from __future__ import annotations

import json
import logging
import re
import shutil
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

USER_MEMORY_DIRNAME = "user_memory"
_KEY_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_.-]{0,63}$")
_MAX_KEY_LEN = 64
_MAX_CONTENT_LEN = 500
_MAX_ENTRIES = 20
_MAX_PROMPT_CHARS = 1200
_MAX_FILE_BYTES = 64 * 1024
# Refuse growth when free space on the memory volume is below this floor.
_MIN_FREE_BYTES = 100 * 1024 * 1024
# Extra headroom required beyond the projected write size.
_WRITE_HEADROOM_BYTES = 1 * 1024 * 1024


class MemoryError(Exception):
    """Base error for user memory operations."""


class MemoryValidationError(MemoryError):
    """Invalid key/content or store limits."""


class MemoryDiskFullError(MemoryError):
    """Not enough free disk space (or file would exceed the per-user cap)."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_owner(owner_id: int | str) -> str:
    text = re.sub(r"[^0-9a-zA-Z._-]+", "_", str(owner_id).strip())
    return (text[:64] or "unknown").lower()


def validate_memory_key(key: str) -> str:
    """Normalize and validate a memory entry key.

    Raises:
        MemoryValidationError: empty or malformed key.
    """
    cleaned = (key or "").strip()
    if not cleaned:
        raise MemoryValidationError("Memory key must not be empty.")
    if len(cleaned) > _MAX_KEY_LEN:
        raise MemoryValidationError(f"Memory key too long (max {_MAX_KEY_LEN}).")
    if not _KEY_RE.match(cleaned):
        raise MemoryValidationError(
            "Memory key must start with a letter and use only letters, digits, "
            "underscore, dot, or hyphen."
        )
    return cleaned


def validate_memory_content(content: str) -> str:
    """Normalize content and enforce length.

    Raises:
        MemoryValidationError: empty or too long.
    """
    cleaned = (content or "").strip()
    if not cleaned:
        raise MemoryValidationError("Memory content must not be empty.")
    if len(cleaned) > _MAX_CONTENT_LEN:
        raise MemoryValidationError(
            f"Memory content too long (max {_MAX_CONTENT_LEN} chars)."
        )
    return cleaned


class UserMemoryStore:
    """Thread-safe JSON memory: one file per Discord user under ``state_dir``.

    Layout::

        <state_dir>/user_memory/user_<discord_id>.json
    """

    def __init__(
        self,
        state_dir: Path | str,
        *,
        min_free_bytes: int = _MIN_FREE_BYTES,
        max_entries: int = _MAX_ENTRIES,
        max_file_bytes: int = _MAX_FILE_BYTES,
    ) -> None:
        """Create a store rooted at ``state_dir / user_memory``.

        Args:
            state_dir: Ultron state directory (same as whitelist).
            min_free_bytes: Refuse growth when free disk is below this.
            max_entries: Cap entries per user.
            max_file_bytes: Cap serialized file size per user.
        """
        self.root = Path(state_dir) / USER_MEMORY_DIRNAME
        self.root.mkdir(parents=True, exist_ok=True)
        self.min_free_bytes = max(0, int(min_free_bytes))
        self.max_entries = max(1, int(max_entries))
        self.max_file_bytes = max(1024, int(max_file_bytes))
        self._lock = threading.Lock()
        logger.info("User memory store ready at %s", self.root.resolve())

    def _path(self, owner_id: int | str) -> Path:
        return self.root / f"user_{_safe_owner(owner_id)}.json"

    def _empty_doc(self, owner_id: int | str) -> dict[str, Any]:
        return {
            "version": 1,
            "owner_id": str(owner_id),
            "updated_at": _utc_now(),
            "entries": {},
        }

    def _read(self, path: Path, owner_id: int | str) -> dict[str, Any]:
        if not path.exists():
            return self._empty_doc(owner_id)
        try:
            raw = path.read_text(encoding="utf-8")
            data = json.loads(raw) if raw.strip() else {}
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Corrupt user memory %s: %s — starting fresh", path, exc)
            return self._empty_doc(owner_id)
        if not isinstance(data, dict):
            return self._empty_doc(owner_id)
        entries = data.get("entries")
        if not isinstance(entries, dict):
            data = self._empty_doc(owner_id)
        return data

    def _serialize(self, data: dict[str, Any]) -> bytes:
        return (json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode("utf-8")

    def free_disk_bytes(self) -> int:
        """Return free bytes on the filesystem that holds this store."""
        self.root.mkdir(parents=True, exist_ok=True)
        usage = shutil.disk_usage(self.root)
        return int(usage.free)

    def assert_can_grow(self, *, current_bytes: int, new_bytes: int) -> None:
        """Refuse growth when free disk is low or the file would exceed the cap.

        Shrinking or same-size rewrites are always allowed (so users can forget
        entries even on a full disk). Growth requires free space above
        ``min_free_bytes`` plus write headroom, and ``new_bytes <= max_file_bytes``.

        Raises:
            MemoryDiskFullError: not enough space or file too large.
        """
        if new_bytes <= current_bytes:
            return
        if new_bytes > self.max_file_bytes:
            raise MemoryDiskFullError(
                f"User memory file would be {new_bytes} bytes "
                f"(max {self.max_file_bytes}). Clear unused keys with /forget."
            )
        free = self.free_disk_bytes()
        needed = (new_bytes - current_bytes) + _WRITE_HEADROOM_BYTES
        if free < self.min_free_bytes:
            raise MemoryDiskFullError(
                f"Not enough free disk for memory growth "
                f"(free={free} B, need at least {self.min_free_bytes} B free)."
            )
        if free < needed:
            raise MemoryDiskFullError(
                f"Not enough free disk for memory growth "
                f"(free={free} B, write needs ~{needed} B)."
            )

    def load(self, owner_id: int | str) -> dict[str, Any]:
        """Load the raw memory document for a user."""
        with self._lock:
            return self._read(self._path(owner_id), owner_id)

    def list_entries(self, owner_id: int | str) -> dict[str, str]:
        """Return key → content for a user (empty dict if none)."""
        data = self.load(owner_id)
        entries = data.get("entries") or {}
        out: dict[str, str] = {}
        for key, meta in entries.items():
            if isinstance(meta, dict):
                content = str(meta.get("content") or "").strip()
            else:
                content = str(meta or "").strip()
            if content:
                out[str(key)] = content
        return out

    def format_for_prompt(
        self,
        owner_id: int | str,
        *,
        max_chars: int = _MAX_PROMPT_CHARS,
    ) -> str:
        """Compact standing notes for LLM system/user injection (content only)."""
        entries = self.list_entries(owner_id)
        if not entries:
            return ""
        lines = ["Standing user prefs (MUST follow when relevant):"]
        for key, content in sorted(entries.items()):
            if "\n" in content:
                first, *rest = content.splitlines()
                lines.append(f"- [{key}] {first.strip()}")
                for part in rest:
                    part = part.strip()
                    if part:
                        lines.append(f"  {part}")
            else:
                lines.append(f"- [{key}] {content}")
        text = "\n".join(lines)
        if len(text) > max_chars:
            text = text[: max_chars - 40] + "\n…(memory truncated for prompt)"
        return text

    def update(self, owner_id: int | str, key: str, content: str) -> dict[str, Any]:
        """Create or replace one memory entry after disk-space checks.

        Raises:
            MemoryValidationError: bad key/content or too many entries.
            MemoryDiskFullError: insufficient free disk or file cap.
        """
        key = validate_memory_key(key)
        content = validate_memory_content(content)
        path = self._path(owner_id)
        with self._lock:
            data = self._read(path, owner_id)
            entries = data.setdefault("entries", {})
            if not isinstance(entries, dict):
                entries = {}
                data["entries"] = entries
            is_new = key not in entries
            if is_new and len(entries) >= self.max_entries:
                raise MemoryValidationError(
                    f"Memory full ({self.max_entries} entries). "
                    "Clear one with /forget before adding more."
                )
            current_bytes = path.stat().st_size if path.is_file() else 0
            entries[key] = {"content": content, "updated_at": _utc_now()}
            data["updated_at"] = _utc_now()
            payload = self._serialize(data)
            self.assert_can_grow(current_bytes=current_bytes, new_bytes=len(payload))
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
            logger.info(
                "user_memory update owner=%s key=%s chars=%s file_bytes=%s",
                owner_id,
                key,
                len(content),
                len(payload),
            )
            return {"key": key, "content": content, "entries": len(entries)}

    def clear(
        self,
        owner_id: int | str,
        *,
        key: str | None = None,
        clear_all: bool = False,
    ) -> str:
        """Delete one key or wipe all entries for a user.

        Raises:
            MemoryValidationError: missing key / invalid args.
        """
        path = self._path(owner_id)
        with self._lock:
            data = self._read(path, owner_id)
            entries = data.get("entries")
            if not isinstance(entries, dict):
                entries = {}
            if clear_all:
                n = len(entries)
                data["entries"] = {}
                data["updated_at"] = _utc_now()
                path.write_bytes(self._serialize(data))
                return f"Cleared all memory ({n} entries)."
            if not key:
                raise MemoryValidationError("Pass key=… or clear_all=true.")
            key = validate_memory_key(key)
            if key not in entries:
                raise MemoryValidationError(f"No memory entry named {key!r}.")
            del entries[key]
            data["entries"] = entries
            data["updated_at"] = _utc_now()
            path.write_bytes(self._serialize(data))
            return f"Forgot memory key {key!r}."
