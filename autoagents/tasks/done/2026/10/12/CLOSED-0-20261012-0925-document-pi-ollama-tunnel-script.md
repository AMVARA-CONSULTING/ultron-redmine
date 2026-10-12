---
## Closing summary (TOP)

- **What happened:** Enhancement reviewer filed docs for optional Ollama SSH tunnel knobs (`pi.tunnel_script` / `ULTRON_OLLAMA_TUNNEL_SCRIPT`) missing from ops discoverability.
- **What was done:** Documented `tunnel_script` in `config.example.yaml` `pi:` comments and OPERATIONS Amvara/Ollama-busy; patch **3.0.43**.
- **What was tested:** Docs/grep/merge-order checks and pytest all **PASS** (**341** passed); version pins match.
- **Why closed:** All testing criteria passed; ready to archive.
- **Closed at (UTC):** 2026-10-12 09:38
---

# Document pi.tunnel_script / ULTRON_OLLAMA_TUNNEL_SCRIPT

## Tracker
- **Redmine:** (none — enhancement reviewer)
- **GitHub:** (none)
- **0** (when no issue)

## Problem / goal

When Ollama is remote, Ultron can run an optional **SSH tunnel script** before pi / Amvara busy probes (`ensure_ollama_reachable` via `ultron/ollama_reachability.py`). Resolution in the bot is **`ULTRON_OLLAMA_TUNNEL_SCRIPT`** env **or** YAML **`pi.tunnel_script`** (`PiConfig.tunnel_script`).

Operators cannot discover this from ops docs:

- **`.env.example`** documents **`ULTRON_OLLAMA_TUNNEL_SCRIPT`**.
- **`config.example.yaml`** `pi:` comment block lists busy-check knobs and `bin_path` but **omits `tunnel_script`**.
- **`docs/OPERATIONS.md`** Amvara / Ollama-busy prose never mentions the tunnel knobs.

Failed “Ollama unreachable” on hosts that need a tunnel is harder to fix than it should be.

## Evidence (008 preflight / review)

- Weekly due; empty queue; pytest **334** pass; smoke OK.
- Code: `ultron/config.py` `PiConfig.tunnel_script`; bot merges env then YAML before `ensure_ollama_ready_for_inference`.
- OPERATIONS documents `ollama_busy_check` / probe seconds but not tunnel.
- No archived task for tunnel_script / `ULTRON_OLLAMA_TUNNEL_SCRIPT` docs.

## High-level instructions for coder

- In **`config.example.yaml`**, extend the **`pi:`** comment block with **`tunnel_script`** (purpose + `# Example:`; keep `pi: {}` default).
- In **`docs/OPERATIONS.md`** Amvara / Ollama-busy area, add one short bullet: env **`ULTRON_OLLAMA_TUNNEL_SCRIPT`** or YAML **`pi.tunnel_script`** (executable; run when Ollama does not respond; point at `.env.example`).
- Prefer docs-only; English only; no secrets; no behavior change unless a claim is wrong.
- Pass/fail: both files name the knobs; no contradiction with `.env.example` / `PiConfig` / bot merge order (env then YAML).

## Handoff log

- 2026-10-12: Documented `pi.tunnel_script` in `config.example.yaml` and OPERATIONS (env then YAML). Patch **3.0.43**. Testing instructions present → **WIP → UNTESTED**.

## Testing instructions

1. Confirm `config.example.yaml` `pi:` comment block documents **`tunnel_script`** (purpose + `# Example:` / sample under the `# pi:` example mapping) and default remains **`pi: {}`**.
2. Confirm `docs/OPERATIONS.md` (Amvara / Ollama-busy area) names **`ULTRON_OLLAMA_TUNNEL_SCRIPT`** and **`pi.tunnel_script`**, states env wins when non-empty, and points at `.env.example` / `config.example.yaml`.
3. Grep:
   ```bash
   grep -nE 'tunnel_script|ULTRON_OLLAMA_TUNNEL' config.example.yaml docs/OPERATIONS.md .env.example
   ```
4. Spot-check merge order against `ultron/bot.py` (`ULTRON_OLLAMA_TUNNEL_SCRIPT` then `pi.tunnel_script`) and `PiConfig.tunnel_script` in `ultron/config.py`; no runtime code change required.
5. Regression: `.venv/bin/pytest -q` (**341** passed at implement time); patch version **3.0.43** in `pyproject.toml` and `ultron/__init__.py`.

## Test report

- **Started:** 2026-10-12 09:37:51 UTC
- **Finished:** 2026-10-12 09:38:15 UTC
- **Environment:** branch `main`, `.venv` present; after `./scripts/git-sync-main.sh` (already up to date).

### What was tested

Docs-only verification of `pi.tunnel_script` / `ULTRON_OLLAMA_TUNNEL_SCRIPT` operator discoverability per Testing instructions (config example, OPERATIONS, grep, merge-order spot-check, pytest + version).

### Results

1. **`config.example.yaml` `pi:` block documents `tunnel_script` (purpose + `# Example:` / sample under `# pi:` mapping); default `pi: {}`:** **PASS** — lines 180–181 purpose/Example; 192 `tunnel_script: ""` under example mapping; line 199 `pi: {}`.
2. **`docs/OPERATIONS.md` Amvara / Ollama-busy names both knobs, env wins when non-empty, points at `.env.example` / `config.example.yaml`:** **PASS** — line 172 bullet under Ollama busy section.
3. **Grep `tunnel_script|ULTRON_OLLAMA_TUNNEL` across the three files:** **PASS** — hits in `config.example.yaml` (180, 192), `docs/OPERATIONS.md` (172), `.env.example` (80–82).
4. **Merge order matches `ultron/bot.py` (env then YAML) and `PiConfig.tunnel_script`:** **PASS** — `bot.py:2198–2199` `ULTRON_OLLAMA_TUNNEL_SCRIPT` then `pi_cfg.tunnel_script`; `config.py:234` / `:731` field present; docs agree; no runtime edit needed.
5. **Regression pytest + version 3.0.43:** **PASS** — `.venv/bin/pytest -q` → **341 passed** in 8.19s; `pyproject.toml` and `ultron/__init__.py` both `3.0.43`.

### Overall: **PASS**

Operator feedback: Tunnel knobs are discoverable from OPERATIONS and the YAML example without contradicting `.env.example` or the bot’s env-then-YAML merge. Docs-only change; suite green at the stated patch.
