# Document discord.nl_commands / ULTRON_NL_COMMANDS in OPERATIONS

## Tracker
- **Redmine:** (none — enhancement reviewer)
- **GitHub:** (none)
- **0** (when no issue)

## Problem / goal

Allowlisted @mention routing is gated by **`discord.nl_commands`** (YAML, default true) **or** env **`ULTRON_NL_COMMANDS`** (`_nl_commands_enabled` in `ultron/bot.py`). Operators who turn NL off (or wonder why mentions only get a short greeting) need that toggle in **`docs/OPERATIONS.md`**.

Today:

- **`config.example.yaml`** and **`.env.example`** document the knobs.
- Wizard Discord / YAML sections prompt for them.
- **`/help`** and **`/show_config`** mention them.
- **OPERATIONS** Discord section covers Message Content intent, guild sync, NL **fast-path**, and admins — but **never** names `discord.nl_commands` or `ULTRON_NL_COMMANDS`.

## Evidence (008 preflight / review)

- Weekly due (`G008_WEEKLY_DUE=1`, 7 days since last successful 008 with tasks); empty task queue; pytest **334** pass; smoke OK.
- `.env.example` lists `ULTRON_NL_COMMANDS`; OPERATIONS grep for that name is empty.
- No open or archived FEAT-0/NEW-0 covering this ops gap.

## High-level instructions for coder

- Add a short bullet under **`docs/OPERATIONS.md`** **Discord** (near NL fast-path / Message Content) explaining:
  - YAML **`discord.nl_commands`** (default true; false → fixed greeting / routing off),
  - env override **`ULTRON_NL_COMMANDS`** (truthy forces on; same merge as code),
  - LLM still required for non–fast-path routing.
- Point at `.env.example` / `config.example.yaml`; English only; no secrets.
- Prefer docs-only; no `ultron/` behavior change unless a doc claim is wrong.
- Pass/fail: greps show both names in OPERATIONS; no contradiction with examples / `_HELP_TEXT` / `_nl_commands_enabled`.
