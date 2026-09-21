---
## Closing summary (TOP)

- **What happened:** Docs drifted: README/USER_GUIDE listing commands and OPERATIONS host whitelist CLI were incomplete vs `/help`.
- **What was done:** Named `/list_new_issues`, `/issues_by_status`, `/list_unassigned_issues` in README and USER_GUIDE; added OPERATIONS Whitelist/approve (`/approve`, `ultron add token`, state/TTL); patch **3.0.36**.
- **What was tested:** Grep/table checks plus `.venv/bin/pytest -q` (293 passed); overall PASS.
- **Why closed:** All acceptance criteria and the test report passed.
- **Closed at (UTC):** 2026-09-21 09:14
---

# Docs: listing commands + host whitelist CLI parity

## Tracker
- **Redmine:** (none — enhancement reviewer)
- **GitHub:** (none)
- **0** (when no issue)

## Problem / goal

Operator/user docs drift from the live command matrix and from each other:

1. **`README.md` Commands** allowlisted row uses ``/list_*`` but never names **`/issues_by_status`** (not a `list_*` command), so newcomers miss a primary listing slash.
2. **`docs/USER_GUIDE.md`** “First commands” table includes **`/issues_by_status`** but omits **`/list_new_issues`** and **`/list_unassigned_issues`** (only mentioned in prose / whitelist bullets).
3. **`docs/USER_GUIDE.md`** tells users admins may use a **host command** and points at operator docs, but **`docs/OPERATIONS.md`** never documents **`ultron add token '…'`** (README already has a one-liner).

## Evidence (008 preflight / review)

- Weekly due; `G008_DOC_DRIFT=0` (version strings aligned) — manual scan found copy gaps.
- Live matrix: `_HELP_TEXT` in `ultron/bot.py` lists all three listing commands; README `Commands` table does not name `issues_by_status`.
- No open/archived FEAT-0/NEW-0 already covering this exact parity trio (last related: admin-commands env/USER_GUIDE parity, 2026-09-14).

## High-level instructions for coder

- Update **`README.md`** Commands allowlisted cell to name **`/issues_by_status`** (keep `/list_*` or expand to `/list_new_issues` / `/list_unassigned_issues` if clearer).
- Update **`docs/USER_GUIDE.md`** first-commands table with short rows for **`/list_new_issues`** and **`/list_unassigned_issues`** (age/limit from config — mirror `/help` tone).
- Add a short **whitelist / approve** subsection (or bullet under Discord/env) in **`docs/OPERATIONS.md`**: Discord **`/approve`**, host **`ultron add token '<token>'`** (`ultron/cli.py`), state files under **`ULTRON_STATE_DIR`**, TTL note if useful — English only; no secrets.
- Do not change `ultron/` behavior unless a doc claim is wrong; prefer docs-only.
- Pass/fail: greps show `issues_by_status` in README; both list commands in USER_GUIDE table area; `ultron add token` in OPERATIONS; English-only.

## Implementation notes

- `README.md` allowlisted listings cell now names `/list_new_issues`, `/issues_by_status`, `/list_unassigned_issues` (plus existing find/top/new_ticket).
- `docs/USER_GUIDE.md` first-commands table gained rows for `/list_new_issues` and `/list_unassigned_issues`.
- `docs/OPERATIONS.md` Discord section: new **Whitelist / approve** subsection (`/approve`, `ultron add token`, state files, 300s TTL).
- Patch version **3.0.36** (docs + version sync). No `ultron/` behavior change.

## Testing instructions

1. Confirm `README.md` Commands allowlisted cell includes **`/issues_by_status`** (and preferably `/list_new_issues` / `/list_unassigned_issues`).
2. Confirm `docs/USER_GUIDE.md` “First commands to try” table has rows for **`/list_new_issues`** and **`/list_unassigned_issues`** (age/limit wording OK).
3. Confirm `docs/OPERATIONS.md` documents **`ultron add token`** and Discord **`/approve`**, with `ULTRON_STATE_DIR` / pending TTL note — English only, no secrets.
4. Optional: `.venv/bin/pytest -q` (docs-only; suite should still pass).

## Test report

- **When:** 2026-09-21 09:13:35–09:14:03 UTC
- **Environment:** branch `main` @ `7874fcc`, `.venv` pytest; docs changes present as uncommitted working-tree edits (v3.0.36 synced in `pyproject.toml` / `ultron/__init__.py`).

### What was tested

Docs parity for listing slash commands and host whitelist CLI, per Testing instructions (grep/table checks + full pytest).

### Results

1. **README Commands allowlisted cell names `/issues_by_status` (and `/list_new_issues` / `/list_unassigned_issues`)** — **PASS** — cell lists `/list_new_issues`, `/issues_by_status`, `/list_unassigned_issues` (plus find/top/new_ticket).
2. **USER_GUIDE “First commands to try” table rows for `/list_new_issues` and `/list_unassigned_issues`** — **PASS** — both rows present with age/limit config wording.
3. **OPERATIONS documents `ultron add token`, Discord `/approve`, `ULTRON_STATE_DIR`, pending TTL** — **PASS** — “Whitelist / approve” subsection covers `/approve`, `ultron add token '<token>'`, state files under `ULTRON_STATE_DIR`, `TOKEN_TTL_SECONDS` 300s; English-only (no non-ASCII letters); no secret-like strings in the subsection.
4. **Optional pytest** — **PASS** — `.venv/bin/pytest -q` → **293 passed** in 7.90s.

### Overall: **PASS**

Operator feedback: Docs now name all three listing commands consistently and document host `ultron add token` next to Discord `/approve`. No product-code changes required for this task; working-tree docs/version bump remain for the committer.
