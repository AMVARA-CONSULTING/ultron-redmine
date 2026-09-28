# Document Redmine time-reporting knobs in OPERATIONS

## Tracker
- **Redmine:** (none — enhancement reviewer)
- **GitHub:** (none)
- **0** (when no issue)

## Problem / goal

Operators hit live Discord errors for **`/time_summary`** (login lookup) and **`/log_time`** (multiple time activities) that already name the fix knobs — but **`docs/OPERATIONS.md`** never documents them. Discovery today is only via **`config.example.yaml`**, **`.env.example`**, Discord error text, or the wizard.

Missing from the OPERATIONS **Redmine** section (which already covers project defaults):

1. **`redmine.user_id_by_login`** — login → numeric id map when API login search is forbidden.
2. **`redmine.time_summary_max_entries`** — pagination cap for spent-hours fetches (default 2000, clamped 50–5000).
3. **`REDMINE_TIME_ACTIVITY_ID`** — required when Redmine has several/no clear default time-entry activity for **`/log_time`**.

## Evidence (008 preflight / review)

- Weekly due (`G008_WEEKLY_DUE=1`, 7 days since last 008 review); empty task queue; pytest **315** pass; smoke OK.
- `docs/OPERATIONS.md` Redmine section: project defaults only — no `user_id_by_login` / `time_summary_max_entries` / `REDMINE_TIME_ACTIVITY_ID`.
- Code + examples already own the behavior: `ultron/config.py` (`RedmineConfig`), `ultron/redmine.py` (`resolve_user_id` / activity picker), `config.example.yaml`, `.env.example`, `_HELP_TEXT` `/time_summary` / `/log_time` lines.
- No open or archived FEAT-0/NEW-0 covering this ops gap.

## High-level instructions for coder

- Extend **`docs/OPERATIONS.md`** **Redmine** section (next to project defaults) with short bullets for **`user_id_by_login`**, **`time_summary_max_entries`**, and **`REDMINE_TIME_ACTIVITY_ID`** (env; point at `.env.example` / enumerations endpoint — English only, no secrets).
- Optional one-liner under Environment / Related docs if that keeps discoverability; do not duplicate the full wizard copy.
- Prefer docs-only; no `ultron/` behavior change unless a doc claim is wrong.
- Pass/fail: greps show the three knobs in OPERATIONS; no contradiction with `config.example.yaml` / `.env.example` / `_HELP_TEXT`.
