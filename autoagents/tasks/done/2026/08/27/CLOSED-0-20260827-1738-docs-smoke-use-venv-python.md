---
## Closing summary (TOP)

- **What happened:** RELEASE_CHECKLIST and OPERATIONS Health smoke blocks used bare `python`, which fails on Debian/Ubuntu hosts without a `python` package or activated venv.
- **What was done:** Pointed smoke/pytest/doctor examples in those two docs at `.venv/bin/python` / `.venv/bin/pytest`; version **3.0.32**.
- **What was tested:** All tester checks passed (no bare python lines, venv forms present, documented smoke OK); pytest **284** green.
- **Why closed:** All acceptance criteria passed; ops/release snippets match Debian/venv reality.
- **Closed at (UTC):** 2026-08-27 17:58
---

# Point release/ops smoke snippets at `.venv/bin/python`

## Tracker
- **Redmine:** (none — enhancement reviewer)
- **GitHub:** (none)
- **0** (when no issue)

## Problem / goal

**`docs/RELEASE_CHECKLIST.md`** and **`docs/OPERATIONS.md`** Health smoke blocks use bare **`python`** / **`python -m …`**. On Debian/Ubuntu hosts without a `python` package (only `python3`) and without an activated venv, those commands fail (`python: command not found`). Task testing and prior CLOSED tasks already standardize on **`.venv/bin/python`**.

## Evidence (008 preflight / review)

- Weekly due; 008 smoke attempt with `python scripts/smoke_check.py` failed on this host; `.venv/bin/python scripts/smoke_check.py` succeeded (all OK lines).
- `docs/OPERATIONS.md` ~line 200: `python scripts/smoke_check.py`.
- `docs/RELEASE_CHECKLIST.md`: `python -m pytest`, `python scripts/smoke_check.py`, `python -m ultron doctor`.
- `README.md` Quick start activates the venv first (OK); ops/release snippets often run without that context.

## High-level instructions for coder

- In **`docs/RELEASE_CHECKLIST.md`** and **`docs/OPERATIONS.md`**, change smoke/pytest/doctor examples to **`.venv/bin/python`** / **`.venv/bin/pytest`** (or an explicit `source .venv/bin/activate` then `python`), matching systemd install docs that already use `python3 -m venv` + `.venv/bin/pip`.
- Keep **`ultron doctor`** / **`ultron wizard`** as console-script alternatives where the venv is on `PATH`.
- Do not change CI Dockerfiles that correctly use image `python`.
- Pass: no bare `python scripts/smoke_check.py` / `python -m pytest` in those two docs without venv activation; commands work on a fresh Debian-style checkout with `.venv` installed.
- Tester: grep the two docs for `^python ` / fenced `python ` smoke lines; confirm venv-qualified forms present.

## Testing instructions

1. Confirm no bare smoke/pytest/doctor lines remain:
   ```bash
   grep -nE '^(python |# or: python )' docs/RELEASE_CHECKLIST.md docs/OPERATIONS.md || echo 'OK: no bare python lines'
   grep -nE '`python -m |`python scripts/' docs/RELEASE_CHECKLIST.md docs/OPERATIONS.md || echo 'OK: no bare python in backticks'
   ```
2. Confirm venv-qualified forms are present:
   ```bash
   grep -n '\.venv/bin/pytest\|\.venv/bin/python' docs/RELEASE_CHECKLIST.md docs/OPERATIONS.md
   ```
   Expect: RELEASE has `.venv/bin/pytest`, `.venv/bin/python scripts/smoke_check.py`, `.venv/bin/python -m ultron doctor`; OPERATIONS Health checks has `.venv/bin/python scripts/smoke_check.py`. Keep `python3 -m venv` and console-script `ultron doctor` / `ultron wizard`.
3. Run the documented smoke command:
   ```bash
   .venv/bin/python scripts/smoke_check.py
   ```
4. Confirm version bump: **`pyproject.toml`** and **`ultron/__init__.py`** both **`3.0.32`**.
5. Regression: `.venv/bin/pytest -q` (expect pass; docs-only + version bump).

## Test report

- **Date/time (UTC):** 2026-08-27 17:57:52 – 17:58:17 UTC
- **Environment:** branch `main` (synced), `.venv` Python 3.13.5

### What was tested

Docs smoke/pytest/doctor snippets in `docs/RELEASE_CHECKLIST.md` and `docs/OPERATIONS.md` use `.venv/bin/python` / `.venv/bin/pytest`; version `3.0.32`; smoke + full pytest regression.

### Results

1. No bare `python` / backtick smoke lines in the two docs — **PASS** (`OK: no bare python lines`; `OK: no bare python in backticks`).
2. Venv-qualified forms present — **PASS** (RELEASE: `.venv/bin/pytest`, `.venv/bin/python scripts/smoke_check.py`, `.venv/bin/python -m ultron doctor`; OPERATIONS: `.venv/bin/python scripts/smoke_check.py`). `python3 -m venv` and console-script `ultron doctor` / `ultron wizard` retained.
3. Documented smoke command — **PASS** (`.venv/bin/python scripts/smoke_check.py`: all OK lines including version 3.0.32, Redmine, LLM).
4. Version bump `3.0.32` in `pyproject.toml` and `ultron/__init__.py` — **PASS**.
5. `.venv/bin/pytest -q` — **PASS** (284 passed in 7.75s).

### Overall: **PASS**

Operator feedback: Ops/release smoke snippets now match the Debian/venv reality already used by testing; bare `python` no longer appears in those two docs. Smoke and full suite are green on this host with the documented `.venv/bin/python` path.
