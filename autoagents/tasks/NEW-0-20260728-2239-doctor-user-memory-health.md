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

- [ ] `ultron doctor` (or documented CLI) shows a user_memory health line without dumping secrets or entry values.
- [ ] `.venv/bin/pytest -q tests/test_doctor.py` PASS.
- [ ] Behavior remains non-destructive on a normal `data/` tree.
