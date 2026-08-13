---
## Closing summary (TOP)

- **What happened:** Docs for Redmine project defaults (`find_issue_project` / `new_ticket_default_project`) were missing from OPERATIONS, RELEASE smoke, and USER_GUIDE `/find_issue`.
- **What was done:** Documented both keys and resolve rules in OPERATIONS; added omit-project `/new_ticket` smoke to OPERATIONS and RELEASE_CHECKLIST; aligned USER_GUIDE `/find_issue` with help defaults.
- **What was tested:** Docs acceptance + phrase scan + full pytest (282 passed); version coherent at 3.0.25 (task pin 3.0.24 superseded) — Overall PASS.
- **Why closed:** All acceptance criteria passed; docs-only, no product follow-up.
- **Closed at (UTC):** 2026-08-13 17:35
---

# Document Redmine project defaults (find_issue / new_ticket)

## Tracker
- **Redmine:** (none — enhancement reviewer)
- **GitHub:** (none)
- **0** (when no issue)

## Problem / goal

Ultron **3.0.22–3.0.23** made **`/new_ticket`** project optional (default prefix **`05_`** via **`redmine.new_ticket_default_project`**) and sorted autocomplete by leading project code. **`/help`**, **`config.example.yaml`**, the wizard, and the USER_GUIDE **`/new_ticket`** row already describe this. Operator docs do not:

- **`docs/OPERATIONS.md`** Redmine / YAML sections never mention **`redmine.find_issue_project`** (default **10_AMVARA**) or **`redmine.new_ticket_default_project`** (default **`05_`**), nor that resolution accepts **identifier, display name, or prefix** (important after the find_issue 404 when a display name was used as a path segment).
- **`docs/RELEASE_CHECKLIST.md`** / **Manual Discord smoke** still only exercise Confirm on **`/new_ticket`** with no check that omitting **project** lands on the **05_** default.
- **`docs/USER_GUIDE.md`** **`/find_issue`** row still says only “default Redmine project” while **`/new_ticket`** names **`05_`**.

Operators and release verifiers can miss the new knobs or ship without validating the default create path.

## Evidence (008 preflight / review)

- Weekly due (`G008_WEEKLY_DUE=1`); empty active task queue.
- Commits **b16051b** (3.0.22 optional project / `05_` default) and **d366191** (3.0.23 autocomplete sort).
- `config.example.yaml` + wizard expose both keys; OPERATIONS/RELEASE do not.
- USER_GUIDE line for **`/find_issue`** lacks the named default that **`/help`** already has (`redmine.find_issue_project`, **10_AMVARA**).

## High-level instructions for coder

- In **`docs/OPERATIONS.md`**, under Redmine and/or YAML validation, add a short note for:
  - **`redmine.find_issue_project`** — default search project; prefer identifier or a value that resolves via `list_projects` (name/id/prefix); empty → **10_AMVARA**.
  - **`redmine.new_ticket_default_project`** — used when **`/new_ticket`** omits project; identifier, name, or prefix (e.g. **`05_`** → **05_AMVARA_internal**); empty → **`05_`**.
  - Point at **`config.example.yaml`** / wizard; do not dump the full schema.
- Extend **Manual Discord smoke** (OPERATIONS) and **`docs/RELEASE_CHECKLIST.md`** section 4 with one line: **`/new_ticket`** with **project omitted** (or cleared) → Confirm preview targets the configured **05_**-style default, then Cancel (no write) or Confirm on a safe test.
- Align **`docs/USER_GUIDE.md`** **`/find_issue`** table row with **`/help`**: mention default project **10_AMVARA** / operator-configurable **`find_issue_project`** (keep user-facing tone).
- English only; no **`ultron/`** behavior changes required unless a doc cross-link is broken.
- Pass/fail: OPERATIONS names both keys + resolve hint; RELEASE/smoke mention optional-project default; USER_GUIDE **`/find_issue`** names the default; no contradiction with **`config.example.yaml`** / **`_HELP_TEXT`**.

