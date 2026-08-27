---
## Closing summary (TOP)

- **What happened:** OPERATIONS Self-upgrade table still said `/upgrade` was a bare cursor-agent edit, while production creates a FEAT task and runs autoagents `shot`.
- **What was done:** Updated `docs/OPERATIONS.md` Self-upgrade table and nearby prose to FEAT + `AGENT_GIT_SYNC=0 … shot` + dump + Redmine #7406 + restart; cross-linked agent-loop; version **3.0.31**.
- **What was tested:** All tester checks passed (no stale phrase, FEAT/shot/#7406 present, parity with agent-loop and `_HELP_TEXT`); pytest **284** green.
- **Why closed:** All acceptance criteria passed; docs match production `/upgrade` pipeline.
- **Closed at (UTC):** 2026-08-27 17:50
---

# Align OPERATIONS `/upgrade` with autoagents FEAT shot

## Tracker
- **Redmine:** (none — enhancement reviewer)
- **GitHub:** (none)
- **0** (when no issue)

## Problem / goal

`docs/OPERATIONS.md` **Self-upgrade** table still describes **`/upgrade`** as “**cursor-agent** edits the Ultron checkout”. Production behavior (and `_HELP_TEXT` / `docs/agent-loop.md` / the Autoagents section later in the same file) is: create a **`FEAT-*`** task, run **`ultron-agent-loop.sh shot`**, then dump + Redmine **#7406** note + restart. Operators reading only the table get the wrong mental model.

## Evidence (008 preflight / review)

- Weekly due (`G008_WEEKLY_DUE=1`, 7 days since last 008 review); empty task queue.
- `docs/OPERATIONS.md` Self-upgrade table (~line 169): `/upgrade` → “cursor-agent edits…”.
- Same file Autoagents section (~line 229) and `docs/agent-loop.md` already describe FEAT + `shot`.
- Code: `ultron/self_upgrade.py` (`create_upgrade_feat_task`, `run_autoagents_upgrade_shot`); `_HELP_TEXT` upgrade bullet.

## High-level instructions for coder

- Update the **Self-upgrade** table (and any nearby prose that still implies a bare cursor-agent edit) in **`docs/OPERATIONS.md`** so **`/upgrade`** matches **`docs/agent-loop.md`**: FEAT under `autoagents/tasks/`, `AGENT_GIT_SYNC=0 … shot`, dump, Redmine **#7406**, restart.
- Keep **self-repair** wording accurate (same pipeline as `/upgrade` if that is still true).
- Cross-link **[agent-loop.md](agent-loop.md)** if helpful; do not duplicate the full shot pipeline.
- Pass: table + prose no longer say cursor-agent alone implements `/upgrade`; FEAT/`shot` language present; no contradiction with the Autoagents section or `_HELP_TEXT`.
- Tester: grep/read OPERATIONS Self-upgrade vs agent-loop `/upgrade` section for parity; no `ultron/` code change required unless a one-line help tweak is clearly needed (prefer docs-only).

## Testing instructions

1. Open **`docs/OPERATIONS.md`** section **Self-upgrade, self-repair, and feedback**.
2. Confirm the **`/upgrade text`** table row describes **FEAT** under **`autoagents/tasks/`**, **`AGENT_GIT_SYNC=0 … shot`**, dump, Redmine **#7406**, and restart — **not** “cursor-agent edits the Ultron checkout” alone.
3. Confirm **Self-repair** still says the **same pipeline** as `/upgrade`.
4. Confirm a cross-link to **`agent-loop.md`** (Discord `/upgrade` one-shot) is present near the table.
5. Grep for stale wording:
   ```bash
   grep -n 'cursor-agent edits' docs/OPERATIONS.md || echo 'OK: no stale phrase'
   grep -n 'FEAT\|shot\|#7406' docs/OPERATIONS.md | head -20
   ```
6. Spot-check parity with **`docs/agent-loop.md`** section **Discord `/upgrade` (one shot)** and Discord **`_HELP_TEXT`** `/upgrade` bullet (no contradiction).
7. Confirm version bump: **`pyproject.toml`** and **`ultron/__init__.py`** both **`3.0.31`**.
8. Optional: `.venv/bin/pytest -q` (expect pass; docs-only + version bump).


## Test report

- **Date/time (UTC):** 2026-08-27 17:49 UTC
- **Environment:** branch `main` (synced), `.venv` pytest

### What was tested

Docs-only alignment of `docs/OPERATIONS.md` Self-upgrade table/prose with `docs/agent-loop.md` Discord `/upgrade` (one shot) and `_HELP_TEXT`; version `3.0.31`; optional full pytest.

### Results

1. **Self-upgrade `/upgrade text` row (FEAT + shot + dump + #7406 + restart):** **PASS** — line 170 lists FEAT under `autoagents/tasks/`, `AGENT_GIT_SYNC=0 … shot`, dump, Redmine #7406, systemd restart.
2. **Self-repair same pipeline:** **PASS** — line 171: “same pipeline as `/upgrade` (FEAT + shot → dump → Redmine note → restart)”.
3. **Cross-link to agent-loop.md:** **PASS** — line 174 links `agent-loop.md#discord-upgrade-one-shot`; prose states `/upgrade` is not a bare cursor-agent edit.
4. **No stale `cursor-agent edits`:** **PASS** — `grep -n 'cursor-agent edits' docs/OPERATIONS.md` → OK: no stale phrase.
5. **FEAT / shot / #7406 present:** **PASS** — grep hits on Self-upgrade table, env notes, and Autoagents section.
6. **Parity with agent-loop.md + `_HELP_TEXT`:** **PASS** — agent-loop Discord `/upgrade` section matches FEAT-7406 + shot + dump + note + restart; `_HELP_TEXT` upgrade bullet: FEAT, shot, dump, #7406, restart.
7. **Version 3.0.31:** **PASS** — `pyproject.toml` and `ultron/__init__.py` both `3.0.31`.
8. **pytest:** **PASS** — `284 passed in 7.64s`.

### Overall: **PASS**

Operator feedback: OPERATIONS Self-upgrade table now matches production `/upgrade` (FEAT + shot). No contradiction with agent-loop or Discord help. Docs-only change verified; suite green.

