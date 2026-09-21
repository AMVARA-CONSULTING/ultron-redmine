# Unit tests for whitelist / pending-token state_store

## Tracker
- **Redmine:** (none — enhancement reviewer)
- **GitHub:** (none)
- **0** (when no issue)

## Problem / goal

`ultron/state_store.py` owns whitelist, admins cache, pending `/token` TTL, and atomic JSON writes used by Discord `/approve` and host `ultron add token`. There are **no** dedicated unit tests (`tests/` has zero references). Regressions in TTL expiry, corrupt JSON, or lock/write failure would affect access control with little CI signal.

## Evidence (008 preflight / review)

- Weekly due (`G008_WEEKLY_DUE=1`); pytest 293 pass / smoke OK — no failure signal, coverage gap found on scan.
- Modules with no test refs: `state_store` (also thin `ultron/cli.py` `cmd_add_token` → `consume_token_add_whitelist`).
- No archived task already covering `state_store` unit tests.

## High-level instructions for coder

- Add `tests/test_state_store.py` using `tmp_path` (no real Discord).
- Cover at least: `register_pending_token` + `consume_token_add_whitelist` happy path; unknown / empty / expired token → `ValueError`; replacing a prior pending token for the same user; `is_user_whitelisted` / `is_admin` with missing file, valid JSON, and mtime cache refresh after file change; corrupt / non-list whitelist or admins JSON treated as empty (or documented safe behavior); optional thin test that `cmd_add_token` returns 0/1 for success vs bad token with env pointed at `tmp_path`.
- Do not weaken TTL (`TOKEN_TTL_SECONDS`) or skip locking; keep tests hermetic.
- Patch-bump version if code under `ultron/` changes (tests-only may still bump per project convention when shipping).
- Pass/fail: `.venv/bin/pytest -q tests/test_state_store.py` PASS; full `.venv/bin/pytest -q` still green.
