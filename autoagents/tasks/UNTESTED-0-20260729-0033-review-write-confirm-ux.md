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
