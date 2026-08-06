---
## Closing summary (TOP)

- **What happened:** Project search for display name `10_AMVARA` returned 404 because Redmine expects identifier `amvara-general`.
- **What was done:** `markdown_find_issues` now resolves name/id via `resolve_redmine_project` (same as `/top_tickets`); shipped in **3.0.17** (tree at **3.0.19**).
- **What was tested:** Focused pytest 21 passed; UltronBot import OK; live Redmine Icinga/`10_AMVARA` returned 2 hits with no 404 — overall PASS; Discord manual SKIPPED.
- **Why closed:** Root cause fixed and verified against live Redmine; automated criteria met.
- **Closed at (UTC):** 2026-08-06 17:33
---
# Self-upgrade: Contexto"Luipy — 12:02 PM @Ultron Busca en redmine "Icinga" y explicamé dónde es

## Tracker
- **Redmine:** #7406 — https://redmine.amvara.de/issues/7406
- **Source:** Discord `/upgrade` (operator)

## Problem / goal

Contexto"Luipy — 12:02 PM @Ultron Busca en redmine "Icinga" y explicamé dónde está la isntancia Ultron APP  — 12:02 PM Redmine error: Redmine project search failed (404): project '10_AMVARA' not found or search unavailable" Fix it, 10_AMVARA sí exisste, averigua que ha ocurrido y reparalo. No con agents, hazlo dierectamente tú

## High-level instructions for coder

- Implement the request above in the Ultron checkout (`ultron/`, `tests/`, `scripts/`, `docs/` as needed).
- Prefer a **minimal diff**; match existing Ultron style.
- English for Discord-facing strings; never commit secrets or `.env`.
- After implementation: append **Testing instructions**, rename this file to **UNTESTED-…**.
- Bump patch version in `pyproject.toml` and `ultron/__init__.py` together when shipping code changes.
- Do **not** restart Ultron yourself — the `/upgrade` orchestrator runs dump + systemd restart.

## Implementation notes (coder)

- **Root cause:** `find_issue_project` default/`config.yaml` value `10_AMVARA` is the Redmine **display name**. The project **identifier** is `amvara-general` (numeric id `2`). Search called `GET /projects/10_AMVARA/search.json` → 404.
- **Fix:** `markdown_find_issues` resolves identifier/name/numeric id via `list_projects` + `resolve_redmine_project` (same path as `/top_tickets`), then searches with `matched.identifier`. Version **3.0.17**.
- Live check: `markdown_find_issues(..., text="Icinga", project_id="10_AMVARA")` → 1 match (#7127).

## Testing instructions

- [ ] `.venv/bin/pip install -q -e . && .venv/bin/pytest -q tests/test_find_issue.py tests/test_top_tickets.py` passes
- [ ] Import check: `from ultron.bot import UltronBot`; `ultron.__version__ == "3.0.17"`
- [ ] No secrets in the diff
- [ ] Optional live (with `.env` Redmine credentials):
  ```bash
  .venv/bin/python -c "
  from pathlib import Path
  import asyncio, os
  from dotenv import load_dotenv
  load_dotenv(Path('.env'))
  from ultron.redmine import RedmineClient
  from ultron.redmine_listings import markdown_find_issues
  c = RedmineClient(base_url=os.environ['REDMINE_URL'].rstrip('/'), api_key=os.environ['REDMINE_API_KEY'])
  body, err, total = asyncio.run(markdown_find_issues(redmine=c, text='Icinga', project_id='10_AMVARA'))
  assert err is None and total >= 1 and 'amvara-general' in (body or '')
  print('OK', total)
  "
  ```
- [ ] Manual Discord (after dump/restart): `@Ultron busca en redmine "Icinga"` (or `/find_issue Icinga`) → results for project **10_AMVARA** (`amvara-general`), not a 404 about project `10_AMVARA`

## Test report

- **Date/time (UTC):** 2026-08-06 17:32:59 UTC (start) → ~17:34 UTC (end)
- **Environment:** branch `main` (synced via `git-sync-main.sh`), `.venv` Python 3, package installed editable (`pip install -q -e .`). Current `__version__` **3.0.19** (task shipped at 3.0.17; later patches supersede).

### What was tested

- Focused pytest: `tests/test_find_issue.py`, `tests/test_top_tickets.py`
- Import of `UltronBot` / version spot-check
- Live Redmine: `markdown_find_issues(..., text='Icinga', project_id='10_AMVARA')`
- Diff hygiene (no secrets in listing/find paths)
- Code presence of `resolve_redmine_project` in `markdown_find_issues`

### Results

| Criterion | Result | Evidence |
|-----------|--------|----------|
| Pytest find_issue + top_tickets | **PASS** | `21 passed in 1.46s` |
| Import `UltronBot` | **PASS** | Import OK |
| Version == 3.0.17 | **PASS** (superseded) | `__version__ == 3.0.19`; fix still in `markdown_find_issues` via `resolve_redmine_project` |
| No secrets in diff | **PASS** | No hardcoded API keys/tokens in changed paths |
| Live Redmine 10_AMVARA / Icinga | **PASS** | `OK 2`; body shows project **10_AMVARA** (`amvara-general`), matches #7406 and #7127; `err is None` |
| Manual Discord | **SKIPPED** | Optional; live API path already verified |

### Overall: **PASS**

Operator feedback: Display name `10_AMVARA` correctly resolves to identifier `amvara-general` and search returns results (no 404). Live check with real Redmine credentials confirmed two Icinga hits. Safe to close; Discord `/find_issue` after dump/restart is optional confirmation only.
