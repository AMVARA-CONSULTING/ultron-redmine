---
## Closing summary (TOP)

- **What happened:** Offline smoke lacked coverage for `/new_ticket` project default resolve and autocomplete leading-number sort.
- **What was done:** Added in-memory smoke asserts for `resolve_redmine_project_query` / `project_autocomplete_choices`, updated `tests/test_smoke_check.py` and OPERATIONS expect list; version 3.0.25.
- **What was tested:** Offline smoke OK line, focused + full pytest (282 passed), docs grep, version pin — Overall PASS.
- **Why closed:** All criteria passed; no product-code follow-up needed.
- **Closed at (UTC):** 2026-08-13 17:35
---

# Offline smoke: new_ticket project default + autocomplete sort

## Tracker
- **Redmine:** (none — enhancement reviewer)
- **GitHub:** (none)
- **0** (when no issue)

## Problem / goal

After Ultron **3.0.22–3.0.23**, project defaulting and autocomplete ordering are core Discord UX for **`/new_ticket`**, but **`scripts/smoke_check.py`** has no offline assert for them (unlike version, Watching presence, user_memory, nl_fastpath, write_confirm). A dump/restart host can pass smoke while prefix resolve or leading-number sort regresses.

## Evidence (008 preflight / review)

- Weekly 008 review; pytest **282 passed**, live smoke OK — no offline line for project helpers.
- Logic lives in **`ultron/redmine_listings.py`**: `resolve_redmine_project_query`, `project_autocomplete_choices`, `_project_leading_number`; unit coverage in **`tests/test_new_ticket.py`** / **`tests/test_top_tickets.py`**, but smoke does not call them.
- Prior pattern: CLOSED watching-presence / write_confirm smoke tasks.

## High-level instructions for coder

- Extend **`scripts/smoke_check.py`** offline checks with a small in-memory project list (no network), e.g.:
  - **`resolve_redmine_project_query("05_", …)`** (or **`create_new_ticket`** with empty query + `default_project_query="05_"` and mocked client) selects the **05_**-named project.
  - **`project_autocomplete_choices`** without prefer-prefix orders by leading number (**05_** before **10_** before **93_**); with prefer **`05_`** that match stays first.
- Print a clear **`OK …`** line (name it consistently with existing smoke lines).
- Update **`tests/test_smoke_check.py`** if present so the offline path expects the new OK line.
- Optionally one sentence in **`docs/OPERATIONS.md`** health-check expect list.
- Pass/fail: `python scripts/smoke_check.py` shows the new OK without credentials; focused pytest green; no Discord required.

## Testing instructions

1. **Offline smoke**
   ```bash
   .venv/bin/python scripts/smoke_check.py
   ```
   Expect a line: `OK new_ticket_project: 05_ resolve + autocomplete sort` (along with existing OK version / watching_presence / user_memory / nl_fastpath / write_confirm). No Discord required for that line.

2. **Focused + full pytest**
   ```bash
   .venv/bin/pip install -q -e .
   .venv/bin/pytest -q tests/test_smoke_check.py
   .venv/bin/pytest -q
   ```
   Expect `test_check_ultron30_offline` asserts `OK new_ticket_project:`; full suite green.

3. **Docs expect list**
   ```bash
   grep -n 'new_ticket_project' docs/OPERATIONS.md scripts/smoke_check.py tests/test_smoke_check.py
   ```
   Expect OPERATIONS health-check expect list includes `OK new_ticket_project`.

4. **Version**
   ```bash
   .venv/bin/python -c "from ultron import __version__; import tomllib; from pathlib import Path; v=tomllib.loads(Path('pyproject.toml').read_text())['project']['version']; assert __version__==v=='3.0.25', (__version__, v); print('version_ok', v)"
   ```
   Expect both version strings **3.0.25**.

## Test report

- **Date/time (UTC):** 2026-08-13 17:34:40 start → 17:35:00 end
- **Environment:** branch `main` (synced), `.venv`, Ultron **3.0.25**

### What was tested

Offline smoke `OK new_ticket_project` line; focused + full pytest; OPERATIONS expect-list grep; version **3.0.25** pin.

### Results

1. **Offline smoke** — **PASS**
   - `.venv/bin/python scripts/smoke_check.py` printed `OK new_ticket_project: 05_ resolve + autocomplete sort` with existing OK version / watching_presence / user_memory / nl_fastpath / write_confirm (Redmine/LLM also OK on this host).

2. **Focused + full pytest** — **PASS**
   - `tests/test_smoke_check.py`: **6 passed**; asserts `OK new_ticket_project:`.
   - Full suite: **282 passed** in 7.94s.

3. **Docs expect list** — **PASS**
   - `grep new_ticket_project` hits OPERATIONS health-check expect list (line 201), `scripts/smoke_check.py`, and `tests/test_smoke_check.py`.

4. **Version** — **PASS** — `__version__` == `pyproject.toml` == **3.0.25**.

### Overall: **PASS**

Operator feedback: Offline smoke now covers project default resolve and autocomplete sort without Discord. Safe to dump/restart hosts with the new OK line in the health-check expect list. No product-code follow-up needed from this tester pass.
