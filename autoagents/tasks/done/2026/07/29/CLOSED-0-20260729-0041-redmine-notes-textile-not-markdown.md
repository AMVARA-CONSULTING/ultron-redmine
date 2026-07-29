---
## Closing summary (TOP)

- **What happened:** Redmine journal notes were Markdown-ish; this instance expects Textile, so self-upgrade and `/note` journals rendered poorly.
- **What was done:** Added `ultron/redmine_textile.py`, rebuilt self-upgrade notes from structured fields, made `/note` polish Textile-only with scrub; reviewed all `add_note` writers.
- **What was tested:** `tests/test_redmine_textile.py` + `tests/test_self_upgrade.py` — 16 passed; live Discord `/note` optional/skipped.
- **Why closed:** All acceptance criteria passed; Textile path locked by helper and snapshot tests.
- **Closed at (UTC):** 2026-07-29 19:48
---

# Redmine journal notes must use Textile, not Markdown

## Tracker
- **Redmine:** (none — bug / formatting follow-up; see self-upgrade notes on #7406 and similar)
- **GitHub:** (none)
- **0**

## Problem / goal

Ultron posts some Redmine journal notes in **Markdown** (or Markdown-ish Discord markup). This Redmine instance expects **Textile** for journals, so notes look wrong in the UI (literal `**bold**`, fenced ` ``` ` blocks, Discord `_italics_`, etc.).

**Concrete example:** the **self-upgrade / self-repair** report note written by `ultron/self_upgrade.py` (`_outcome_redmine_notes` → `RedmineClient.add_note`). Today it only strips `**` and still leaves Markdown/Discord constructs from `_format_outcome_report` (headings via bold labels, triple-backtick log tails, backticks around paths).

The same class of bug likely affects **`/note`** / NL `note`: `NOTE_SYSTEM` in `ultron/workflows.py` still says *“Use markdown only if the user already used it”*, and `_note_body_with_author` prefixes `_Note written by … from Discord_` (Discord markdown underscore), which is not a proper Textile byline.

## Evidence

- `ultron/self_upgrade.py`: `_outcome_redmine_notes` — `text.replace("**", "")` only; body built with Markdown-oriented `**Label:**` and ` ``` ` fences in `_format_outcome_report`.
- `ultron/workflows.py`: `NOTE_SYSTEM` + `_note_body_with_author`.
- Operator observation: self-update notes in Redmine render as Markdown source, not Textile.

## High-level instructions for coder

- Add a small shared helper (e.g. `ultron/redmine_textile.py` or under `textutil`) that formats **Redmine journal bodies in Textile**:
  - Bold/strong → Textile `*text*` (or `**` only if you confirm Textile flavor; prefer classic Redmine Textile `*strong*` / `_em_`).
  - Inline code → `@code@` (not backticks).
  - Multi-line logs / shot tails → `<pre>...</pre>` or Textile `bc. ` / indented pre blocks — pick one style and stick to it.
  - Lists → Textile `* ` / `# ` as appropriate.
  - Do **not** emit Markdown ` ``` `, `**`, `# ` ATX headings, or Discord spoiler/mention syntax in journal notes.
- Rework **`_outcome_redmine_notes`** (and optionally the Discord `FeedbackReport` path separately): Discord feedback may stay Markdown; **Redmine path must be Textile-only**. Prefer building the Redmine note from structured fields rather than stripping Markdown from the Discord report.
- Fix **`/note`** path:
  - Change `NOTE_SYSTEM` to require **Textile** for Redmine (plain text + Textile markup only).
  - Author line in Textile (e.g. `_Note written by Name from Discord_` is OK in Textile for emphasis, or use a plain `Note written by Name from Discord:` line without Discord-only conventions).
- Grep for other `add_note` call sites; apply the same rule everywhere Ultron writes journals.
- Tests: unit-test the Textile helper (bold, code, pre/log, no leftover ` ``` ` / `**`); optional snapshot of a self-upgrade note body.
- English for any user-facing Discord strings; Redmine note language can stay English like today.
- Patch-bump `pyproject.toml` + `ultron/__init__.py` when shipping the fix.

## Acceptance criteria

- [x] Self-upgrade Redmine note contains no Markdown fences or `**`; uses Textile/`<pre>` for logs
- [x] `/note` LLM prompt + author prefix documented as Textile-oriented; tests cover helper
- [x] All `add_note` writers reviewed (list them in Implementation notes)
- [x] `.venv/bin/pytest -q` for new/changed tests PASS
- [x] Manual: trigger a dry note or inspect last `/upgrade` note format on Redmine (or unit-equivalent) — journals readable as Textile in the UI

## Implementation notes

- Added `ultron/redmine_textile.py`: `textile_strong` / `textile_em` / `textile_code` / `textile_pre` / `textile_labeled` / `textile_bullet_list`, plus `scrub_markdown_to_textile` safety net and `has_markdown_artifacts`.
- `_outcome_redmine_notes` no longer strips Discord Markdown from `_format_outcome_report`; it builds a Textile body from structured `SelfUpgradeOutcome` fields. Shot tails go in `<pre>`; `**` / ``` markers are neutralized in log text. Discord `FeedbackReport` path unchanged (still Markdown).
- `NOTE_SYSTEM` requires Textile-only markup; `polish_note_text` runs `scrub_markdown_to_textile` on LLM output. Author prefix kept as Textile emphasis `_Note written by … from Discord_`.
- Version bump **3.0.3 → 3.0.4**.

### `add_note` writers reviewed

| Site | Path | Change |
|------|------|--------|
| Self-upgrade / self-repair | `ultron/self_upgrade.py` → `_report_to_redmine` → `_outcome_redmine_notes` | Textile from fields |
| Slash `/note` (after confirm) | `ultron/bot.py` | Uses polished body (Textile prompt + scrub) |
| NL `note` (after confirm) | `ultron/bot.py` | Same via `add_formatted_note(..., skip_post=True)` |
| Direct workflow post | `ultron/workflows.py` → `add_formatted_note` | Same polish + scrub |

## Testing instructions

```bash
cd /root/Repos/ultron-redmine
.venv/bin/pip install -q -e .
.venv/bin/pytest -q tests/test_redmine_textile.py tests/test_self_upgrade.py
```

Expected: all tests PASS (including Textile helper, scrub, and `_outcome_redmine_notes` snapshots with no `**` / ```).

### Manual / live (optional)

1. After dump/restart: post a short `/note` on a test issue, Confirm → open Redmine journal; expect Textile-friendly body (no literal `**` / fences from polish).
2. Or inspect unit-built note via pytest above; optional: next `/upgrade` note on #7406 should use `*Label:*` and `<pre>` for shot log.

## Test report

- **Date/time (UTC):** 2026-07-29 19:47:23 – 19:47:35 UTC
- **Environment:** branch `main` @ `aef4b61`, `.venv` Python 3.13.5 / pytest 9.1.1, package version 3.0.14

### What was tested

- Automated: `.venv/bin/pytest -q tests/test_redmine_textile.py tests/test_self_upgrade.py` (16 tests, verbose confirm of Textile helper + `_outcome_redmine_notes` snapshots).
- Static: `NOTE_SYSTEM` Textile-only wording; `_outcome_redmine_notes` builds from structured fields via `ultron/redmine_textile.py`; `polish_note_text` calls `scrub_markdown_to_textile`.

### Results

| Criterion | Result | Evidence |
|-----------|--------|----------|
| Self-upgrade Redmine note has no MD fences/`**`; Textile/`<pre>` for logs | **PASS** | `test_outcome_redmine_notes_is_textile` / `…_auto_repair` assert no `**` / ``` |
| `/note` prompt + author prefix Textile-oriented; helper tests | **PASS** | `NOTE_SYSTEM` Textile rules; scrub + helper unit tests |
| All `add_note` writers reviewed | **PASS** | Listed in Implementation notes (self-upgrade, slash/NL note, workflow) |
| pytest for new/changed tests | **PASS** | `16 passed in 1.27s` |
| Manual/unit-equivalent journal format | **PASS** | Unit-built notes cover Textile body; live Discord `/note` not run |

### Overall: **PASS**

Operator feedback: Redmine journal Textile path is locked by unit tests for self-upgrade notes and the shared scrub/helper. Optional live `/note` Confirm on a test issue after dump/restart would still be good operator sanity, but not required given the snapshots.
