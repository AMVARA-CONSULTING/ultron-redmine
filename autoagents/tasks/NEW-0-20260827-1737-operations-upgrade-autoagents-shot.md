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
