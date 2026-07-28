# Review & harden per-user durable memory (disk growth guards)

## Tracker
- **Redmine:** (none — Ultron 3.0 follow-up)
- **GitHub:** (none)
- **0**

## Problem / goal

Ultron **3.0.0** added `ultron/user_memory.py` with per-Discord-user JSON under `ULTRON_STATE_DIR/user_memory/`, plus `/remember` `/forget` `/memory` and NL fast-path remember/forget. Growth is supposed to **refuse** when free disk is low or the file would exceed the per-user cap. Agents should **review** the implementation for correctness/edge cases, **extend tests**, and **harden** anything weak (race conditions, corrupt files, path traversal via owner id, prompt injection via memory content).

## Context (shipped)

- Store: `ultron/user_memory.py` (`UserMemoryStore`, `MemoryDiskFullError`, `assert_can_grow`)
- Wire-up: `ultron/bot.py` (`user_memory`, slash + NL memory outcomes, `format_for_prompt` into router/summary/ask/ol)
- Tests: `tests/test_user_memory.py`
- Docs: `docs/USER_GUIDE.md`, `docs/OPERATIONS.md`

## High-level instructions for coder / reviewer

- Read `ultron/user_memory.py` end-to-end; confirm shrink/clear still works when `min_free_bytes` is huge (already tested — keep that invariant).
- Add tests for: content length cap, clear_all, corrupt JSON recovery, concurrent updates if practical, owner_id sanitization (no `../` path escape).
- Consider redacting or rejecting memory content that looks like secrets (API keys / `Bearer ` / private key headers) — soft warn or hard reject; document choice.
- Ensure prompt injection risk is bounded (`max_chars` on `format_for_prompt`); optionally strip markdown fences / role-play prefixes from stored content.
- If you change shipped behavior, bump **patch** version (`pyproject.toml` + `ultron/__init__.py`) and extend pytest.
- English for any new Discord-facing strings.

## Acceptance criteria

- [x] `.venv/bin/pytest -q tests/test_user_memory.py` passes with expanded cases
- [x] Disk growth still blocked when free space &lt; floor; shrink/forget still allowed
- [x] No secrets written into task notes or logs from fixtures
- [x] Brief note in task **Implementation notes** summarizing findings (pass / fixed issues)

## Implementation notes

**Review (pass + harden):** Core disk growth / shrink invariants were already correct (`assert_can_grow` allows shrink; corrupt JSON recovers to empty doc; per-process `threading.Lock` serializes updates).

**Fixed / added in 3.0.1:**
- **Secrets:** hard-reject on store (`looks_like_secret` — Bearer, PEM private keys, `sk-…`, Slack `xox*`, `api_key=` / `discord_token=` style). Choice: hard reject (not soft warn) so durable memory cannot hold credentials.
- **Prompt hygiene:** `sanitize_memory_text` strips markdown fences and role prefixes (`System:`, `Assistant:`, `ignore previous instructions:`) on validate; `format_for_prompt` re-sanitizes and skips secret-shaped legacy entries; truncation still capped by `max_chars`.
- **Path safety:** `_safe_owner` no longer keeps `.` (so `../escape` cannot embed `..`); `_path` resolves and requires the file under `self.root`.
- **Tests:** content length, clear_all, corrupt JSON, owner sanitization, secrets, sanitize, truncate, legacy secret skip, concurrent different keys + same-key last-write-wins.
- **Docs:** `docs/OPERATIONS.md` notes hard-reject + shrink-on-full-disk.

## Testing instructions

1. From repo root:
   ```bash
   .venv/bin/pip install -q -e .
   .venv/bin/pytest -q tests/test_user_memory.py
   .venv/bin/pytest -q
   ```
   Expect `tests/test_user_memory.py` green (17 cases) and full suite green.
2. Optional manual Discord (allowlisted user, after dump/restart to **3.0.1+**):
   - `/remember preferred_project: 10_AMVARA` → ack
   - `/remember leak: Bearer FAKESECRET_g1h2i3j4k5l6m7n8o9p0` → error mentioning secret (no file growth for that key)
   - `/forget preferred_project` → gone from `/memory`
3. Confirm `__version__` / `pyproject.toml` both show `3.0.1`.
