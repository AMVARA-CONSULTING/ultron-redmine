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
