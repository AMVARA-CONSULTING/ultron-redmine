---
## Closing summary (TOP)

- **What happened:** `scripts/smoke_check.py` skipped LLM with `unexpected backend LLMWithCursorAgentFallback` instead of probing the chain like `ultron doctor`.
- **What was done:** Smoke unwraps via `llm_chain_client`, reports OK with fallback note, added `tests/test_smoke_check.py` and an OPERATIONS health-check note.
- **What was tested:** Focused pytest 14 passed; live smoke OK LLM with cursor-agent fallback; doctor LLM OK — all PASS.
- **Why closed:** All pass/fail criteria passed; no product issues found.
- **Closed at (UTC):** 2026-07-28 22:51
---
# Fix smoke_check LLM probe for cursor-agent fallback wrapper

## Tracker
- **Redmine:** (none — enhancement reviewer)
- **GitHub:** (none)
- **0**

## Problem / goal

On hosts where chat LLM is wrapped in **`LLMWithCursorAgentFallback`** (default when `cursor_agent.llm_fallback_enabled` is on), `scripts/smoke_check.py` prints **`SKIP LLM: unexpected backend LLMWithCursorAgentFallback`** and never pings the chain. Operators get a false “LLM not checked” signal even though Redmine OK and the live bot uses Gemma. **`ultron doctor`** already unwraps via **`llm_chain_client`** — smoke should match.

## Evidence (008 preflight / review)

- Weekly due (`G008_WEEKLY_DUE=1`, ~10 days since last 008 stamp); live smoke on this host: Redmine OK, then `SKIP LLM: unexpected backend LLMWithCursorAgentFallback`.
- `ultron/doctor.py` uses `llm_chain_client(llm)` then `ping_primary()`; `scripts/smoke_check.py` only accepts bare `LLMChainClient`.
- Helper already exists: `ultron/llm_cursor_fallback.py` → `llm_chain_client`.
- Related but distinct from **FEAT-0-…-integration-smoke-memory-confirm** (memory/confirm Discord checklist + optional offline imports) — this task is only the false LLM SKIP.

## High-level instructions for coder

- In `scripts/smoke_check.py`, after `build_llm_backend`, unwrap with `llm_chain_client` (same pattern as `ultron/doctor.py`); ping the chain primary; mention fallback in the OK line when the outer type is `LLMWithCursorAgentFallback`.
- Keep `NullLLMBackend` → SKIP; unknown unwrapped backends → clear SKIP/FAIL message.
- Add a focused unit test (or extend doctor/smoke tests) that mocks a wrapped backend and asserts smoke does not treat it as “unexpected”.
- Optional tiny doc note under OPERATIONS **Health checks** that smoke unwraps the cursor-agent LLM fallback wrapper.
- Patch bump only if you change shipped `ultron/` (script-only + tests may still warrant patch per project norms if tests ship with the package — follow existing smoke/doctor change style).

## Pass / fail criteria for tester

- [ ] With local `.env` + `llm_chain` + cursor LLM fallback enabled: `python scripts/smoke_check.py` prints **OK LLM** (model + endpoint), not unexpected-backend SKIP.
- [ ] `ultron doctor` still OK for LLM (no regression).
- [ ] `.venv/bin/pytest -q` for any new/changed tests PASS.

## Testing instructions

### Automated

```bash
cd /root/Repos/ultron-redmine
.venv/bin/pytest -q tests/test_smoke_check.py tests/test_doctor.py tests/test_llm_cursor_fallback.py
```

Expect all PASS (14 at implement time for that subset).

### Live smoke / doctor (needs `.env` + llm_chain + cursor LLM fallback)

```bash
python scripts/smoke_check.py
.venv/bin/python -m ultron doctor
```

Expect smoke: **`OK LLM: … + cursor-agent LLM fallback`** (not `SKIP LLM: unexpected backend LLMWithCursorAgentFallback`).
Expect doctor: LLM OK line still present (no regression).

### Notes for tester

- Script-only + tests + OPERATIONS note; no `ultron/` version bump for this task.
- New helper: `scripts/smoke_check.report_llm` (tested via `tests/test_smoke_check.py`).

## Test report

- **Date/time (UTC):** 2026-07-28 22:50 UTC
- **Environment:** branch `main`, `.venv` pytest/python; live `.env` + `config.yaml` with llm_chain + cursor-agent LLM fallback

### What was tested

1. Focused pytest: `tests/test_smoke_check.py`, `tests/test_doctor.py`, `tests/test_llm_cursor_fallback.py`
2. Live `scripts/smoke_check.py` (via `.venv/bin/python`)
3. Live `.venv/bin/python -m ultron doctor`

### Results

| Criterion | Result | Evidence |
|-----------|--------|----------|
| smoke_check prints OK LLM (not unexpected-backend SKIP) | **PASS** | `OK LLM: chain primary model='gemma4:latest' @ amvara8:11434/v1 + cursor-agent LLM fallback` |
| `ultron doctor` LLM OK (no regression) | **PASS** | `LLM: OK (chain primary model 'gemma4:latest' @ amvara8:11434/v1 + cursor-agent LLM fallback)` |
| Focused pytest PASS | **PASS** | `14 passed in 1.25s` |

### Overall: **PASS**

Smoke now unwraps `LLMWithCursorAgentFallback` the same way doctor does; operators get a real LLM probe instead of a false SKIP. No product-code issues found; task can close.
