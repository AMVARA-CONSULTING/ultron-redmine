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
