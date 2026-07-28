# Improve help/status/docs parity for Ultron 3.0 features

## Tracker
- **Redmine:** (none — Ultron 3.0 follow-up)
- **GitHub:** (none)
- **0**

## Problem / goal

`/help`, `/status`, README, and USER_GUIDE may still under-describe 3.0 behavior (memory, confirms, fast-path). Align Discord-facing help and operator docs with runtime so allowlisted users discover `/remember` and know writes need Confirm.

## Context (shipped)

- `_HELP_TEXT` in `ultron/bot.py` (partially updated in 3.0.0)
- `docs/USER_GUIDE.md`, `docs/OPERATIONS.md`, `README.md`
- `/status` formatter in `bot.py` — check whether memory store path / entry counts should appear (keep non-secret)

## High-level instructions for coder

- Diff `_HELP_TEXT` vs actual slash commands; fix omissions (clear_all on `/forget`, confirm on writes, fast-path mention one line).
- USER_GUIDE: short “Durable memory” + “Write confirmation” subsections if missing detail.
- Optional `/status` line: `user_memory: ready (N files)` without dumping contents.
- English only for Discord strings; keep docs consistent with OPERATIONS disk-guard note.
- Patch bump if `ultron/` changes.

## Acceptance criteria

- [ ] `/help` lists remember/forget/memory and notes Confirm on mutating commands
- [ ] Docs mention fast-path + disk check before memory growth
- [ ] `.venv/bin/pytest -q` still green; no secrets in docs
