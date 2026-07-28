---
## Closing summary (TOP)

- **What happened:** Operators needed a repeatable smoke checklist (and offline automation) for Ultron 3.0 memory, NL fast-path, and write confirms beyond unit coverage.
- **What was done:** Extended `scripts/smoke_check.py` with offline Ultron 3.0 checks; added Manual Discord smoke docs (`OPERATIONS.md` + pointers); pytest coverage for smoke helpers.
- **What was tested:** Focused pytest 44 passed; smoke_check OK (version/memory/fastpath/write_confirm + Redmine/LLM); live Discord 6-step SKIP (no guild session) — overall PASS.
- **Why closed:** Acceptance criteria met; interactive Discord UI left as explicit operator follow-up SKIP.
- **Closed at (UTC):** 2026-07-28 23:22
---
# Integration smoke: memory + fast-path + write confirm (Discord)

## Tracker
- **Redmine:** (none — Ultron 3.0 follow-up)
- **GitHub:** (none)
- **0**

## Problem / goal

Unit tests cover pieces of Ultron **3.0.0**, but operators need a **repeatable smoke checklist** (and optional automation via `scripts/smoke_check.py` if extendable) proving memory, fast-path, and confirms work on the live bot (amvara4 / Discord guild).

## Context (shipped)

- Live service: `ultron.service` on amvara4, version **3.0.0+**
- Memory dir: `data/user_memory/`
- Slash: `/remember` `/forget` `/memory` `/note` `/new_ticket` `/log_time` `/summary`
- NL: `@Ultron summarize #N`, `@Ultron remember key: value`

## High-level instructions for coder / tester

- Extend `scripts/smoke_check.py` **only if** it can validate offline pieces (import `UserMemoryStore`, `try_nl_fastpath`, version ≥ 3.0.0) without Discord tokens in the task file.
- Append a **Manual Discord smoke** section to `docs/USER_GUIDE.md` or `docs/OPERATIONS.md` (short): numbered steps + expected outcomes.
- After dump/restart on a host with Discord: run the checklist; paste results into this task’s **Test report** when moving to UNTESTED/TESTING.
- Do not commit `.env`, tokens, or real Redmine issue bodies with secrets.

### Manual Discord smoke (must verify)

1. `/status` shows Ultron **v3.0.x**.
2. `/remember preferred_project: 10_AMVARA` → ack; `/memory` lists it; file appears under `data/user_memory/`.
3. `@Ultron summarize #<known-issue>` → **no** long “routing…” LLM delay if fast-path hits (status may jump to summary); summary returns.
4. `/log_time` on a safe test issue with tiny hours → Confirm → logged; repeat and **Cancel** → no new entry.
5. `/note` → preview Confirm → Cancel → journal unchanged.
6. `/forget preferred_project` → gone from `/memory`.

## Acceptance criteria

- [x] Offline smoke (pytest + optional smoke_check) documented and green
- [x] Manual checklist written in docs
- [x] Test report filled after at least one live Discord pass (or explicit SKIP with reason)

## Implementation notes

- **v3.0.7** — `scripts/smoke_check.py` always runs offline Ultron 3.0 checks (`check_ultron30_offline`): version ≥ 3.0.0, temp-dir `UserMemoryStore` round-trip, `try_nl_fastpath` summarize/remember/miss, write-confirm prompt/author/abort helpers; then existing Redmine/LLM probes.
- Docs: **Manual Discord smoke** in `docs/OPERATIONS.md`; short pointer in `docs/USER_GUIDE.md` and `docs/RELEASE_CHECKLIST.md`.
- Tests: `tests/test_smoke_check.py` covers `_parse_semver` + `check_ultron30_offline`.

## Testing instructions

### Automated

```bash
cd /path/to/ultron-redmine
.venv/bin/pip install -q -e .
.venv/bin/pytest -q tests/test_smoke_check.py tests/test_user_memory.py tests/test_nl_fastpath.py tests/test_write_confirm.py
.venv/bin/python scripts/smoke_check.py
```

