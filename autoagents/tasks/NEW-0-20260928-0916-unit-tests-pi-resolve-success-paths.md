# Expand pi_resolve unit tests (success paths + build settings)

## Tracker
- **Redmine:** (none — enhancement reviewer)
- **GitHub:** (none)
- **0** (when no issue)

## Problem / goal

`ultron/pi_resolve.py` gates **`/pi`** and Amvara-pi: **`resolve_pi_bin`**, **`pi_availability_message`**, **`resolve_ollama_endpoint`**, **`build_pi_run_settings`**. `tests/test_pi_agent.py` covers only **failure** paths (no chain, missing binary, explicit disable). Success paths for env/`bin_path` resolution, Ollama endpoint overrides, and `build_pi_run_settings` assembly are untested — easy to break while “tests still pass”.

## Evidence (008 preflight / review)

- Weekly due; empty queue; pytest **315** pass; smoke OK.
- Docs for `ULTRON_PI_BIN` / `pi.bin_path` already closed (2026-09-14); this is the missing **test** follow-through.
- No archived task for pi_resolve success-path / `build_pi_run_settings` coverage.

## High-level instructions for coder

- Extend **`tests/test_pi_agent.py`** or add **`tests/test_pi_resolve.py`** with offline cases:
  - **`resolve_pi_bin`**: fake executable via tmp_path for **`ULTRON_PI_BIN`**, then **`bin_path_cfg`**, then `node_modules/.bin/pi`; non-executable env/cfg raises.
  - **`resolve_ollama_endpoint`**: returns chain primary when `pi.ollama_base_url` / `pi.model` empty; prefers pi overrides when set; `None` when no Ollama-like chain entry.
  - **`build_pi_run_settings`**: happy path with fake pi binary + Ollama chain (workspace/config_dir defaults); rejects when availability message would fire.
- Optional: cloud-only `llm_chain` → availability message mentions Ollama-like requirement (if not already covered).
- Pass/fail: new tests green; `.venv/bin/pytest -q` full suite passes; no Discord/network.
