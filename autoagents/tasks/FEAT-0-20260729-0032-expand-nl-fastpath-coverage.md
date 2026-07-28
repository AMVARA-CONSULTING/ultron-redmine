# Expand NL fast-path coverage and Spanish/edge intents

## Tracker
- **Redmine:** (none — Ultron 3.0 follow-up)
- **GitHub:** (none)
- **0**

## Problem / goal

Ultron **3.0.0** introduced `ultron/nl_fastpath.py` so Gemma is not called for obvious intents (`summarize #N`, bare `#123`, `ping`/`help`, remember/forget/show memory). Coverage is thin: more Spanish phrases, reply-context separator handling, and **false-positive** guards are needed so ambiguous chat still falls through to the LLM router.

## Context (shipped)

- `ultron/nl_fastpath.py` → `try_nl_fastpath`
- Called from `UltronBot._run_nl_redmine_router` before `run_nl_router`
- Tests: `tests/test_nl_fastpath.py`

## High-level instructions for coder

- Inventory real Discord phrasings (ES/EN) for summary / ask / remember; add regexes only when **high confidence** (prefer miss → LLM over wrong command).
- Add negative tests: long prose with an incidental `#123`, poems, “remember when we…” (nostalgia, not memory write), compound Amvara+Redmine messages (fast-path must return `None` so prefilter/compound path keeps ownership — verify call order in `bot.py`).
- Confirm reply-context `---` stripping does not drop the user half incorrectly.
- Optional: log metric / structured log line already exists (`nl_fastpath`); document in OPERATIONS if operators need to grep it.
- Patch bump if code changes; pytest for `test_nl_fastpath` + `test_nl_router` + `test_amvara_prefilter`.

## Acceptance criteria

- [ ] New positive + negative cases in `tests/test_nl_fastpath.py`
- [ ] `.venv/bin/pytest -q tests/test_nl_fastpath.py tests/test_nl_router.py tests/test_amvara_prefilter.py` PASS
- [ ] No regression: compound/Amvara-only paths still take precedence when `_handle_nl_chat_message` routes by prefilter **before** redmine router (do not move fast-path earlier without re-checking)
