# Audit Gemma prompt budgets (ticket truncate + memory injection)

## Tracker
- **Redmine:** (none — Ultron 3.0 follow-up)
- **GitHub:** (none)
- **0**

## Problem / goal

Ultron runs **gemma4** (~9GB) via Ollama. 3.0.0 tightened `format_issue_for_summary` defaults and injects user memory into router/summary/ask/ol. Agents should **measure** typical prompt sizes, ensure caps are enough for useful summaries without blowing context, and tune constants / docs for operators.

## Context (shipped)

- `ultron/textutil.py` — `max_description_chars=4000`, journals 12×800, `max_total_chars=8000`
- `ultron/workflows.py` — shorter SUMMARY/ASK systems; `memory_block` prefix
- `ultron/nl_router.py` — memory appended to router system
- `ultron/user_memory.py` — `_MAX_PROMPT_CHARS=1200`
- Model: `config.yaml` → `gemma4:latest` on amvara8 Ollama

## High-level instructions for coder

- Add a small helper or test that builds a synthetic “fat” issue and asserts `len(format_issue_for_summary(...))` stays ≤ `max_total_chars`.
- Log or document estimated chars for: router system+memory, summary user prompt with memory (see existing `wf_info` prompt_chars).
- Optionally add config knobs under `config.example.yaml` (e.g. `llm.prompt_max_issue_chars`) **only if** wiring stays simple; otherwise keep constants but document them in OPERATIONS.
- Verify memory injection order does not duplicate huge blocks (orchestrator-style mistake — here single user file only).
- Suggest (in Implementation notes) whether router should use a **smaller** model from `llm_chain` model list for routing only — implement only if low-risk and tested.
- Patch bump if code/config changes.

## Acceptance criteria

- [x] Documented prompt size limits in `docs/OPERATIONS.md` (Gemma / local LLM section or new subsection)
- [x] Tests lock truncation invariants
- [x] `.venv/bin/pytest -q tests/test_textutil.py tests/test_user_memory.py` PASS
- [x] No increase of default ticket dump sizes without justification

## Implementation notes

- Named public constants in `ultron/textutil.py` (`ISSUE_SUMMARY_MAX_*`) and `MEMORY_PROMPT_MAX_CHARS` in `ultron/user_memory.py`; defaults unchanged (no dump-size increase; no YAML knobs — keep wiring simple).
- Tests: synthetic `_fat_issue` locks default total/per-field caps; `test_prompt_budget_ballpark_chars` asserts router+memory and single memory prefix on summary user prompt; `test_format_for_prompt_default_budget` locks memory injection ≤ 1200.
- Docs: new **Gemma / local LLM prompt budgets** section in `docs/OPERATIONS.md` with table + measured ballparks (~3.3k router system, ~4.5k with mem, ~9.3k summary user with fat ticket).
- **Router smaller model:** optional future win (routing is short JSON) via `llm_chain` model list / `model_override` — **not implemented** here; gemma4 remains fine if latency is acceptable. Low-risk only after an explicit slash/NL provider test matrix.
- Version **3.0.5 → 3.0.6**.

## Testing instructions

Automated:

```bash
.venv/bin/pip install -q -e .
.venv/bin/pytest -q tests/test_textutil.py tests/test_user_memory.py
```

Expect: all tests in those files PASS (25 at implement time), including fat-ticket total cap and memory default budget.

Optional full suite:

```bash
.venv/bin/pytest -q
```

Manual / operator:

1. Open `docs/OPERATIONS.md` → section **Gemma / local LLM prompt budgets**; confirm table matches code constants.
2. On a host with LLM logging: run `/summary` on a large ticket and grep logs for `prompt_chars=` on the summarize `FETCH` step — should stay near ≤ ~9.5k user chars with memory.
