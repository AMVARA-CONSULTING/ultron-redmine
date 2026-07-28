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

- [x] `/help` lists remember/forget/memory and notes Confirm on mutating commands
- [x] Docs mention fast-path + disk check before memory growth
- [x] `.venv/bin/pytest -q` still green; no secrets in docs

## Implementation notes

- **`_HELP_TEXT`**: clarified `/forget` `clear_all`, explicit Confirm blurb for Redmine writes, @mention **fast-path** line, memory still available without `llm_chain`; `/status` help mentions durable memory file count.
- **`UserMemoryStore.count_user_files` / `status_line`**: `/status` Features section shows `user_memory: ready (N files)` (no contents/paths with secrets).
- **Docs**: USER_GUIDE subsections **Durable memory** + **Write confirmation**; README Confirm/fast-path/disk note; OPERATIONS `/status` memory count mention.
- Version **3.0.2 → 3.0.3**.

## Testing instructions

Automated:

```bash
.venv/bin/pip install -q -e .
.venv/bin/pytest -q tests/test_help_status_parity.py tests/test_user_memory.py
.venv/bin/pytest -q
```

Expect: parity + memory tests PASS; full suite green (244 passed at implement time).

Manual (after dump/restart on Discord host):

1. `/help` — see `/remember`, `/forget` (`clear_all`), `/memory`, Confirm blurb, fast-path on @mention.
2. `/status` — line `user_memory: ready (N files)` under Features (N ≥ 0).
3. Spot-check USER_GUIDE Durable memory / Write confirmation against live Confirm UX on `/log_time` Cancel.
