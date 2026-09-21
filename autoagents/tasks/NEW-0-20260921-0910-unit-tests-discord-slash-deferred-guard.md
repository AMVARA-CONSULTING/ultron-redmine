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
