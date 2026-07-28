# Refresh RELEASE_CHECKLIST for Ultron 3.x

## Tracker
- **Redmine:** (none — enhancement reviewer)
- **GitHub:** (none)
- **0**

## Problem / goal

`docs/RELEASE_CHECKLIST.md` still shows an annotated-tag example **`v0.1.13`** and a thin Discord manual sanity list (`/help`, whitelist, one Redmine command). After **Ultron 3.0**, releases should explicitly remind operators to verify durable memory, write Confirm/Cancel, and that **`smoke_check` / `ultron doctor`** exercise the real LLM backend. Stale checklist increases the chance of shipping without those checks.

## Evidence (008 preflight / review)

- Weekly enhancement pass; docs skim vs 3.0.0 features.
- `docs/RELEASE_CHECKLIST.md` §5 still cites `v0.1.13`; §4 manual sanity omits `/remember`, Confirm on `/log_time`/`/note`/`/new_ticket`, and doctor.
- Not covered by **FEAT-0-…-help-docs-parity-ultron-30** (Discord `/help` + USER_GUIDE focus) or the integration-smoke FEAT (live Discord checklist in OPERATIONS/USER_GUIDE).

## High-level instructions for coder

- Update the tag example to current major.minor style (e.g. `v3.0.x` / match `__version__` guidance) — do not invent a fake release number as “current”; use a placeholder like `vX.Y.Z` matching `pyproject.toml` at release time.
- Extend **Manual sanity** with short bullets: `/remember`+`/memory`, one Confirm Cancel path, `/status` version line.
- Point optional smoke to both `scripts/smoke_check.py` and `ultron doctor` (or `python -m ultron doctor` / CLI entry the repo actually ships).
- English only; no secrets; docs-only change (no `ultron/` edits → no version bump unless project policy requires it for docs — default: skip bump for checklist-only).

## Pass / fail criteria for tester

- [ ] Checklist has no `v0.1.13` (or other long-obsolete) as the sole tag example.
- [ ] Manual section mentions memory and at least one write-confirm flow.
- [ ] Smoke/doctor commands in the doc match real CLI entry points in this repo.
