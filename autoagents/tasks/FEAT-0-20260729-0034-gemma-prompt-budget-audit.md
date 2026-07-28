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

- [ ] Documented prompt size limits in `docs/OPERATIONS.md` (Gemma / local LLM section or new subsection)
- [ ] Tests lock truncation invariants
- [ ] `.venv/bin/pytest -q tests/test_textutil.py tests/test_user_memory.py` PASS
- [ ] No increase of default ticket dump sizes without justification
