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
