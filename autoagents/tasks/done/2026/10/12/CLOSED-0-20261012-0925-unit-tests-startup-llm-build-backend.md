---
## Closing summary (TOP)

- **What happened:** Enhancement reviewer filed offline unit coverage for `startup_llm.build_llm_backend` (null/chain primary and cursor-agent wrap).
- **What was done:** Added `tests/test_startup_llm.py` (7 cases) and patch-bumped to **3.0.42** in `pyproject.toml` / `ultron/__init__.py`.
- **What was tested:** Module and full pytest green (**7** / **341** passed); version pins and import spot-check OK.
- **Why closed:** All testing criteria passed; ready to archive.
- **Closed at (UTC):** 2026-10-12 09:29
---

# Unit tests for startup_llm.build_llm_backend

## Tracker
- **Redmine:** (none — enhancement reviewer)
- **GitHub:** (none)
- **0** (when no issue)

## Problem / goal

`ultron/startup_llm.py` **`build_llm_backend`** is the shared constructor for bot startup, **`ultron doctor`**, and **`scripts/smoke_check.py`**: resolve `llm_chain` → `LLMChainClient` / `NullLLMBackend`, optionally wrap with **`LLMWithCursorAgentFallback`** when `cursor_agent.enabled` and `llm_fallback_enabled`.

There are **no** unit tests importing `startup_llm` / `build_llm_backend`. Fallback unwrap is tested around smoke/doctor helpers, but regressions in the assemble-or-wrap branch (wrong workspace root, missing wrap when flags flip, chain vs null) would only show up live.

## Evidence (008 preflight / review)

- Weekly due; empty queue; pytest **334** pass; smoke OK.
- Module map: `startup_llm` has **0** test-file mentions (unlike `pi_resolve` / `cursor_agent` resolve coverage closed 2026-09-28).
- Call sites: `ultron/__main__.py`, `ultron/doctor.py`, `scripts/smoke_check.py`.
- No archived NEW-0/FEAT-0 for `startup_llm` / `build_llm_backend` unit tests.

## High-level instructions for coder

- Add **`tests/test_startup_llm.py`** (or extend an existing LLM/smoke test module) with offline cases:
  - No `llm_chain` → `NullLLMBackend`, `resolved_chain is None`.
  - Minimal fake chain config + patched `resolve_llm_chain` → primary is chain client; `resolved_chain` set.
  - `cursor_agent.enabled` + `llm_fallback_enabled` → backend is `LLMWithCursorAgentFallback` wrapping primary; workspace / timeout taken from config (tmp_path; no network).
  - Fallback disabled or cursor-agent disabled → no wrap (primary only).
- Pass/fail: new tests green; full `.venv/bin/pytest -q` passes; no Discord/network.

## Implementation notes

- 2026-10-12: Added `tests/test_startup_llm.py` with offline coverage for null vs chain primary, cursor-agent wrap (absolute + default workspace, timeout/state_dir), and no-wrap when flags are off. Patch version **3.0.42**.

## Testing instructions

1. Confirm checklist coverage in the new module:
   ```bash
   grep -nE 'build_llm_backend|NullLLMBackend|LLMChainClient|LLMWithCursorAgentFallback|resolve_llm_chain|llm_fallback' tests/test_startup_llm.py
   ```
2. Run the module:
   ```bash
   .venv/bin/pytest -q tests/test_startup_llm.py
   ```
   Expect: **7 passed**.
3. Full suite:
   ```bash
   .venv/bin/pytest -q
   ```
   Expect: green (includes new `test_startup_llm`).
4. Version bump: `pyproject.toml` and `ultron/__init__.py` both **`3.0.42`**.
5. Import spot-check:
   ```bash
   .venv/bin/python -c "from ultron.startup_llm import build_llm_backend, BuiltLLM; from ultron import __version__; print('import_ok', __version__)"
   ```
   Expect: `import_ok 3.0.42`.

## Test report

- **When:** 2026-10-12 09:28:11–09:28:30 UTC
- **Environment:** branch `main` (synced), `.venv` present

### What was tested

Offline unit coverage for `ultron.startup_llm.build_llm_backend` per Testing instructions (grep checklist, module pytest, full suite, version pins, import spot-check). No Discord/network smoke required.

### Results

1. Checklist symbols in `tests/test_startup_llm.py` — **PASS** — grep hit `build_llm_backend`, `NullLLMBackend`, `LLMChainClient`, `LLMWithCursorAgentFallback`, `resolve_llm_chain`, `llm_fallback`.
2. Module pytest — **PASS** — `.venv/bin/pytest -q tests/test_startup_llm.py` → **7 passed** in 1.25s.
3. Full suite — **PASS** — `.venv/bin/pytest -q` → **341 passed** in 7.97s.
4. Version bump — **PASS** — `pyproject.toml` and `ultron/__init__.py` both **`3.0.42`**.
5. Import spot-check — **PASS** — `import_ok 3.0.42`.

### Overall: **PASS**

New `startup_llm` tests cover null vs chain primary, wrap when both flags are on (workspace/timeout/state_dir), and no-wrap when either flag is off. Full suite stayed green; version and import match the task bar. Ready for closing review / archive.
