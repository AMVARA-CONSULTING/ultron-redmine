---
## Closing summary (TOP)

- **What happened:** Enhancement task to document `pi.bin_path` / `ULTRON_PI_BIN` in config example and OPERATIONS so operators can fix “pi binary not found”.
- **What was done:** Documented `bin_path` under the `pi:` comment block in `config.example.yaml` and the resolution order in `docs/OPERATIONS.md` (matches `resolve_pi_bin`); no runtime code change.
- **What was tested:** Docs/config greps, spot-check of `resolve_pi_bin`, and `.venv/bin/pytest -q` (293 passed); overall PASS.
- **Why closed:** All acceptance criteria and the test report passed.
- **Closed at (UTC):** 2026-09-14 09:18
---

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

## Handoff log

- 2026-09-14: Implementation complete (`config.example.yaml` pi `bin_path`, OPERATIONS resolution order, matches `resolve_pi_bin`). Testing instructions present → **WIP → UNTESTED**.

## Testing instructions

1. Confirm `config.example.yaml` `pi:` comment block documents **`bin_path`** (purpose + `# Example:` / sample under the `# pi:` example mapping) and default remains **`pi: {}`**.
2. Confirm `docs/OPERATIONS.md` (Amvara section) states pi resolution order **`ULTRON_PI_BIN` → `pi.bin_path` → `node_modules/.bin/pi`**.
3. Grep: `bin_path` under pi comments in `config.example.yaml`; `ULTRON_PI_BIN` and `pi.bin_path` in `docs/OPERATIONS.md`.
4. Spot-check against `ultron/pi_resolve.py` `resolve_pi_bin`: same order, no code change required.
5. Regression: `.venv/bin/pytest -q` (293 passed at implement time); patch version **3.0.34** in `pyproject.toml` and `ultron/__init__.py`.

## Test report

- **Date/time (UTC):** 2026-09-14 09:17:35 start → 09:17:57 end
- **Environment:** branch `main` (synced), `.venv` present

### What was tested

Docs/config for `pi.bin_path` / `ULTRON_PI_BIN` per Testing instructions; spot-check of `resolve_pi_bin`; full pytest suite; version pins.

### Results

1. **PASS** — `config.example.yaml` documents `bin_path` (purpose line + `# Example:` and `#   bin_path: ""` under `# pi:`); default remains `pi: {}`.
2. **PASS** — `docs/OPERATIONS.md` Amvara section: Resolution order **`ULTRON_PI_BIN` → `pi.bin_path` → `node_modules/.bin/pi`**.
3. **PASS** — Grep: `bin_path` in pi comments (`config.example.yaml`); `ULTRON_PI_BIN` and `pi.bin_path` in OPERATIONS.
4. **PASS** — `resolve_pi_bin` checks env → `bin_path_cfg` → `node_modules/.bin/pi`; matches docs; no code change needed.
5. **PASS** — `.venv/bin/pytest -q`: **293 passed**; `pyproject.toml` / `ultron/__init__.py` both **3.0.34**.

### Overall: **PASS**

Operator feedback: Documentation and example config now mirror runtime resolution, so “pi binary not found” should be easier to fix via env or YAML. No product code changes required; regression suite clean.
