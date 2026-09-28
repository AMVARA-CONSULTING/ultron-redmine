---
## Closing summary (TOP)

- **What happened:** Enhancement reviewer filed a docs gap: Redmine time-reporting knobs were missing from OPERATIONS despite live Discord errors naming them.
- **What was done:** Documented `user_id_by_login`, `time_summary_max_entries`, and `REDMINE_TIME_ACTIVITY_ID` in `docs/OPERATIONS.md` (plus env/YAML discoverability one-liners); patch **3.0.41**.
- **What was tested:** Docs acceptance and phrase scan passed; pytest 334 passed; import_ok; version sync OK.
- **Why closed:** All criteria passed; no Redmine/GitHub tracker item.
- **Closed at (UTC):** 2026-09-28 09:40
---

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

## Implementation notes (coder)

- Extended **`docs/OPERATIONS.md`** Redmine section with **Time reporting** bullets for **`user_id_by_login`**, **`time_summary_max_entries`**, and env **`REDMINE_TIME_ACTIVITY_ID`** (enumerations endpoint + `.env.example`).
- One-liners under **Environment validation** and **YAML validation** for discoverability; no `ultron/` behavior change.
- Patch version **3.0.40 → 3.0.41**.

## Testing instructions

1. **Docs acceptance**
   - `docs/OPERATIONS.md` **Redmine** section names **`user_id_by_login`**, **`time_summary_max_entries`**, and **`REDMINE_TIME_ACTIVITY_ID`**.
   - Bullets match behavior: login→id map when API search forbidden; max entries default **2000** clamped **50–5000**; activity id via env / `GET /enumerations/time_entry_activities.json`.
   - No contradiction with `config.example.yaml`, `.env.example`, or `_HELP_TEXT` (`/time_summary` / `/log_time`).

2. **Phrase scan**
   ```bash
   grep -n 'user_id_by_login\|time_summary_max_entries\|REDMINE_TIME_ACTIVITY_ID' docs/OPERATIONS.md
   grep -n 'user_id_by_login\|time_summary_max_entries' config.example.yaml
   grep -n 'REDMINE_TIME_ACTIVITY_ID' .env.example
   grep -n 'user_id_by_login\|REDMINE_TIME_ACTIVITY_ID' ultron/bot.py | head -10
   ```
   Expect all three knobs in OPERATIONS; YAML/env examples and help still describe the same knobs.

3. **Pytest + import + version**
   ```bash
   .venv/bin/pytest -q
   .venv/bin/python -c "
   from ultron.settings import load_env
   from ultron.bot import UltronBot
   load_env()
   print('import_ok')
   "
   grep -n 'version\|__version__' pyproject.toml ultron/__init__.py | head -5
   ```
   Expect pytest green, `import_ok`, and matching **3.0.41** in both version files.

## Test report

- **Date/time (UTC):** 2026-09-28 09:39:31 – 09:40:17 UTC
- **Environment:** branch `main` (synced), `.venv` Python, repo root `/root/Repos/ultron-redmine`

### What was tested

Docs acceptance for Redmine time-reporting knobs in `docs/OPERATIONS.md`; phrase scan vs `config.example.yaml` / `.env.example` / `_HELP_TEXT`; full pytest; bot import with `.env` loaded; version **3.0.41** sync.

### Results

| Criterion | Result | Evidence |
|-----------|--------|----------|
| OPERATIONS Redmine names all three knobs | **PASS** | Lines 70–73: `user_id_by_login`, `time_summary_max_entries`, `REDMINE_TIME_ACTIVITY_ID` under **Time reporting** |
| Behavior matches (403 map / 2000 clamp 50–5000 / enumerations) | **PASS** | Ops bullets match `config.example.yaml` (15–21), `.env.example` (40–42), and help lines in `ultron/bot.py` (393–394) |
| No contradiction with examples / `_HELP_TEXT` | **PASS** | Same knob names and semantics across OPERATIONS, YAML, env example, and `/time_summary` / `/log_time` help |
| Phrase scan (OPERATIONS + YAML + env + bot) | **PASS** | All three knobs in OPERATIONS; YAML/env examples present; bot help references `user_id_by_login` and `REDMINE_TIME_ACTIVITY_ID` |
| Pytest | **PASS** | `.venv/bin/pytest -q` → **334 passed** in 8.17s |
| Import + load_env | **PASS** | With `dotenv.load_dotenv('.env')` then `load_env()` → `import_ok` (bare shell lacked `DISCORD_TOKEN`) |
| Version 3.0.41 both files | **PASS** | `pyproject.toml` `version = "3.0.41"`; `ultron/__init__.py` `__version__ = "3.0.41"` |

### Overall: **PASS**

Operator feedback: Docs-only change is complete and consistent with examples and Discord help. No product-code fix needed; smoke Discord slash exercise was out of scope for this ops-doc task.
