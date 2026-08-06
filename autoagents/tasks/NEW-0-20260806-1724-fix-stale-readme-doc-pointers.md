# Fix stale README pointers and USER_GUIDE /top_tickets gap

## Tracker
- **Redmine:** (none — enhancement reviewer)
- **GitHub:** (none)
- **0** (when no issue)

## Problem / goal

`docs/OPERATIONS.md` Related documentation still claims README has a **full env table** and **slash commands**. Since Ultron **2.0.28** the README is a short overview; env detail lives in `.env.example` / OPERATIONS, and the live command list is Discord **`/help`** plus USER_GUIDE. Separately, **`/top_tickets`** is in README and `_HELP_TEXT` but missing from the USER_GUIDE “First commands to try” table (unlike `/find_issue`), so Discord users reading only the guide may not discover it.

## Evidence (008 preflight / review)

- Weekly 008 scan; compared slash registration vs docs: `/top_tickets` → README only (not USER_GUIDE).
- `docs/OPERATIONS.md` line: “README.md — full env table, slash commands, Docker” — inaccurate after short README.
- Closed `CLOSED-0-20260729-0036-help-docs-parity-ultron-30` covered Ultron 3.0 help/docs broadly; this is a residual pointer + table gap, not a re-open of that task.

## High-level instructions for coder

- Update `docs/OPERATIONS.md` Related (and any similar “see README for full slash/env table” phrasing) to point at `.env.example`, USER_GUIDE / `/help`, and Docker notes as appropriate — do not restore a long README unless product owners ask.
- Add **`/top_tickets`** (and briefly **`/new_ticket`** if still only under Write confirmation) to USER_GUIDE first-commands or an adjacent short blurb so allowlisted users can find them without reading `_HELP_TEXT` source.
- Pass: no doc claims README is the full env/slash reference; USER_GUIDE mentions `/top_tickets`.
- Fail: OPERATIONS Related line unchanged and USER_GUIDE still omits `/top_tickets`.
