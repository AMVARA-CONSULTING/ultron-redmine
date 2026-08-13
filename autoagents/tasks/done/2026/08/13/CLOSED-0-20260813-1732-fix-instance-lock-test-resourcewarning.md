---
## Closing summary (TOP)

- **What happened:** Instance-lock contention test left an unclosed stderr pipe, causing a ResourceWarning under `pytest -W default`.
- **What was done:** Switched the hold-script child to `stderr=subprocess.DEVNULL`, adjusted failure messaging, and bumped version to 3.0.26.
- **What was tested:** Targeted instance-lock tests and full suite with `-W default` — 282 passed, no ResourceWarning; version strings match.
- **Why closed:** All acceptance criteria passed; suite clean under `-W default`.
- **Closed at (UTC):** 2026-08-13 17:43
---

# Fix ResourceWarning in bot instance-lock contention test

## Tracker
- **Redmine:** (none — enhancement reviewer)
- **GitHub:** (none)
- **0** (when no issue)

## Problem / goal

`pytest -W default` reports **1 ResourceWarning**: unclosed file from **`tests/test_bot_instance_lock.py::test_second_process_cannot_acquire_while_first_holds_lock`**. The child process is started with **`stderr=subprocess.PIPE`** and the pipe is only read after **`wait`**, which leaves a BufferedReader unclosed on CPython 3.13 and noisies the suite (escape_markdown warnings were already cleaned; this is the remaining warning).

## Evidence (008 preflight / review)

- Weekly 008; **282 passed, 1 warning**.
- Warning points at `_pytest/python.py` / unraisable handler; enabling `-W default` attributes it to the instance-lock contention test’s stderr pipe.
- File: **`tests/test_bot_instance_lock.py`** (~lines 47–62): `Popen(..., stderr=subprocess.PIPE)` then `proc.wait` then conditional `proc.stderr.read()`.

## High-level instructions for coder

- Fix the test so stderr is not left open: prefer **`stderr=subprocess.DEVNULL`** if stderr is unused for the happy path, or **`communicate()`** / context-managed close after read; ensure the hold script still releases the lock.
- Keep Unix skip/`fork` guards unchanged.
- Pass/fail:  
  `.venv/bin/pytest -q tests/test_bot_instance_lock.py -W default`  
  — all green and **no ResourceWarning** / PytestUnraisableExceptionWarning from this test. Full suite should stay green with no new warnings from this file.

## Implementation notes

- `test_second_process_cannot_acquire_while_first_holds_lock`: use `stderr=subprocess.DEVNULL` (same as stdout) so no pipe `BufferedReader` is left open after `wait`.
- On non-zero hold-script exit, raise `AssertionError` with the return code (stderr text no longer captured).
- Patch version bumped to **3.0.26** (`pyproject.toml` + `ultron/__init__.py`).

## Testing instructions

1. From repo root:
   ```bash
   .venv/bin/pytest -q tests/test_bot_instance_lock.py -W default
   ```
   Expect **2 passed** and **no** `ResourceWarning` / `PytestUnraisableExceptionWarning`.

2. Full suite:
   ```bash
   .venv/bin/pytest -q -W default
   ```
   Expect all green; no new warnings from `tests/test_bot_instance_lock.py`.

3. Confirm version strings match:
   ```bash
   .venv/bin/python -c "from ultron import __version__; print(__version__)"
   ```
   Expect `3.0.26`.

## Test report

- **Started:** 2026-08-13 17:42:48 UTC
- **Finished:** 2026-08-13 17:43:06 UTC
- **Environment:** branch `main` (synced), `.venv` pytest, Linux

### What was tested

1. `tests/test_bot_instance_lock.py` with `-W default`
2. Full suite with `-W default`
3. Version string via `ultron.__version__` / `pyproject.toml`

### Results

| Criterion | Result | Evidence |
|-----------|--------|----------|
| Instance-lock tests green, no ResourceWarning / PytestUnraisableExceptionWarning | **PASS** | `2 passed in 4.23s`; no warnings in output |
| Full suite green; no new warnings from instance-lock file | **PASS** | `282 passed in 7.81s`; no warnings |
| Version `3.0.26` in package and pyproject | **PASS** | `__version__` prints `3.0.26`; `pyproject.toml` and `ultron/__init__.py` match |

### Overall: **PASS**

Contention test uses `stderr=subprocess.DEVNULL`; the prior unclosed pipe warning is gone. Suite is clean under `-W default`. Ready for closing reviewer.
