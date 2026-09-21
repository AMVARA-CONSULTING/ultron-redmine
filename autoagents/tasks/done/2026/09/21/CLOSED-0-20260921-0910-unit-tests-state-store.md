---
## Closing summary (TOP)

- **What happened:** `ultron/state_store.py` had no dedicated unit tests despite owning whitelist, admins cache, and pending `/token` TTL used for access control.
- **What was done:** Added `tests/test_state_store.py` (10 hermetic cases: register/consume, expiry, cache refresh, corrupt JSON, `cmd_add_token`); patch **3.0.37**; no behavior change in `state_store`.
- **What was tested:** Checklist greps, dedicated suite (10 passed), full pytest (303 passed), version parity, offline register/consume spot-check; overall PASS.
- **Why closed:** All acceptance criteria and the test report passed.
- **Closed at (UTC):** 2026-09-21 09:24
---

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

## Implementation notes

- Added **`tests/test_state_store.py`** (10 cases): register/consume happy path; empty/unknown/expired tokens; replace pending for same user; whitelist/admins missing + valid + mtime cache refresh; non-list JSON treated as empty; skip non-int entries; `remove_user_from_whitelist`; `TOKEN_TTL_SECONDS == 300`; thin `cmd_add_token` 0/1 via mocked `load_env`.
- No changes to `ultron/state_store.py` behavior.
- Patch version bumped to **`3.0.37`** in `pyproject.toml` and `ultron/__init__.py`.

## Testing instructions

1. Confirm the new module exists and covers the task checklist:
   ```bash
   test -f tests/test_state_store.py && rg -n 'register_pending|consume_token|empty token|unknown token|expired|is_user_whitelisted|is_admin|non.list|cmd_add_token|TOKEN_TTL' tests/test_state_store.py
   ```
2. Run the dedicated suite:
   ```bash
   .venv/bin/pytest -q tests/test_state_store.py
   ```
   Expect: all tests pass (10).
3. Full regression:
   ```bash
   .venv/bin/pytest -q
   ```
   Expect: green (includes `test_state_store`).
4. Confirm version bump: **`pyproject.toml`** and **`ultron/__init__.py`** both **`3.0.37`**.
5. Spot-check register/consume offline:
   ```bash
   .venv/bin/python -c "
   from pathlib import Path
   import tempfile
   from ultron.state_store import register_pending_token, consume_token_add_whitelist, is_user_whitelisted
   d = Path(tempfile.mkdtemp())
   t = register_pending_token(d, 12345)
   assert consume_token_add_whitelist(d, t) == 12345
   assert is_user_whitelisted(d, 12345)
   print('state_store_ok')
   "
   ```
   Expect: `state_store_ok`.

## Test report

- **Date/time (UTC):** 2026-09-21 09:23 UTC
- **Environment:** branch `main`, `.venv` (`Already up to date` after `./scripts/git-sync-main.sh`)

### What was tested

Dedicated `tests/test_state_store.py` coverage checklist, dedicated pytest, full suite regression, version `3.0.37` parity, and offline register/consume spot-check. No Discord/smoke required (unit-test-only task).

### Results

1. **Coverage checklist (`tests/test_state_store.py` exists + expected symbols):** **PASS** — file present; matches for register/consume, empty/unknown/expired, whitelist/admin, non-list, `cmd_add_token`, `TOKEN_TTL`.
2. **Dedicated suite:** **PASS** — `.venv/bin/pytest -q tests/test_state_store.py` → **10 passed** in 0.16s.
3. **Full regression:** **PASS** — `.venv/bin/pytest -q` → **303 passed** in 8.07s (includes `test_state_store`).
4. **Version bump:** **PASS** — `pyproject.toml` and `ultron.__version__` both **`3.0.37`**.
5. **Offline register/consume spot-check:** **PASS** — printed `state_store_ok`.

### Overall: **PASS**

Operator feedback: New state_store unit tests meet the task checklist and stay hermetic. Full suite is green with the added module; version bump is consistent. Safe to close; no product-code fixes needed.