Expect focused pytest all PASS. Smoke must print **OK version**, **OK user_memory**, **OK nl_fastpath**, **OK write_confirm** (Redmine/LLM OK or SKIP depending on `.env`).

### Manual Discord (after dump/restart on live host)

Follow **Manual Discord smoke (Ultron 3.0)** in `docs/OPERATIONS.md` (same six steps as above). Paste outcomes into **Test report**.

### Notes for tester

- No Discord tokens in this task file.
- Live Discord steps may be SKIPPED in the coder Test report if this agent session has no guild access; tester should run them on amvara4.

## Test report

- **Date/time (UTC):** 2026-07-28 23:05 UTC (approx.)
- **Environment:** repo `main` worktree, `.venv`; host has `.env` + Redmine/LLM

### What was tested

1. Focused pytest: smoke_check / user_memory / nl_fastpath / write_confirm
2. Live `scripts/smoke_check.py` (offline + Redmine + LLM)
3. Manual Discord checklist on live guild

### Results

| Criterion | Result | Evidence |
|-----------|--------|----------|
| Offline smoke pytest PASS | **PASS** | `44 passed` (`test_smoke_check` + memory + fastpath + write_confirm) |
| `smoke_check.py` Ultron 3.0 offline OK | **PASS** | OK version 3.0.7; OK user_memory; OK nl_fastpath; OK write_confirm; OK Redmine; OK LLM gemma4 |
| Manual checklist in docs | **PASS** | `docs/OPERATIONS.md`, pointer in USER_GUIDE + RELEASE_CHECKLIST |
| Live Discord 6-step smoke | **SKIP** | Coder agent has no Discord guild session; tester must run OPERATIONS checklist on amvara4 after dump/restart |

### Overall: **PARTIAL** (offline green; Discord live deferred to tester)

## Test report (tester)

- **Date/time (UTC):** 2026-07-28 23:21–23:22 UTC
- **Environment:** branch `main` (synced), host **amvara4**, `.venv`, package **3.0.8**; `ultron.service` active (PID from restart 01:14:54 CEST)

### What was tested

1. Focused pytest per Testing instructions
2. `scripts/smoke_check.py` (offline Ultron 3.0 + Redmine + LLM)
3. Docs checklist presence (`OPERATIONS.md` Manual Discord smoke)
4. Live host corroboration via `ultron.log` / systemd (no interactive Discord client)
5. Manual Discord 6-step guild checklist

### Results

| Criterion | Result | Evidence |
|-----------|--------|----------|
| Offline smoke pytest PASS | **PASS** | `44 passed` in 1.56s (`test_smoke_check` + `test_user_memory` + `test_nl_fastpath` + `test_write_confirm`) |
| `smoke_check.py` Ultron 3.0 offline OK | **PASS** | OK version 3.0.8; OK user_memory; OK nl_fastpath; OK write_confirm; OK Redmine 200; OK LLM gemma4:latest |
| Manual checklist in docs | **PASS** | `docs/OPERATIONS.md` § Manual Discord smoke; pointers in USER_GUIDE + RELEASE_CHECKLIST |
| Live bot Discord gateway (host) | **PASS** | `ultron.log`: Logged in as Ultron#7482 \| Ultron **v3.0.8**; user_memory store ready; slash synced to guild |
| Live Discord 6-step smoke (`/status`…`/forget`) | **SKIP** | Tester agent has no Discord guild interactive session; cannot exercise slash/NL UI. Operators: run OPERATIONS checklist once on amvara4. |

### Overall: **PASS**

Operator feedback: Offline automation and docs deliverables are green on amvara4 with live bot **v3.0.8**. Interactive Discord six-step smoke remains an operator follow-up (explicit SKIP). Safe to close this task; re-run OPERATIONS checklist after the next dump/restart if you want guild UI confirmation on record.
