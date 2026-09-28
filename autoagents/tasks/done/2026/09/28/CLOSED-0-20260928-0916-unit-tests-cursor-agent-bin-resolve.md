---
## Closing summary (TOP)

- **What happened:** Enhancement reviewer filed a tests-only gap: `resolve_cursor_agent_bin` had no unit coverage.
- **What was done:** Added `tests/test_cursor_agent.py` with 7 offline cases for env → config → PATH/`~/.local/bin` resolution and missing-binary errors; patch **3.0.39**.
- **What was tested:** Module and full suite green (7 + 322 passed); version sync and import spot-check OK.
- **Why closed:** All test criteria passed; no Redmine/GitHub tracker item.
- **Closed at (UTC):** 2026-09-28 09:21
---

# Unit tests for cursor-agent binary resolution

## Tracker
- **Redmine:** (none — enhancement reviewer)
- **GitHub:** (none)
- **0** (when no issue)

## Problem / goal

`ultron/cursor_agent.py` **`resolve_cursor_agent_bin`** owns the override order for **`/ca`**, Amvara fallback, and LLM fallback sessions: **`ULTRON_CURSOR_AGENT_BIN`** → **`cursor_agent.bin_path`** → **`PATH`** / `~/.local/bin/cursor-agent`. There are **no** unit tests referencing this resolver. Regressions would only show up as live “cursor-agent not found” / non-executable errors in Discord.

## Evidence (008 preflight / review)

- Weekly due; empty queue; pytest **315** pass; smoke OK.
- `tests/` has zero imports of `resolve_cursor_agent_bin` (pi has partial coverage in `tests/test_pi_agent.py`; cursor-agent does not).
- OPERATIONS already documents the override path; this task is **tests only** (no docs rewrite unless a claim is wrong).
- No archived NEW-0/FEAT-0 for cursor-agent bin resolve tests.

## High-level instructions for coder

- Add focused tests (new `tests/test_cursor_agent.py` or extend an existing module) for **`resolve_cursor_agent_bin`**:
  - Prefer env override when executable; raise on non-executable env / `bin_path`.
  - Prefer `cursor_agent.bin_path` when set and executable.
  - Fall through to `shutil.which` / `~/.local/bin` with tmp_path / monkeypatch (no real Cursor install required).
  - Missing binary → clear `RuntimeError` matching production message tone.
- Keep tests offline (no network, no Discord). Do not expand into full session/`call_cursor_agent_session` integration unless trivial.
- Pass/fail: new tests green under `.venv/bin/pytest -q`; suite still passes.

## Implementation notes

- 2026-09-28: Added `tests/test_cursor_agent.py` (7 offline cases for `resolve_cursor_agent_bin`). Patch version **3.0.39**.

## Testing instructions

1. Confirm coverage of the resolver checklist:
   ```bash
   grep -nE 'resolve_cursor_agent_bin|ULTRON_CURSOR_AGENT_BIN|bin_path|which|local/bin|not found on PATH' tests/test_cursor_agent.py
   ```
2. Run the new module:
   ```bash
   .venv/bin/pytest -q tests/test_cursor_agent.py
   ```
   Expect: **7 passed**.
3. Full suite:
   ```bash
   .venv/bin/pytest -q
   ```
   Expect: green (includes `test_cursor_agent`).
4. Version bump: `pyproject.toml` and `ultron/__init__.py` both **`3.0.39`**.
5. Import spot-check:
   ```bash
   .venv/bin/python -c "from ultron.cursor_agent import resolve_cursor_agent_bin; from ultron import __version__; print('import_ok', __version__)"
   ```
   Expect: `import_ok 3.0.39`.

## Test report

- **Started:** 2026-09-28 09:20:20 UTC
- **Finished:** 2026-09-28 09:20:45 UTC
- **Environment:** branch `main`, `.venv` at `/root/Repos/ultron-redmine/.venv/bin/python`

### What was tested

Offline unit coverage for `resolve_cursor_agent_bin` per Testing instructions (grep checklist, module pytest, full suite, version sync, import spot-check). No Discord / smoke required.

### Results

1. **Resolver checklist coverage** — **PASS** — grep hits for `resolve_cursor_agent_bin`, `ULTRON_CURSOR_AGENT_BIN`, `bin_path`, `which`, and `not found on PATH`; `~/.local/bin` covered via `test_resolve_falls_through_to_local_bin` (`tmp_path / ".local" / "bin" / "cursor-agent"`).
2. **Module pytest** — **PASS** — `.venv/bin/pytest -q tests/test_cursor_agent.py` → **7 passed** in 0.09s.
3. **Full suite** — **PASS** — `.venv/bin/pytest -q` → **322 passed** in 8.33s.
4. **Version bump** — **PASS** — `pyproject.toml` and `ultron/__init__.py` both `3.0.39`.
5. **Import spot-check** — **PASS** — `import_ok 3.0.39`.

### Overall: **PASS**

Focused offline tests cover env → config → PATH/`~/.local/bin` → clear missing-binary error. Suite stayed green at 322; version strings match. Ready to close.
