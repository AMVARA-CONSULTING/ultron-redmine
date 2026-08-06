# Document Discord Watching presence (Ultron version)

## Tracker
- **Redmine:** (none — enhancement reviewer)
- **GitHub:** (none)
- **0** (when no issue)

## Problem / goal

Ultron **3.0.11** sets Discord **Watching Ultron vX.Y.Z** on connect (`watching_presence_name` / `_set_watching_presence` in `ultron/bot.py`, covered by `tests/test_watching_presence.py`), but operator docs and offline smoke do not mention it. Operators verifying a dump/restart have no checklist line for presence, and `scripts/smoke_check.py` has no offline assert for the presence name helper (unlike version / user_memory / nl_fastpath / write_confirm).

## Evidence (008 preflight / review)

- Weekly due (`G008_WEEKLY_DUE=1`, 8 days since last 008 review); no doc_drift SIGNAL from preflight version mismatch.
- Shipped in commit `9a07a61` (Watching presence); absent from `docs/OPERATIONS.md` Manual Discord smoke, `docs/RELEASE_CHECKLIST.md`, `docs/USER_GUIDE.md`, and smoke offline OK lines.
- No existing open/archived `FEAT-0`/`NEW-0` task covers Watching presence.

## High-level instructions for coder

- Document the expected presence string (**Watching Ultron v\<version\>**) in `docs/OPERATIONS.md` Manual Discord smoke (and a short note in `docs/RELEASE_CHECKLIST.md` § Manual sanity). Optional one-liner in `docs/USER_GUIDE.md` only if it helps end users recognize the bot.
- Extend `scripts/smoke_check.py` with an offline check that `watching_presence_name()` matches `Ultron v{__version__}` (mirror existing OK lines); update `tests/test_smoke_check.py` if present.
- Pass: docs mention presence; smoke prints an OK watching/presence line; `.venv/bin/pytest -q` still green.
- Fail: presence still undocumented and smoke unchanged.

## Implementation notes (coder)

- Documented **Watching Ultron vX.Y.Z** in `docs/OPERATIONS.md` Manual Discord smoke (item 1), smoke expect line, `docs/RELEASE_CHECKLIST.md` § Manual sanity + offline OK list, and `docs/USER_GUIDE.md` Quick Discord smoke.
- `scripts/smoke_check.py`: offline assert `watching_presence_name() == f"Ultron v{__version__}"` → **OK watching_presence**.
- `tests/test_smoke_check.py`: asserts the new OK line.
- Patch bump **3.0.17 → 3.0.18** (`pyproject.toml` + `ultron/__init__.py`).

## Testing instructions

1. **Offline smoke**
   ```bash
   .venv/bin/python scripts/smoke_check.py
   ```
   Expect a line: `OK watching_presence: Ultron v3.0.18` (or current `__version__`), plus existing OK version / user_memory / nl_fastpath / write_confirm.

2. **Pytest**
   ```bash
   .venv/bin/pip install -q -e .
   .venv/bin/pytest -q tests/test_smoke_check.py tests/test_watching_presence.py
   ```
   Expect all green; `test_check_ultron30_offline` must see `OK watching_presence:`.

3. **Docs spot-check**
   - `docs/OPERATIONS.md` Manual Discord smoke step 1 mentions **Watching Ultron vX.Y.Z**.
   - `docs/RELEASE_CHECKLIST.md` Manual sanity has a Presence checkbox.
   - `docs/USER_GUIDE.md` Quick Discord smoke lists Watching presence.

4. **Manual Discord (optional, after dump/restart)**
   - Member list / bot profile shows **Watching Ultron v\<version\>** matching the running release.
