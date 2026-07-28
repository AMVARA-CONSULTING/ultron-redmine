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

- [ ] `.venv/bin/pytest -q tests/test_user_memory.py` passes with expanded cases
- [ ] Disk growth still blocked when free space &lt; floor; shrink/forget still allowed
- [ ] No secrets written into task notes or logs from fixtures
- [ ] Brief note in task **Implementation notes** summarizing findings (pass / fixed issues)
