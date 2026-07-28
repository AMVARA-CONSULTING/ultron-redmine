---
## Closing summary (TOP)

- **What happened:** `ultron doctor` reported paths and bindings but never checked user_memory dir presence, writability, or free disk vs the growth floor.
- **What was done:** Added read-only User memory health lines (path, present/missing, writable, free disk vs 100 MiB, file count); wired into doctor after state_dir; tests and OPERATIONS note; version 3.0.8.
- **What was tested:** `tests/test_doctor.py` (8 passed), full suite (272 passed), live doctor User memory block, missing-dir non-destructive — all PASS.
- **Why closed:** All pass/fail criteria passed; ready to archive (product changes may still need commit on main).
- **Closed at (UTC):** 2026-07-28 23:14
---
# Extend ultron doctor with user_memory health line

## Tracker
- **Redmine:** (none — enhancement reviewer)
- **GitHub:** (none)
- **0**

## Problem / goal

Ultron **3.0** stores per-user durable memory under **`ULTRON_STATE_DIR/user_memory/`** and refuses growth when free disk is below the store’s floor. **`ultron doctor`** reports paths, bindings, Redmine, and LLM, but never mentions whether the memory directory exists, is writable, or how free space compares to the growth guard. Operators debugging “remember failed” / disk-full errors lack a one-shot host check.

## Evidence (008 preflight / review)

- Weekly due; `ultron/doctor.py` has no `user_memory` references; OPERATIONS documents memory under state_dir but Health checks only name smoke_check.
- Distinct from **FEAT-0-…-review-user-memory-disk-guards** (harden store + pytest) and **FEAT-0-…-help-docs-parity** (Discord/docs copy).
- Constants / helpers live in `ultron/user_memory.py` (`assert_can_grow`, min free bytes).

## High-level instructions for coder

- After printing `state_dir` (or in a short **User memory** section), report: directory present/created?, writable?, approximate free bytes vs the store’s minimum free floor, and optionally count of `user_*.json` files (no contents).
- Reuse existing APIs from `ultron/user_memory.py` where practical; do not print memory values or Discord ids beyond file count.
- Keep doctor read-only: do **not** create user files; creating the empty `user_memory/` dir is optional and should be documented if done.
- Extend `tests/test_doctor.py` with a tmp_path case asserting the new line appears (and disk-low messaging if easy to mock).
- Patch bump (`pyproject.toml` + `ultron/__init__.py`) when changing `ultron/doctor.py`.
- One-line OPERATIONS Health checks note optional.

## Pass / fail criteria for tester

- [x] `ultron doctor` (or documented CLI) shows a user_memory health line without dumping secrets or entry values.
- [x] `.venv/bin/pytest -q tests/test_doctor.py` PASS.
- [x] Behavior remains non-destructive on a normal `data/` tree.

## Implementation notes

- Added read-only `doctor_user_memory_lines()` / `count_user_memory_files()` / `MIN_FREE_BYTES` in `ultron/user_memory.py` (no mkdir, no entry contents).
- `ultron doctor` prints a **User memory** block after `state_dir` (path, present/missing, writable, free disk vs 100 MiB floor, `user_*.json` count).
- Tests: present+count, missing (no create), mocked disk-low messaging.
- Docs: one OPERATIONS Health checks bullet. Version **3.0.8**.

## Testing instructions

1. From repo root:
   ```bash
   .venv/bin/pip install -q -e .
   .venv/bin/pytest -q tests/test_doctor.py
   .venv/bin/pytest -q
   ```
   Expect `tests/test_doctor.py` green (including user_memory cases) and full suite green.
2. With a valid `config.yaml` (Discord/Redmine optional for this check):
   ```bash
   .venv/bin/ultron doctor
   # or: .venv/bin/python -m ultron doctor
   ```
   Expect a **User memory** section after `state_dir` with `directory` / `writable` / `free disk` / `user_*.json files` — no JSON entry values or Discord ids beyond the file count.
3. Confirm non-destructive: if `user_memory/` was missing under `ULTRON_STATE_DIR`, doctor must leave it missing (does not create the dir or user files).
4. Confirm `__version__` / `pyproject.toml` both show `3.0.8`.

## Test report

- **Started:** 2026-07-28T23:13:09Z
- **Finished:** 2026-07-28T23:13:39Z
- **Environment:** branch `main`, `.venv` (Python 3.13), editable install; local uncommitted doctor/user_memory changes under test.
- **What was tested:** `tests/test_doctor.py` + full pytest; live `ultron doctor`; missing-`user_memory/` non-destructive check; version sync `3.0.8`.

### Results

| Criterion | Result | Evidence |
|-----------|--------|----------|
| Doctor User memory block, no secrets/entry dumps | **PASS** | `ultron doctor` printed path / present / writable / free disk / `user_*.json files: 0` after `state_dir`; no entry values or Discord ids |
| `pytest tests/test_doctor.py` | **PASS** | `8 passed in 1.04s` |
| Full suite | **PASS** | `272 passed, 35 warnings in 7.51s` |
| Non-destructive when dir missing | **PASS** | Temp `ULTRON_STATE_DIR` with no `user_memory/`: doctor reported `directory: missing`; dir still absent afterward |
| Version `3.0.8` | **PASS** | `ultron/__init__.py` and `pyproject.toml` both `3.0.8`; doctor banner `version 3.0.8` |

**Overall: PASS**

Operator feedback: Doctor’s new User memory block is clear and safe for operators debugging disk/memory issues. Read-only behavior holds when the directory is absent. Ready to close; product changes still need a commit on `main` if not already landed.
