---
## Closing summary (TOP)

- **What happened:** `docs/RELEASE_CHECKLIST.md` still used obsolete `v0.1.13` tag example and a thin Discord sanity list missing Ultron 3.x memory/confirm/doctor checks.
- **What was done:** Updated tag example to `vX.Y.Z` / `v3.0.7` style; extended Manual sanity with `/status`, `/remember`→`/memory`→`/forget`, Confirm/Cancel; documented `smoke_check.py` and `ultron doctor` entry points.
- **What was tested:** Docs review — no `v0.1.13`; memory/confirm/`/status` present; smoke/doctor CLI `-h` and script path OK — all PASS.
- **Why closed:** All pass/fail criteria passed; docs-only, no product issues.
- **Closed at (UTC):** 2026-07-28 23:04
---
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

## Implementation notes

- Docs-only: `docs/RELEASE_CHECKLIST.md`.
- §3: kept `scripts/smoke_check.py` Ultron 3.0 offline expectations; added **`ultron doctor`** / **`python -m ultron doctor`** (matches `[project.scripts]` `ultron` → `ultron.__main__:main`).
- §4: explicit **`/status`** version, **`/remember`→`/memory`→`/forget`**, one Confirm/Cancel write path; OPERATIONS link retained for fuller smoke.
- §5: tag example is `vX.Y.Z` / `v3.0.7` style; no `v0.1.13`.
- No `ultron/` edits → no version bump (per task).

## Testing instructions

Docs review (no Discord required):

```bash
# No obsolete sole tag example
! grep -q 'v0\.1\.13' docs/RELEASE_CHECKLIST.md

# Manual sanity covers memory + write confirm + /status
grep -E '/remember|/memory|/status|Confirm' docs/RELEASE_CHECKLIST.md

# Smoke + doctor entry points present
grep -E 'smoke_check\.py|ultron doctor|python -m ultron doctor' docs/RELEASE_CHECKLIST.md

# CLI entries exist
.venv/bin/ultron doctor -h
.venv/bin/python -m ultron doctor -h
test -f scripts/smoke_check.py
```

Expect: grep finds the new bullets; doctor `-h` prints usage; no `v0.1.13` in the checklist.

## Test report

- **Date/time (UTC):** 2026-07-28 23:03:27 start → 23:03:34 end
- **Environment:** branch `main` @ `d85ca4a`; `.venv` at `/root/Repos/ultron-redmine/.venv`; package version `3.0.7`

### What was tested

Docs-only review of `docs/RELEASE_CHECKLIST.md` per Testing instructions: obsolete tag grep, manual sanity bullets, smoke/doctor entry points, and live `ultron doctor -h` / `python -m ultron doctor -h` plus `scripts/smoke_check.py` existence.

### Results

| Criterion | Result | Evidence |
|-----------|--------|----------|
| No `v0.1.13` (or long-obsolete) as sole tag example | **PASS** | `! grep -q 'v0\.1\.13'` → no match; §5 uses `vX.Y.Z` / `v3.0.7` |
| Manual section mentions memory + write-confirm | **PASS** | §4 has `/status`, `/remember`→`/memory`→`/forget`, Confirm/Cancel on `/log_time`/`/note`/`/new_ticket` |
| Smoke/doctor commands match real CLI | **PASS** | Doc cites `scripts/smoke_check.py`, `ultron doctor`, `python -m ultron doctor`; `[project.scripts] ultron = ultron.__main__:main`; both `-h` print usage; `test -f scripts/smoke_check.py` OK |

### Overall: **PASS**

Operator feedback: Checklist is aligned with Ultron 3.x release practice — tag placeholder, memory/confirm manual bullets, and doctor/smoke entry points all check out. Docs-only change; no product code regressions in scope.
