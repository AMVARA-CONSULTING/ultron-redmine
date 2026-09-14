# Admin command list parity (.env.example + USER_GUIDE)

## Tracker
- **Redmine:** (none — enhancement reviewer)
- **GitHub:** (none)
- **0** (when no issue)

## Problem / goal

Bot-admin slash surface is **`/approve`**, **`/remove`**, **`/show_config`**, **`/pi`**, **`/upgrade`** (`_HELP_TEXT`, OPERATIONS `DISCORD_ADMIN_IDS` bullet). Two operator/user-facing strings are incomplete:

1. **`.env.example`** — `DISCORD_ADMIN_IDS` comment lists only `/approve`, `/remove`, `/show_config`.
2. **`docs/USER_GUIDE.md`** — “Bot admins” bullet mentions only **`/approve`** and **`/remove`**.

Operators copying the env comment (or Discord users reading the guide) can miss that **`/pi`** and **`/upgrade`** are admin-gated.

## Evidence (008 preflight / review)

- Weekly due; `/help` and OPERATIONS already list all five admin commands.
- `.env.example` L112 and USER_GUIDE “Whitelist vs bot admins” lag that matrix.

## High-level instructions for coder

- Update **`.env.example`** `DISCORD_ADMIN_IDS` comment to include **`/pi`** and **`/upgrade`** alongside approve/remove/show_config (same order as OPERATIONS / `/help` if practical).
- Update **`docs/USER_GUIDE.md`** “Bot admins” bullet so admins may **`/approve`**, **`/remove`**, **`/show_config`**, **`/pi`**, and **`/upgrade`** (one short sentence; keep USER_GUIDE end-user tone — no deep ops detail).
- Optional: if README admin row already lists all five, leave it; do not expand USER_GUIDE into an ops manual.
- Pass/fail: those two files name all five admin commands; no contradiction with `_HELP_TEXT` / OPERATIONS.
