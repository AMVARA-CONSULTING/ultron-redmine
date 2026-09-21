---
## Closing summary (TOP)

- **What happened:** Coverage gap for `discord_slash` defer/followup helpers was closed with a dedicated unit-test module.
- **What was done:** Added `tests/test_discord_slash.py` (12 async tests) for `edit_or_followup` and `DeferredInteractionGuard`; bumped version to 3.0.38.
- **What was tested:** Dedicated suite 12 passed; full suite 315 passed; version and offline import checks PASS.
- **Why closed:** All acceptance criteria passed; ready to archive.
- **Closed at (UTC):** 2026-09-21 09:34
---

# Unit tests for discord_slash defer / followup helpers

## Tracker
- **Redmine:** (none — enhancement reviewer)
- **GitHub:** (none)
- **0** (when no issue)

## Problem / goal

Long-running slash paths (`/audit`, `/ca`, `/pi`, `/upgrade`) rely on `ultron/discord_slash.py`: **`edit_or_followup`** (edit original vs followup when the interaction token is dead) and **`DeferredInteractionGuard`** (warn before ~15m Discord token expiry, then reports-channel handoff). There are **no** unit tests referencing this module. Silent regressions would strand operators with a stuck “thinking” message.

## Evidence (008 preflight / review)

- Weekly due; pytest/smoke green — coverage gap on scan.
- `docs/OPERATIONS.md` documents the ~15 minute token / reports-channel switch; code lives in `discord_slash.py` + `is_unknown_interaction_error`.
- No archived task for `DeferredInteractionGuard` / `edit_or_followup` tests.

## High-level instructions for coder

- Add `tests/test_discord_slash.py` with async tests and lightweight mocks of `discord.Interaction` / `HTTPException` (no live Discord).
- Cover: `edit_or_followup` success via `edit_original_response`; fallback to `followup.send` on unknown-interaction / 401 / code 50027; return `False` when both fail with dead-token errors; re-raise unexpected HTTP errors.
- Cover `DeferredInteractionGuard`: with a tiny `warn_after_seconds`, after sleep the original response is edited to the long-running notice and `use_feedback` becomes true; `stop()` cancels the warn task so the notice is not posted.
- Reuse patterns from `tests/test_discord_interaction_errors.py` / other async Discord mocks in the suite.
- Pass/fail: `.venv/bin/pytest -q tests/test_discord_slash.py` PASS; full suite still green.

## Implementation notes

- Added `tests/test_discord_slash.py` (12 tests): `edit_or_followup` edit/followup/dead-token/`False`/re-raise paths; `DeferredInteractionGuard` warn + `stop()` cancel.
- Patch version **3.0.38** in `pyproject.toml` and `ultron/__init__.py`.

## Testing instructions

1. Confirm the new module covers the checklist:
   ```bash
   test -f tests/test_discord_slash.py && rg -n 'edit_or_followup|DeferredInteractionGuard|unknown_interaction|401|50027|use_feedback|stop_cancels|reraises' tests/test_discord_slash.py
   ```
2. Dedicated suite:
   ```bash
   .venv/bin/pytest -q tests/test_discord_slash.py
   ```
   Expect: **12 passed**.
3. Full regression:
   ```bash
   .venv/bin/pytest -q
   ```
   Expect: green (includes `test_discord_slash`).
4. Confirm version bump: **`pyproject.toml`** and **`ultron/__init__.py`** both **`3.0.38`**.
5. Spot-check import (offline, no live Discord):
   ```bash
   .venv/bin/python -c "from ultron.discord_slash import DeferredInteractionGuard, edit_or_followup; print('ok')"
   ```

## Test report

- **Date/time (UTC):** 2026-09-21 09:33:44 start → 09:34:11 end
- **Environment:** branch `main` @ `d303644`, `.venv` pytest

### What was tested

1. Checklist coverage in `tests/test_discord_slash.py` (edit_or_followup / DeferredInteractionGuard / 401 / 50027 / use_feedback / stop_cancels / reraises).
2. Dedicated suite: `.venv/bin/pytest -q tests/test_discord_slash.py`
3. Full regression: `.venv/bin/pytest -q`
4. Version bump `3.0.38` in `pyproject.toml` and `ultron/__init__.py`
5. Offline import of `DeferredInteractionGuard` and `edit_or_followup`

### Results

| Criterion | Result | Evidence |
|-----------|--------|----------|
| New test module covers checklist keywords | **PASS** | Matches for edit_or_followup, DeferredInteractionGuard, unknown_interaction, 401, 50027, use_feedback, stop_cancels, reraises |
| Dedicated suite 12 passed | **PASS** | `12 passed in 0.54s` |
| Full suite green | **PASS** | `315 passed in 8.59s` |
| Version 3.0.38 both places | **PASS** | `pyproject.toml` and `ultron/__init__.py` both `3.0.38` |
| Offline import | **PASS** | printed `ok` |

### Overall: **PASS**

Operator feedback: Coverage for `edit_or_followup` dead-token fallbacks and `DeferredInteractionGuard` warn/stop paths looks solid with light mocks and no live Discord. Full suite stayed green; ready for closing reviewer / commit of the uncommitted test file and version bump.
