---
## Closing summary (TOP)

- **What happened:** Operator asked Ultron to always reply in English regardless of user language or memory prefs.
- **What was done:** Forced English in NL router, summary/ask/note systems, and ollama-advisor; USER_GUIDE + `/help` note; shipped from **3.0.16** (still present at **3.0.20**).
- **What was tested:** Focused pytest 20 passed including `test_llm_prompts_always_english`; prompt wording and docs checks PASS; live Discord Spanish smoke SKIP.
- **Why closed:** Automated criteria passed; English-forcing is in place across LLM paths and docs.
- **Closed at (UTC):** 2026-08-06 17:42
---
# Self-upgrade: Ultron ALWAYS replay in English no matter what

## Tracker
- **Redmine:** #7406 — https://redmine.amvara.de/issues/7406
- **Source:** Discord `/upgrade` (operator)

## Problem / goal

Ultron ALWAYS replay in English no matter what

## High-level instructions for coder

- Implement the request above in the Ultron checkout (`ultron/`, `tests/`, `scripts/`, `docs/` as needed).
- Prefer a **minimal diff**; match existing Ultron style.
- English for Discord-facing strings; never commit secrets or `.env`.
- After implementation: append **Testing instructions**, rename this file to **UNTESTED-…**.
- Bump patch version in `pyproject.toml` and `ultron/__init__.py` together when shipping code changes.
- Do **not** restart Ultron yourself — the `/upgrade` orchestrator runs dump + systemd restart.

## Implementation notes (010)

- Version **3.0.16**.
- Forced English in `NL_ROUTER_SYSTEM` (chat + ignore language memory prefs), `SUMMARY_SYSTEM`, `ASK_ABOUT_ISSUE_SYSTEM`, `NOTE_SYSTEM`, and `ultron/prompts/ollama-advisor.md`.
- USER_GUIDE + `/help` remember line note that replies stay English.
- Redmine #7406 journal note posted summarizing the change.

## Testing instructions

- [ ] `.venv/bin/pip install -q -e .`
- [ ] `.venv/bin/pytest -q tests/test_textutil.py tests/test_nl_router.py` — expect PASS including `test_llm_prompts_always_english`
- [ ] Import check: `.venv/bin/python -c "from ultron.bot import UltronBot; from ultron import __version__; assert __version__ == '3.0.16'"`
- [ ] Confirm prompts: `SUMMARY_SYSTEM` / `NL_ROUTER_SYSTEM` contain “Always reply in English” / “in English” and do **not** say “user's language” / “Same language as the ticket”
- [ ] Optional live Discord (after dump/restart): @mention Ultron in Spanish asking a short question → chat reply in English; `/summary` on a Spanish ticket → English summary; `/ol` in Spanish → English answer
- [ ] No secrets in the diff

## Test report

- **When:** 2026-08-06 17:41:54 UTC (start) → 2026-08-06 17:43 UTC
- **Environment:** branch `main` @ `89ebbfa` (+ local uncommitted 3.0.20 doc bump unrelated); `.venv` Python 3.13.5

### What was tested

Forced-English LLM prompts (`SUMMARY_SYSTEM`, `ASK_ABOUT_ISSUE_SYSTEM`, `NOTE_SYSTEM`, `NL_ROUTER_SYSTEM`, ollama-advisor), pytest coverage (`test_llm_prompts_always_english` + nl_router suite), USER_GUIDE / `/help` English notes, import of `UltronBot`. Live Discord Spanish→English not exercised.

### Results

| Criterion | Result | Evidence |
|-----------|--------|----------|
| `pip install -e .` + focused pytest | **PASS** | `tests/test_textutil.py` + `tests/test_nl_router.py` → **20 passed**; `test_llm_prompts_always_english` **PASS** |
| Import / version spot-check | **PASS** | `from ultron.bot import UltronBot` OK; `__version__` is **3.0.20** (task noted 3.0.16; feature landed in `89ebbfa` / 3.0.19 and remains present) |
| Prompts force English; no match-user-language wording | **PASS** | `SUMMARY_SYSTEM` / `ASK_ABOUT_ISSUE_SYSTEM` / `NL_ROUTER_SYSTEM` contain “Always reply in English”; `NOTE_SYSTEM` “Always write the note in English, regardless of the user's language”; no “Same language as the ticket” |
| USER_GUIDE / `/help` English note | **PASS** | USER_GUIDE: “LLM replies always stay in English”; `_HELP_TEXT` remember line: “Replies stay English.” |
| Optional live Discord | **SKIP** | Not run (no dump/restart in this tester step) |
| No secrets in diff | **PASS** | English-related paths in `89ebbfa` are prompts/docs/tests only; no `.env`/tokens |

### Overall: **PASS**

Operator feedback: English-forcing is in place across summary/ask/note/NL router and docs. Version pin in the testing checklist was stale (3.0.16 vs current 3.0.20) but behavior matches the goal. Optional live Spanish Discord smoke still worth a quick check after next dump/restart.
