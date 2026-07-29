---
## Closing summary (TOP)

- **What happened:** Operators asked that adding a Redmine note (`/note` / NL note) should not require Discord Confirm/Cancel.
- **What was done:** Shipped **v3.0.12** so slash and NL note post immediately after LLM polish; Confirm kept for `/new_ticket` and `/log_time`; help/docs and Redmine #7406 updated.
- **What was tested:** Full pytest 273 passed; UltronBot import OK; smoke_check OK; help/code-path review PASS; live Discord manual SKIP (no guild) — overall PASS.
- **Why closed:** Automated criteria met; note no longer goes through Confirm in code/docs; interactive Discord left as operator follow-up after dump/restart.
- **Closed at (UTC):** 2026-07-29 19:22
---
# Self-upgrade: No necesitas confirmación para cuando se te solicite añadir una nota a redmine

## Tracker
- **Redmine:** #7406 — https://redmine.amvara.de/issues/7406
- **Source:** Discord `/upgrade` (operator)

## Problem / goal

No necesitas confirmación para cuando se te solicite añadir una nota a redmine

## High-level instructions for coder

- Implement the request above in the Ultron checkout (`ultron/`, `tests/`, `scripts/`, `docs/` as needed).
- Prefer a **minimal diff**; match existing Ultron style.
- English for Discord-facing strings; never commit secrets or `.env`.
- After implementation: append **Testing instructions**, rename this file to **UNTESTED-…**.
- Bump patch version in `pyproject.toml` and `ultron/__init__.py` together when shipping code changes.
- Do **not** restart Ultron yourself — the `/upgrade` orchestrator runs dump + systemd restart.

## Implementation notes (coder)

- **v3.0.12** — `/note` (slash) and NL `note` post immediately after LLM polish; removed Discord Confirm/Cancel for notes only.
- `/new_ticket` and `/log_time` still require Confirm.
- Updated `_HELP_TEXT`, README, USER_GUIDE, OPERATIONS, RELEASE_CHECKLIST, and `write_confirm` / `add_formatted_note` docs.
- Redmine journal note added on #7406.

## Testing instructions

- [x] `.venv/bin/pytest -q` passes (full suite green locally: 273 passed)
- [x] Import check: `from ultron.bot import UltronBot`
- [x] No secrets in the diff
- [x] Help parity: `_HELP_TEXT` says `/note` posts without Confirm; Confirm still listed for `/new_ticket` and `/log_time`
- [ ] Manual (after dump/restart): `/note` on a safe test issue → journal updated **without** Confirm/Cancel buttons; Discord reply still shows preview
- [ ] Manual: `@Ultron` NL “add a note to #N: …” → same (no Confirm)
- [ ] Manual regression: `/log_time` still shows Confirm / Cancel
- [x] Optional: `python scripts/smoke_check.py` (OK write_confirm still expected for remaining confirm paths)

## Test report

- **Date/time (UTC):** 2026-07-29 19:21–19:22 UTC
- **Environment:** branch `main` (synced via `./scripts/git-sync-main.sh`), `.venv`, package **3.0.12**

### What was tested

1. Full pytest suite
2. `from ultron.bot import UltronBot` import
3. Diff review for secrets; help-text and note/confirm code-path review
4. `scripts/smoke_check.py` (offline Ultron 3.0 + Redmine + LLM)
5. Manual Discord slash/NL (interactive guild)

### Results

| Criterion | Result | Evidence |
|-----------|--------|----------|
| `.venv/bin/pytest -q` | **PASS** | `273 passed, 35 warnings` in ~8s |
| Import `UltronBot` | **PASS** | import OK; `ultron.__version__ == "3.0.12"` |
| No secrets in diff | **PASS** | Diff is docs + `bot.py` / `workflows.py` / `write_confirm.py` / version bump only; no credential values |
| Help parity | **PASS** | `/note` line: “Posts immediately (no Confirm)”; writes blurb excludes `/note`; `/new_ticket` and `/log_time` still say Confirm |
| Code path: note posts without Confirm | **PASS** | NL + slash `/note` call `add_formatted_note` with no `skip_post` / no `_confirm_redmine_write`; `skip_post=True` absent from `bot.py` |
| Code path: `/log_time` / `/new_ticket` still Confirm | **PASS** | Both NL and slash handlers still gate on `ConfirmResult.APPROVE` |
| `smoke_check.py` | **PASS** | OK version 3.0.12; OK user_memory; OK nl_fastpath; OK write_confirm; OK Redmine 200; OK LLM gemma4:latest |
| Manual Discord `/note` / NL note / `/log_time` | **SKIP** | Tester has no interactive Discord guild session; dump/restart of **3.0.12** not yet applied. Static paths match the intended behavior. Operator: one live check after dump/restart. |

### Overall: **PASS**

Operator feedback: Automated suite and smoke are green on **3.0.12**; note no longer goes through Confirm in code or help/docs, while ticket create and time log still do. Interactive Discord confirmation remains an operator follow-up after dump/restart. Safe to close.
