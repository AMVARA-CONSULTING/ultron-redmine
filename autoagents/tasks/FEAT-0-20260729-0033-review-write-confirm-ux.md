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

- [ ] Timeout and Cancel paths leave a clear user-visible message
- [ ] Other users cannot approve (interaction_check)
- [ ] Manual Discord checklist appended for operators (whitelist user: NL note cancel, slash log_time confirm, new_ticket cancel)
- [ ] `.venv/bin/pytest -q` relevant modules PASS
