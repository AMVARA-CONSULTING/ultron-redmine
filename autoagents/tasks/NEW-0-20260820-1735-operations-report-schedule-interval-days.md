# Clarify OPERATIONS report_schedule interval_days

## Tracker
- **Redmine:** (none — enhancement reviewer)
- **GitHub:** (none)
- **0** (when no issue)

## Problem / goal

`docs/OPERATIONS.md` documents `interval_hours | interval_days` for **`report_schedule`**, but the same bullet then says jobs run only when **`interval_hours`** have elapsed — without stating that **`interval_days`** is converted to hours (`days * 24`) at config load. Operators copying the weekly `interval_days: 7` example from `config.example.yaml` may think the prose and the YAML disagree.

## Evidence (008 preflight / review)

- Weekly 008 scan of operator docs vs `ultron/config.py` `_parse_report_schedule` (idays → `interval_hours = max(1, days * 24)`).
- `config.example.yaml` examples use **`interval_days: 7`**; OPERATIONS never explains the conversion.
- No prior task covers this wording gap.

## High-level instructions for coder

- In **`docs/OPERATIONS.md`** (report_schedule bullet under Logs and scheduled posts), clarify that **`interval_days`** is accepted and normalized to **`interval_hours`** (`× 24`) before the hourly loop compares elapsed time; keep the existing command list and channel_id warnings.
- Optional one-line cross-check against **`config.example.yaml`** comment block only if a sentence is already ambiguous there (prefer minimal edits).
- Pass: OPERATIONS states the days→hours conversion; no code change required unless a doc example is factually wrong; pytest green.
