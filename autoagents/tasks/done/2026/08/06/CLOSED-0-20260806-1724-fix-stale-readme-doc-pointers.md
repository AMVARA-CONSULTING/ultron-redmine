---
## Closing summary (TOP)

- **What happened:** OPERATIONS still claimed README held the full env/slash tables; USER_GUIDE omitted `/top_tickets`.
- **What was done:** Retargeted OPERATIONS Related to `.env.example` / USER_GUIDE / `/help`; added `/top_tickets` and `/new_ticket` to USER_GUIDE first-commands; patch **3.0.20**.
- **What was tested:** Docs acceptance and stale-phrase scan PASS; pytest 278 passed; import_ok at **3.0.20**.
- **Why closed:** All criteria passed; stale README pointers fixed and `/top_tickets` discoverable in USER_GUIDE.
- **Closed at (UTC):** 2026-08-06 17:50
---
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

## Implementation notes (coder)

- `docs/OPERATIONS.md` Related: README is overview / quick start / short map / Docker; env → `.env.example`; slash → USER_GUIDE + `/help`.
- `docs/USER_GUIDE.md` First commands: added `/top_tickets` and `/new_ticket`; pointer text no longer implies README is the full env/slash reference.
- Patch bump **3.0.19 → 3.0.20** (`pyproject.toml` + `ultron/__init__.py`).

## Testing instructions

1. **Docs acceptance**
   - `docs/OPERATIONS.md` Related must **not** say README has a “full env table” or full slash-command reference.
   - Related should point at `.env.example`, USER_GUIDE / `/help`, and README for overview/Docker only.
   - `docs/USER_GUIDE.md` “First commands to try” table must include **`/top_tickets`** (and preferably **`/new_ticket`**).

2. **Stale-phrase scan**
   ```bash
   grep -RIn 'full env table\|README.md — full env' docs/ README.md || echo 'no_stale_claims'
   grep -n 'top_tickets' docs/USER_GUIDE.md
   ```
   Expect no stale “full env” README claims; at least one `top_tickets` hit in USER_GUIDE.

3. **Pytest + import**
   ```bash
   .venv/bin/pip install -q -e .
   .venv/bin/pytest -q
   .venv/bin/python -c "
   from dotenv import load_dotenv
   from pathlib import Path
   load_dotenv(Path('.') / '.env')
   from ultron.settings import load_env
   from ultron.bot import UltronBot
   load_env()
   print('import_ok')
   "
   ```
   Expect suite green and `import_ok`. Version strings in `pyproject.toml` and `ultron/__init__.py` both **3.0.20**.

## Test report

- **Date/time (UTC):** 2026-08-06 17:50:15 UTC
- **Environment:** branch `main`, `.venv`, `__version__` / `pyproject.toml` both **3.0.20**

### What was tested
Docs acceptance for OPERATIONS Related + USER_GUIDE first-commands, stale-phrase grep, full pytest, and bot import after `load_env()`.

### Results
1. Docs acceptance — **PASS** — OPERATIONS Related points README at overview/quick start/Docker; env → `.env.example`; slash → USER_GUIDE + `/help`. USER_GUIDE first-commands table includes `/top_tickets` and `/new_ticket`.
2. Stale-phrase scan — **PASS** — `no_stale_claims` for `full env table` / `README.md — full env`; `top_tickets` present in USER_GUIDE (line 28).
3. Pytest + import — **PASS** — `278 passed`; `import_ok` from settings + UltronBot; versions both **3.0.20**.

### Overall: **PASS**

Operator feedback: Stale README env/slash claims are gone; allowlisted users can discover `/top_tickets` from USER_GUIDE alone. Suite and import checks are green at 3.0.20.
