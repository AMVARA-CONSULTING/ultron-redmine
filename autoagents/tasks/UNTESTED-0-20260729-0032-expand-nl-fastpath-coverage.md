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

- [x] New positive + negative cases in `tests/test_nl_fastpath.py`
- [x] `.venv/bin/pytest -q tests/test_nl_fastpath.py tests/test_nl_router.py tests/test_amvara_prefilter.py` PASS
- [x] No regression: compound/Amvara-only paths still take precedence when `_handle_nl_chat_message` routes by prefilter **before** redmine router (do not move fast-path earlier without re-checking)

## Implementation notes

- Expanded summary polite prefixes (EN/ES: can you / me puedes / hazme / quiero …) and Spanish memory show (`muéstrame la memoria`, `ver memoria`).
- **False-positive guards:** nostalgia (`remember when` / `recuerda cuando` / `te acuerdas cuando`) returns `None`; loose summary+issue path skipped when negation (`not`/`no`/`ignore`/…) is present.
- Reply-context strip extracted to `_strip_reply_context` (keeps user half after `\n\n---\n\n`).
- Call order unchanged: prefilter AMVARA_ONLY/COMPOUND still returns before `_run_nl_redmine_router` / `try_nl_fastpath`.
- Documented `nl_fastpath` log grep in `docs/OPERATIONS.md`. Version **3.0.2**.

## Testing instructions

1. Install and run unit tests:

```bash
.venv/bin/pip install -q -e .
.venv/bin/pytest -q tests/test_nl_fastpath.py tests/test_nl_router.py tests/test_amvara_prefilter.py
```

Expect: all PASS (30+ in `test_nl_fastpath` alone after this change).

2. Optional quick probes (no Discord):

```bash
.venv/bin/python -c "
from ultron.nl_fastpath import try_nl_fastpath
assert try_nl_fastpath('remember when we shipped') is None
assert try_nl_fastpath('muéstrame la memoria') is not None
assert try_nl_fastpath('can you summarize #99 please').args['issue_id'] == 99
print('ok')
"
```

3. Manual Discord (whitelist user, after dump/restart to **3.0.2+**):

- `@Ultron summarize #N` / `@Ultron me puedes resumir #N` → summary without long LLM routing delay; logs contain `nl_fastpath`.
- `@Ultron remember when we fixed prod` → should **not** write memory (LLM path / no `/memory` new nostalgia key).
- `@Ultron muéstrame la memoria` → memory list.
- Compound: mention Amvara host + ticket in one message → still Amvara/compound path (not a bare summary fast-path).
