---
## Closing summary (TOP)

- **What happened:** Enhancement task to align `.env.example` and USER_GUIDE bot-admin command lists with OPERATIONS / `/help`.
- **What was done:** Updated `DISCORD_ADMIN_IDS` comment and USER_GUIDE “Bot admins” bullet to list `/approve`, `/remove`, `/show_config`, `/pi`, `/upgrade`; patch bumped to 3.0.35.
- **What was tested:** Docs/env greps vs OPERATIONS/`_HELP_TEXT`, and `.venv/bin/pytest -q` (293 passed); overall PASS.
- **Why closed:** All acceptance criteria and the test report passed.
- **Closed at (UTC):** 2026-09-14 09:27
---

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

## Implementation notes

- `.env.example` `DISCORD_ADMIN_IDS` comment and USER_GUIDE “Bot admins” bullet now list all five commands in OPERATIONS order: `/approve`, `/remove`, `/show_config`, `/pi`, `/upgrade`.
- README admin row already complete; left unchanged.
- Patch version bumped to **3.0.35**.

## Testing instructions

1. Confirm `.env.example` `DISCORD_ADMIN_IDS` comment names **`/approve`**, **`/remove`**, **`/show_config`**, **`/pi`**, and **`/upgrade`**.
2. Confirm `docs/USER_GUIDE.md` “Bot admins” bullet names the same five commands.
3. Spot-check against `docs/OPERATIONS.md` `DISCORD_ADMIN_IDS` bullet and `ultron/bot.py` `_HELP_TEXT` “Bot admins only” section — no missing admin commands in the two updated files.
4. Optional: `.venv/bin/pytest -q` (docs-only change; suite should still pass).

## Test report

- **Date/time (UTC):** 2026-09-14 09:26 UTC
- **Environment:** branch `main`, `.venv`, version **3.0.35**
- **Start:** 2026-09-14 09:26:02 UTC

### What was tested

Docs/env parity for bot-admin slash commands per Testing instructions (no Discord manual exercise required).

### Results

1. **`.env.example` `DISCORD_ADMIN_IDS` comment** — **PASS**. L112 lists `/approve`, `/remove`, `/show_config`, `/pi`, and `/upgrade`.
2. **`docs/USER_GUIDE.md` “Bot admins” bullet** — **PASS**. Whitelist vs bot admins section names the same five commands.
3. **Spot-check vs OPERATIONS + `_HELP_TEXT`** — **PASS**. `docs/OPERATIONS.md` `DISCORD_ADMIN_IDS` bullet and `ultron/bot.py` `_HELP_TEXT` “Bot admins only” both cover `/approve`, `/remove`, `/show_config`, `/pi`, `/upgrade`; updated files have no missing admin commands.
4. **pytest** — **PASS**. `.venv/bin/pytest -q` → **293 passed** in 8.13s.

### Overall: **PASS**

Operator feedback: Env example and USER_GUIDE now match the admin matrix already documented in OPERATIONS and `/help`. Docs-only change; full suite green. Ready for closing reviewer archive.
