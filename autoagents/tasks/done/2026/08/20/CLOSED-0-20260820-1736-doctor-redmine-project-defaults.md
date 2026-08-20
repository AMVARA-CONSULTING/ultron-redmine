---
## Closing summary (TOP)

- **What happened:** `ultron doctor` only pinged Redmine and did not show effective `find_issue_project` / `new_ticket_default_project` defaults operators need after 3.0.22+.
- **What was done:** Doctor now prints those resolved config values after Config OK; tests and OPERATIONS/RELEASE docs updated; version bumped to 3.0.27.
- **What was tested:** Doctor unit tests (10) and full suite (284) passed; live doctor and temp-config override showed the expected knobs with no secrets.
- **Why closed:** All acceptance criteria passed; operators can confirm project defaults from doctor alone.
- **Closed at (UTC):** 2026-08-20 17:41
---

# Doctor: show Redmine project default knobs

## Tracker
- **Redmine:** (none — enhancement reviewer)
- **GitHub:** (none)
- **0** (when no issue)

## Problem / goal

After Ultron **3.0.22+**, **`redmine.find_issue_project`** (default **10_AMVARA**) and **`redmine.new_ticket_default_project`** (default **`05_`**) matter for `/find_issue` and `/new_ticket`, and are documented in OPERATIONS / wizard / config.example. **`ultron doctor`** still only prints a Redmine API ping line — operators cannot confirm the effective project defaults without opening YAML. Add a short, non-secret doctor readout of the resolved values from the loaded config.

## Evidence (008 preflight / review)

- Weekly due; project-default docs/smoke closed 2026-08-13; doctor unchanged (`ultron/doctor.py` Redmine block = connection label only).
- Live `ultron doctor` on this host shows User memory + bindings + Redmine OK, no `find_issue_project` / `new_ticket_default_project`.
- Related closed tasks documented YAML/docs only (`CLOSED-0-20260813-1730-…`, `…-1731-…`).

## High-level instructions for coder

- After config loads successfully in **`ultron/doctor.py`**, print the effective **`app_cfg.redmine.find_issue_project`** and **`app_cfg.redmine.new_ticket_default_project`** (labels clear to operators; no secrets).
- Extend **`tests/test_doctor.py`** to assert both keys appear (defaults and/or overridden YAML).
- Optionally one sentence in **`docs/OPERATIONS.md`** / RELEASE doctor bullet that doctor surfaces these knobs — keep docs minimal.
- Pass: `ultron doctor` shows both values; focused doctor tests + full pytest green; bump patch version per repo rules when committing code.

## Implementation notes (coder)

- **`ultron/doctor.py`:** After `Config: OK`, prints effective `redmine.find_issue_project` and `redmine.new_ticket_default_project` (with short operator labels; no secrets).
- **`tests/test_doctor.py`:** Asserts built-in defaults (`10_AMVARA` / `05_`) and overridden YAML values.
- Docs: one-line updates in `docs/OPERATIONS.md` (Health checks) and `docs/RELEASE_CHECKLIST.md` doctor bullet.
- Version: **3.0.26 → 3.0.27** (`pyproject.toml` + `ultron/__init__.py`).

## Testing instructions

1. **Unit tests**
   ```bash
   .venv/bin/pip install -q -e .
   .venv/bin/pytest -q tests/test_doctor.py
   .venv/bin/pytest -q
   ```
   Expect: doctor tests (incl. default + overridden project knobs) pass; full suite green.

2. **Manual doctor smoke**
   ```bash
   ultron doctor
   # or: python -m ultron doctor
   ```
   After `Config: OK (read and parse)`, expect two lines naming:
   - `redmine.find_issue_project: '…'`
   - `redmine.new_ticket_default_project: '…'`
   Values should match loaded `config.yaml` (or built-in defaults when unset). No API keys in that output.

3. **Optional:** With a temp config that sets custom `find_issue_project` / `new_ticket_default_project`, run `CONFIG_PATH=… ultron doctor` and confirm the overridden values appear.


## Test report

- **Date/time (UTC):** 2026-08-20 17:40:13 start → 17:41:00 end
- **Environment:** branch `main`, `.venv` (`pip install -e .`, `ultron` / `pytest` under `.venv/bin`)

### What was tested

Doctor readout of effective `redmine.find_issue_project` / `redmine.new_ticket_default_project`; focused + full pytest; live `ultron doctor`; optional temp-config override.

### Results

1. **Unit tests — PASS.** `.venv/bin/pip install -q -e .`; `pytest -q tests/test_doctor.py` → **10 passed**; full `.venv/bin/pytest -q` → **284 passed** in 7.76s.
2. **Manual doctor smoke — PASS.** `ultron doctor` after `Config: OK (read and parse)` prints:
   - `redmine.find_issue_project: '10_AMVARA' (default for /find_issue)`
   - `redmine.new_ticket_default_project: '05_' (default when /new_ticket omits project)`
   No API keys in those lines (token/key env bindings remain masked).
3. **Optional override — PASS.** Temp `CONFIG_PATH` with `ZZ_FIND` / `ZZ_NEW` → doctor shows those values on the same two lines.

### Overall: **PASS**

Doctor now surfaces the project-default knobs operators need without opening YAML. Tests and live/override smoke agree with defaults and custom config.
