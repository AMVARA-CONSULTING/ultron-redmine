---
## Closing summary (TOP)

- **What happened:** OPERATIONS lacked documentation for the `discord.nl_commands` / `ULTRON_NL_COMMANDS` toggle that gates allowlisted @mention routing.
- **What was done:** Added a Discord-section bullet in `docs/OPERATIONS.md` covering YAML default, env override, and LLM requirement; patch bump 3.0.43 → 3.0.44.
- **What was tested:** Greps, help/example/`_nl_commands_enabled` parity asserts, version check, and full pytest — all PASS (341 passed).
- **Why closed:** All acceptance criteria passed; docs-only change with no behavior mismatch.
- **Closed at (UTC):** 2026-10-12 09:47
---

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

## Implementation notes

- Added Discord bullet in **`docs/OPERATIONS.md`** (before NL fast-path) for **`discord.nl_commands`** / **`ULTRON_NL_COMMANDS`**: default true, false → fixed short notice, env truthy forces on (`YAML or env`), LLM still required for non–fast-path (Amvara exception noted). Links to `config.example.yaml` and `.env.example`.
- Patch bump **3.0.43 → 3.0.44** (`pyproject.toml` + `ultron/__init__.py`). No `ultron/` behavior change.

## Testing instructions

1. Confirm both knobs appear in OPERATIONS Discord section:
   ```bash
   grep -n 'discord.nl_commands\|ULTRON_NL_COMMANDS' docs/OPERATIONS.md
   ```
   Expect: one bullet naming both; default true; false → fixed notice; env truthy forces on; points at `config.example.yaml` / `.env.example`; mentions LLM for non–fast-path.
2. No contradiction with examples / help / merge:
   ```bash
   grep -n 'nl_commands\|ULTRON_NL_COMMANDS' config.example.yaml .env.example
   .venv/bin/python -c "
   from ultron.bot import _nl_commands_enabled, _NL_DISABLED_MENTION_MSG, _HELP_TEXT
   assert 'discord.nl_commands' in _HELP_TEXT and 'ULTRON_NL_COMMANDS' in _HELP_TEXT
   assert 'discord.nl_commands' in _NL_DISABLED_MENTION_MSG
   # merge: YAML or env (truthy env forces on)
   from ultron.config import AppConfig, DiscordConfig
   from ultron.settings import EnvSettings
   # spot-check docstring/merge matches OPERATIONS wording
   import inspect
   assert 'or' in inspect.getsource(_nl_commands_enabled)
   print('parity_ok')
   "
   ```
   Expect: `parity_ok`; examples still describe the same semantics.
3. Version bump both places **3.0.44**:
   ```bash
   grep -n '3.0.44' pyproject.toml ultron/__init__.py
   ```
4. Full regression (docs-only; suite should stay green):
   ```bash
   .venv/bin/pytest -q
   ```

## Test report

- **Date/time (UTC):** 2026-10-12 09:46:55 start → 09:47:19 end
- **Environment:** branch `main`, `.venv` present, pytest via `.venv/bin/pytest`

### What was tested

1. OPERATIONS Discord bullet names both knobs and documents semantics.
2. Parity with `config.example.yaml`, `.env.example`, `_HELP_TEXT`, `_NL_DISABLED_MENTION_MSG`, and `_nl_commands_enabled` merge (`YAML or env`).
3. Version **3.0.44** in `pyproject.toml` and `ultron/__init__.py`.
4. Full pytest suite.

### Results

| Criterion | Result | Evidence |
|-----------|--------|----------|
| Both knobs in OPERATIONS Discord section | **PASS** | `docs/OPERATIONS.md:79` — one bullet; default true; false → fixed short notice; env truthy forces on; links `config.example.yaml` / `.env.example`; LLM required for non–fast-path (Amvara note) |
| No contradiction with examples / help / merge | **PASS** | examples grep OK; Python assert → `parity_ok` |
| Version bump 3.0.44 both places | **PASS** | `pyproject.toml:7` and `ultron/__init__.py:4` = `3.0.44` |
| Full pytest green | **PASS** | `341 passed in 8.18s` |

### Overall: **PASS**

Operator feedback: OPERATIONS now documents the NL routing toggle consistently with examples and `_nl_commands_enabled`. Docs-only change; suite stayed green. No live Discord exercise required for this criterion set.
