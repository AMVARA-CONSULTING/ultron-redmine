# Document pi.bin_path and ULTRON_PI_BIN in config/ops

## Tracker
- **Redmine:** (none — enhancement reviewer)
- **GitHub:** (none)
- **0** (when no issue)

## Problem / goal

Operators who cannot rely on `node_modules/.bin/pi` need an explicit binary override. Code already supports **`pi.bin_path`** (`PiConfig` in `ultron/config.py`) and **`ULTRON_PI_BIN`** (`.env.example`, `ultron/pi_resolve.py`), and OPERATIONS already documents the cursor-agent equivalent — but **`config.example.yaml`’s `pi:` comment block omits `bin_path`**, and OPERATIONS never states the pi resolution order. Failed `/pi` / `/audit` with “pi binary not found” is harder to fix than it should be.

## Evidence (008 preflight / review)

- Weekly due; empty task queue.
- `PiConfig.bin_path` exists; `config.example.yaml` `pi:` example lists enabled/workspace/model/timeout/busy knobs only — no `bin_path`.
- OPERATIONS Amvara section documents **`ULTRON_CURSOR_AGENT_BIN`** / `cursor_agent.bin_path` but not pi’s override path (only “`npm install` for pi”).

## High-level instructions for coder

- In **`config.example.yaml`**, extend the **`pi:`** comment block with **`bin_path`** (purpose + `# Example:`), English only; keep `pi: {}` default.
- In **`docs/OPERATIONS.md`** (Amvara / pi subsection), document resolution order: **`ULTRON_PI_BIN`** → **`pi.bin_path`** → **`node_modules/.bin/pi`** after `npm install` (mirror the cursor-agent sentence nearby).
- Do not change runtime resolution logic unless docs reveal a true mismatch — then fix code to match documented order in `resolve_pi_bin`.
- Pass/fail: grep/`config.example.yaml` shows `bin_path` under pi comments; OPERATIONS mentions `ULTRON_PI_BIN` and `pi.bin_path`; no contradiction with `ultron/pi_resolve.py`.
