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
