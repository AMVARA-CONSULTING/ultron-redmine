---
## Closing summary (TOP)

- **What happened:** RELEASE_CHECKLIST §3 omitted the offline `OK new_ticket_project` gate already expected by smoke_check and OPERATIONS.
- **What was done:** Added `OK new_ticket_project` to the Ultron 3.0 offline OK-line list in RELEASE_CHECKLIST so it matches OPERATIONS; version bumped to 3.0.28.
- **What was tested:** Docs grep alignment (six OK names), full pytest 284 passed, smoke_check printed `OK new_ticket_project`.
- **Why closed:** All acceptance criteria passed; checklist and OPERATIONS agree on the six offline gates.
- **Closed at (UTC):** 2026-08-20 17:41
---

# Align RELEASE_CHECKLIST smoke OK lines with new_ticket_project

## Tracker
- **Redmine:** (none — enhancement reviewer)
- **GitHub:** (none)
- **0** (when no issue)

## Problem / goal

`scripts/smoke_check.py` and `docs/OPERATIONS.md` expect an offline **`OK new_ticket_project:`** line (Ultron **3.0.25**), but **`docs/RELEASE_CHECKLIST.md`** §3 still lists only **OK version / watching_presence / user_memory / nl_fastpath / write_confirm**. Operators following the release checklist can miss a required offline gate.

## Evidence (008 preflight / review)

- Weekly due (`G008_WEEKLY_DUE=1`); queue empty; pytest 282 passed; smoke prints `OK new_ticket_project: 05_ resolve + autocomplete sort`.
- Closed `CLOSED-0-20260813-1731-smoke-check-new-ticket-project-defaults` updated OPERATIONS expect-list, not RELEASE_CHECKLIST §3.
- `docs/RELEASE_CHECKLIST.md` line ~21 omits **`OK new_ticket_project`**.

## High-level instructions for coder

- Update **`docs/RELEASE_CHECKLIST.md`** §3 offline Ultron **3.0** OK-line list to include **`OK new_ticket_project`** (same order/wording spirit as OPERATIONS expect comment).
- Do **not** change smoke script behavior unless the checklist text would otherwise be wrong.
- Pass: `grep -n 'new_ticket_project' docs/RELEASE_CHECKLIST.md` hits §3; OPERATIONS and RELEASE lists agree on the six offline OK names; pytest still green.

## Implementation notes (coder)

- **`docs/RELEASE_CHECKLIST.md` §3:** Offline Ultron **3.0** OK-line list now includes **`OK new_ticket_project`** (same six names / order spirit as OPERATIONS expect comment).
- No smoke script changes.
- Version: **3.0.27 → 3.0.28** (`pyproject.toml` + `ultron/__init__.py`).

## Testing instructions

1. **Docs alignment**
   ```bash
   grep -n 'new_ticket_project' docs/RELEASE_CHECKLIST.md
   grep -n 'OK version\|OK new_ticket' docs/RELEASE_CHECKLIST.md docs/OPERATIONS.md
   ```
   Expect: RELEASE §3 lists all six offline OK names including **`OK new_ticket_project`**; OPERATIONS expect comment matches the same six names.

2. **Unit tests**
   ```bash
   .venv/bin/pytest -q
   ```
   Expect: full suite green (docs-only change; no smoke behavior change).

3. **Optional smoke**
   ```bash
   .venv/bin/python scripts/smoke_check.py
   ```
   Expect: an **`OK new_ticket_project:`** line among the offline Ultron **3.0** checks.

## Test report

- **Date/time (UTC):** 2026-08-20 17:39:44 start → 17:40:15 end
- **Environment:** branch `main`, `.venv` (`pytest` / `python` under `.venv/bin`)

### What was tested

Docs alignment of offline Ultron 3.0 OK lines in `docs/RELEASE_CHECKLIST.md` §3 vs `docs/OPERATIONS.md`; full pytest; `scripts/smoke_check.py` offline OK lines including `OK new_ticket_project`.

### Results

1. **Docs alignment — PASS.** `grep -n 'new_ticket_project' docs/RELEASE_CHECKLIST.md` → line 21 (§3). Both RELEASE §3 and OPERATIONS expect comment list the same six names in order: `OK version` / `OK watching_presence` / `OK user_memory` / `OK nl_fastpath` / `OK write_confirm` / `OK new_ticket_project`.
2. **Unit tests — PASS.** `.venv/bin/pytest -q` → **284 passed** in 7.66s.
3. **Smoke — PASS.** `.venv/bin/python scripts/smoke_check.py` exit 0; includes `OK new_ticket_project: 05_ resolve + autocomplete sort` among the six offline Ultron 3.0 lines (version reported 3.0.28).

### Overall: **PASS**

Operators following the release checklist now see the same six offline OK gates as OPERATIONS. Docs-only change; suite and smoke remain green.