## Testing instructions

1. **Docs acceptance**
   - `docs/OPERATIONS.md` **Redmine** section names **`find_issue_project`** and **`new_ticket_default_project`**, states empty defaults (**10_AMVARA** / **`05_`**), and notes identifier/name/prefix resolution (display-name-as-path 404 hint OK).
   - `docs/OPERATIONS.md` **YAML validation** points at those knobs / example YAML / wizard (no full schema dump).
   - `docs/OPERATIONS.md` **Manual Discord smoke** includes **`/new_ticket`** with project omitted → **05_**-style default preview, then Cancel or safe Confirm.
   - `docs/RELEASE_CHECKLIST.md` section 4 has the same optional-project default check.
   - `docs/USER_GUIDE.md` **`/find_issue`** row names **10_AMVARA** / **`find_issue_project`**.
   - No contradiction with `config.example.yaml` comments or Discord **`/help`** (`_HELP_TEXT`).

2. **Phrase scan**
   ```bash
   grep -n 'find_issue_project\|new_ticket_default_project' docs/OPERATIONS.md docs/RELEASE_CHECKLIST.md
   grep -n 'find_issue' docs/USER_GUIDE.md | head -5
   grep -n 'project omitted\|05_' docs/OPERATIONS.md docs/RELEASE_CHECKLIST.md
   ```
   Expect both config keys in OPERATIONS; RELEASE/smoke mention omit-project / **05_**; USER_GUIDE find_issue mentions **10_AMVARA**.

3. **Pytest + version**
   ```bash
   .venv/bin/pip install -q -e .
   .venv/bin/pytest -q
   .venv/bin/python -c "from ultron import __version__; import tomllib; from pathlib import Path; v=tomllib.loads(Path('pyproject.toml').read_text())['project']['version']; assert __version__==v=='3.0.24', (__version__, v); print('version_ok', v)"
   ```
   Expect suite green; both version strings **3.0.24**. Docs-only change — no Discord/Redmine behavior change required beyond checklist reading.

## Test report

- **Date/time (UTC):** 2026-08-13 17:33:59 start → 17:34:28 end
- **Environment:** branch `main` (synced), `.venv`, Ultron **3.0.25** (`__version__` == `pyproject.toml`)

### What was tested

Docs acceptance for OPERATIONS / RELEASE_CHECKLIST / USER_GUIDE Redmine project defaults; phrase scan; full pytest; version coherence vs task pin **3.0.24**.

### Results

1. **Docs acceptance** — **PASS**
   - OPERATIONS Redmine names both keys, empty defaults **10_AMVARA** / **`05_`**, identifier/name/prefix + display-name 404 hint (lines 65–67).
   - YAML validation points at knobs / example YAML / wizard (line 191).
   - Manual Discord smoke step 6: omit project → **05_**-style default, Cancel/safe Confirm (line 214).
   - RELEASE_CHECKLIST §4 same optional-project check (line 40).
   - USER_GUIDE `/find_issue` names **10_AMVARA** / `find_issue_project` (line 27).
   - Aligns with `config.example.yaml` and `_HELP_TEXT` in `ultron/bot.py`.

2. **Phrase scan** — **PASS**
   - `grep` found both config keys in OPERATIONS; RELEASE/smoke omit-project / **05_**; USER_GUIDE find_issue mentions **10_AMVARA**.

3. **Pytest** — **PASS** — `282 passed` in 7.58s.

4. **Version pin 3.0.24** — **PASS** (superseded)
   - Task expected **3.0.24**; tree is **3.0.25** / **3.0.25** (matched) after subsequent UNTESTED smoke-check work in the same working tree. Docs criteria unaffected.

### Overall: **PASS**

Operator feedback: Project-default docs are complete and consistent with config/help. No Discord live check required for this docs-only task. Proceed to archive via closing reviewer when ready; next tester queue item is the smoke-check UNTESTED sibling.
