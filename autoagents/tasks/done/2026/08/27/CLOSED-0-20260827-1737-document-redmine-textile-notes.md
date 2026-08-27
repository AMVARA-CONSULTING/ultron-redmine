---
## Closing summary (TOP)

- **What happened:** Ops and user docs never stated that Redmine journal notes from Ultron are Textile, so operators could expect Discord-style Markdown in Redmine.
- **What was done:** `docs/OPERATIONS.md` and `docs/USER_GUIDE.md` now document Textile for `/note`, compound notes, and upgrade/self-repair Redmine reports; Discord replies stay Markdown.
- **What was tested:** Textile grep and no-Markdown-journals checks passed; code ownership spot-check OK; pytest **284** green; version **3.0.30**.
- **Why closed:** All acceptance criteria passed; docs match runtime Textile journal behavior.
- **Closed at (UTC):** 2026-08-27 17:41
---

# Document Redmine journal Textile (not Markdown) in ops/user docs

## Tracker
- **Redmine:** (none — enhancement reviewer)
- **GitHub:** (none)
- **0** (when no issue)

## Problem / goal

Ultron writes Redmine journal notes as **Textile** (`ultron/redmine_textile.py`, `/note` polish, self-upgrade reports). That behavior was implemented (CLOSED-0-20260729-0041) but **`docs/OPERATIONS.md`** and **`docs/USER_GUIDE.md`** never say so. Operators and Discord users may expect Markdown journals and misread formatting in Redmine.

## Evidence (008 preflight / review)

- Weekly due; empty task queue; pytest 284 passed; smoke OK.
- Code/prompts: `NOTE_SYSTEM` + `scrub_markdown_to_textile` in `ultron/workflows.py`; `_outcome_redmine_notes` in `ultron/self_upgrade.py`.
- Grep of `docs/*.md`: no Textile/journal-format guidance (USER_GUIDE only covers Confirm vs immediate `/note`).

## High-level instructions for coder

- In **`docs/OPERATIONS.md`** Redmine (or Health / Manual smoke) section, add a short bullet: journals from **`/note`**, compound @mention notes, and **`/upgrade`** / self-repair Redmine reports use **Textile** (via `ultron/redmine_textile.py`); Discord replies stay Markdown.
- In **`docs/USER_GUIDE.md`**, one sentence near **`/note`** / Write confirmation: notes land in Redmine as Textile-friendly text (not Discord Markdown).
- Optional: one line in Manual Discord smoke step for `/note` (“journal readable as Textile, no literal `**` / fences”).
- Do **not** rework Textile helpers or prompts unless a docs example reveals a real bug.
- Pass: both docs mention Textile for Redmine journals; no claim that journals are Markdown.
- Tester: grep `Textile` in OPERATIONS + USER_GUIDE; spot-check against `NOTE_SYSTEM` / closed textile task outcome.

## Testing instructions

1. Grep both docs for Textile:
   ```bash
   grep -n Textile docs/OPERATIONS.md docs/USER_GUIDE.md
   ```
   Expect hits in OPERATIONS Redmine (journal format bullet) and Manual Discord smoke step 7; USER_GUIDE Write confirmation near `/note`.
2. Confirm neither file claims Redmine journals are Markdown:
   ```bash
   grep -niE 'journal.*[Mm]arkdown|[Mm]arkdown.*journal' docs/OPERATIONS.md docs/USER_GUIDE.md || true
   ```
   (Discord Markdown for replies is OK; journals must be described as Textile.)
3. Spot-check: `ultron/workflows.py` (`NOTE_SYSTEM` / scrub) and `ultron/redmine_textile.py` still own the behavior — docs-only change; no code rework required.
4. Regression: `.venv/bin/pytest -q` (expect pass); version `3.0.30` in `pyproject.toml` and `ultron/__init__.py`.

## Test report

- **Started:** 2026-08-27 17:40:16 UTC
- **Finished:** 2026-08-27 17:40:38 UTC
- **Environment:** branch `main`, `.venv` Python 3.13.5 (`/root/Repos/ultron-redmine/.venv/bin/python`)

### What was tested

Docs Textile guidance for Redmine journals (`OPERATIONS.md`, `USER_GUIDE.md`), no “journals are Markdown” claim, code ownership spot-check (`NOTE_SYSTEM` / `scrub_markdown_to_textile`), pytest regression, version `3.0.30`.

### Results

1. **Textile grep in both docs** — **PASS** — `OPERATIONS.md:65` Journal format bullet; `OPERATIONS.md:216` Manual Discord smoke step 7; `USER_GUIDE.md:63` Write confirmation near `/note`.
2. **No claim journals are Markdown** — **PASS** — `journal.*Markdown` hits only negate Markdown for journals (“not Markdown” / “Textile-friendly… not Discord Markdown”); Discord replies correctly stay Markdown.
3. **Spot-check code ownership** — **PASS** — `NOTE_SYSTEM` in `ultron/workflows.py` states Textile; polish returns `scrub_markdown_to_textile`; helper in `ultron/redmine_textile.py`. Docs-only; no product code change needed.
4. **Regression + version** — **PASS** — `.venv/bin/pytest -q` → **284 passed** in 7.58s; `pyproject.toml` and `ultron/__init__.py` both `3.0.30`.

### Overall: **PASS**

Operator feedback: Docs now match runtime Textile journals for `/note`, compound notes, and upgrade reports. Grep and suite look clean; live Discord `/note` Textile readability was not re-exercised in this pass (smoke step text covers it). Ready to close.
