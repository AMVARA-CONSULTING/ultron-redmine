# Ultron

Discord bot for **Redmine**: slash commands, optional LLM summaries/Q&A/notes, scheduled channel listings, and allowlisted @mention routing.

**Python 3.11+** · [`.env.example`](.env.example) · [`config.example.yaml`](config.example.yaml)

## Quick start

```bash
git clone https://github.com/AMVARA-CONSULTING/ultron-redmine.git
cd ultron-redmine
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
cp .env.example .env && cp config.example.yaml config.yaml
# edit .env (DISCORD_TOKEN, REDMINE_URL, REDMINE_API_KEY) and config.yaml
python -m ultron
```

Interactive setup (optional):

```bash
pip install -e ".[wizard]"
ultron wizard
```

**Docker:** `mkdir -p data` then `docker compose up --build` (mounts `.env`, `config.yaml`, `data/`). On Linux, same host URLs as bare metal: add `-f docker-compose.hostnet.yml`.

## Commands

In Discord, **`/help`** is the live list. Short map:

| Who | Commands |
|-----|----------|
| Everyone | `/help`, `/token` (DM) |
| Allowlisted | `/ping`, `/status`, listings (`/list_*`, `/find_issue`, `/top_tickets`, `/new_ticket`), time (`/time_summary`, `/log_time`), LLM (`/summary`, `/ask_issue`, `/note`, `/ol`), audits (`/audit`, `/ca`), `@Ultron` NL routing |
| Admins | `/approve`, `/remove`, `/show_config`, `/pi`, `/upgrade` |

Access: user DMs **`/token`** → admin **`/approve`** (or host `ultron add token '…'`). Admins = `DISCORD_ADMIN_IDS` and/or `admins.json`.

LLM is optional (`llm_chain` in `config.yaml`). Without it, listings and tickets still work; `/summary`, `/ask_issue`, `/note`, `/ol`, and NL routing do not.

## Docs

| Doc | For |
|-----|-----|
| [docs/USER_GUIDE.md](docs/USER_GUIDE.md) | Discord users |
| [docs/OPERATIONS.md](docs/OPERATIONS.md) | Deploy / Redmine / Discord / LLM / systemd |
| [docs/agent-loop.md](docs/agent-loop.md) | Autoagents (`/upgrade`, intake) |
| [docs/RELEASE_CHECKLIST.md](docs/RELEASE_CHECKLIST.md) | Releases |

## License

[MIT](LICENSE)
