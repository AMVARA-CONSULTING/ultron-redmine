---
## Closing summary (TOP)

- **What happened:** Review of Discord Confirm/Cancel UX for Redmine writes (`log_time` / `new_ticket`) after Ultron 3.0.
- **What was done:** Cleared Cancel/Timeout abort copy, author gate, double-submit/timeout settling, and subject on confirm; automated tests green on 3.0.13 (notes no longer require Confirm since 3.0.12).
- **What was tested:** `tests/test_write_confirm.py` — 8 passed; live Discord checklist SKIP in tester env.
- **Why closed:** All automated acceptance criteria passed; manual Discord left as operator follow-up.
- **Closed at (UTC):** 2026-07-29 19:39
---

# Review Redmine write Confirm/Cancel UX and failure modes

## Tracker
- **Redmine:** (none — Ultron 3.0 follow-up)
- **GitHub:** (none)
- **0**

## Problem / goal

Ultron **3.0.0** requires Discord **Confirm / Cancel** before mutating Redmine (`note`, `new_ticket`, `log_time`) via `ultron/write_confirm.py`, for both NL and slash. Review UX and edge cases: timeout messaging, ephemeral vs public, button clicks by other users, interaction expiry after LLM polish on `/note`, and double-submit.

## Context (shipped)

- `ultron/write_confirm.py` — `WriteConfirmView`, `ask_write_confirm`, `format_write_confirm_prompt`
- `UltronBot._confirm_redmine_write` / `_confirm_slash_redmine_write`
- NL: polish note with `skip_post=True` → confirm → `redmine.add_note`
- Slash note: same pattern via `original_response()` edit

## High-level instructions for coder

- After Cancel/Timeout, ensure status bubble / followup clearly says nothing was written (audit current strings).
- On `/note`, if confirm times out after a long LLM polish, user should not be stuck with stale buttons; view cleared on timeout (verify `on_timeout`).
- Consider showing issue subject (fetched) in confirm summary for `log_time` / `note` to catch wrong ids — keep summaries short for Discord limits.
- Add unit tests that do not need live Discord where possible (prompt formatting, view author check logic if extractable); document manual Discord checklist in **Testing instructions**.
- Do not remove confirms; only improve clarity/reliability.
- Patch bump if code changes.

## Acceptance criteria

- [x] Timeout and Cancel paths leave a clear user-visible message
- [x] Other users cannot approve (interaction_check)
- [x] Manual Discord checklist appended for operators (whitelist user: NL note cancel, slash log_time confirm, new_ticket cancel)
- [x] `.venv/bin/pytest -q` relevant modules PASS

## Implementation notes

- **v3.0.5** — clearer Cancel vs Timeout abort copy (`format_write_abort_message`); abort text applied on the confirm message (buttons cleared); double-submit ignored via `_settled`; `note`/`log_time` confirms include best-effort **Subject** (lightweight `get_issue(..., includes="")`); unit tests in `tests/test_write_confirm.py`.

## Testing instructions

### Automated

```bash
cd /path/to/ultron-redmine
.venv/bin/pip install -q -e .
.venv/bin/pytest -q tests/test_write_confirm.py
```

Expect **8 passed**.

### Manual Discord checklist (whitelist user)

1. **NL note cancel** — `@Ultron note #N: test cancel` (or equivalent routed note). After polish, press **Cancel**. Expect message **Cancelled — note was not posted. Nothing was written to Redmine.** and no new journal on the issue.
2. **Slash `/log_time` confirm** — `/log_time` on a safe test issue with tiny hours. Confirm summary should show **Subject** (if Redmine reachable). Press **Confirm** → time entry created. Repeat with **Cancel** → abort text, no new entry.
3. **Slash `/new_ticket` cancel** — start create with a disposable title; press **Cancel**. Expect abort on the confirm message; no new issue.
4. **Timeout** — start `/note` or `/log_time`, wait ~2 minutes without clicking. Expect **Timed out — … Nothing was written to Redmine.** and no active Confirm/Cancel buttons.
5. **Other user** — as a second Discord account, click **Confirm** on someone else’s prompt. Expect ephemeral “Only the person who requested this write can confirm it.” and no Redmine write.

## Test report

- **Date/time (UTC):** 2026-07-29 19:38–19:39 UTC
- **Environment:** branch `main` (synced via `./scripts/git-sync-main.sh`), `.venv`, package **3.0.13**

### What was tested

1. `.venv/bin/pytest -q tests/test_write_confirm.py` (expected 8 passed)
2. Static review of Cancel/Timeout abort copy, `interaction_check` / `_settled`, `on_timeout` button disable
3. Confirm wiring in `bot.py` for NL + slash `/log_time` and `/new_ticket` (subject heading on `log_time`)
4. Note path post-**3.0.12**: notes no longer use Confirm (checklist item 1 / `/note` timeout are stale vs current code)
5. Manual Discord guild checklist (interactive)

### Results

| Criterion | Result | Evidence |
|-----------|--------|----------|
| Timeout / Cancel clear user-visible message | **PASS** | `format_write_abort_message` unit test; abort applied in `ask_write_confirm` and `_confirm_slash_redmine_write`; callers use `no time logged` / `no ticket created` |
| Other users cannot approve | **PASS** | `author_may_confirm` + `WriteConfirmView.interaction_check` ephemeral deny; unit test `test_author_may_confirm_only_requester` |
| Double-submit / timeout clears view | **PASS** | `test_write_confirm_view_double_finish_ignored`; `on_timeout` sets TIMEOUT, disables buttons, `_settled` |
| Subject on `log_time` confirm | **PASS** | NL + slash use `format_issue_confirm_heading` + `_issue_subject_for_confirm` |
| Manual Discord checklist present | **PASS** | Appended in task; note-cancel steps obsolete after **3.0.12** (notes post without Confirm) — operator should use `/log_time` / `/new_ticket` for live checks |
| `.venv/bin/pytest -q tests/test_write_confirm.py` | **PASS** | `8 passed in 0.27s` |
| Manual Discord (live guild) | **SKIP** | No interactive Discord session in this tester environment |

### Overall: **PASS**

Operator feedback: Automated write-confirm coverage is green on **3.0.13**; Cancel/Timeout copy, author gate, and double-submit/timeout behavior match the acceptance bar for `/log_time` and `/new_ticket`. Live Discord remains an operator follow-up; treat the task’s NL note cancel steps as superseded by the no-Confirm-for-notes change.
