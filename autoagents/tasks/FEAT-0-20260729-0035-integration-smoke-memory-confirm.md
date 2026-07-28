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

- [ ] Offline smoke (pytest + optional smoke_check) documented and green
- [ ] Manual checklist written in docs
- [ ] Test report filled after at least one live Discord pass (or explicit SKIP with reason)
