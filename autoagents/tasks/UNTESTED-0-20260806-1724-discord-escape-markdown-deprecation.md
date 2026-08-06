# Quell discord.utils escape_markdown DeprecationWarning in tests

## Tracker
- **Redmine:** (none — enhancement reviewer)
- **GitHub:** (none)
- **0** (when no issue)

## Problem / goal

Full pytest runs report **35×** `DeprecationWarning: 'count' is passed as positional argument` from `discord.utils` (discord.py **2.7.1**), triggered via `escape_markdown` used in `ultron/bot.py` and `ultron/redmine_listings.py` (and tests that exercise those paths: find_issue, new_ticket, top_tickets). Noise hides real warnings and will become an error under stricter CI filters.

## Evidence (008 preflight / review)

- Weekly 008 scan: `.venv/bin/pytest -q` → `273 passed, 35 warnings` (all this DeprecationWarning).
- Same noise noted on prior closed tasks (e.g. user-memory disk-guards closing notes); never queued as its own fix.
- Repro: `escape_markdown('x')` under `warnings.simplefilter('error', DeprecationWarning)` raises.

## High-level instructions for coder

- Prefer a **small Ultron-owned helper** (e.g. wrap `re.sub` with keyword `count=` / call discord API in the non-deprecated form) used by bot + listings, rather than filtering warnings in pytest.ini.
- Keep escaping behavior identical for Discord markdown in subjects/project names.
- Pass: `.venv/bin/pytest -q` shows **0** DeprecationWarnings from this source (or suite warning count drops accordingly); existing listing/find/top_tickets tests still pass.
- Fail: warnings unchanged or escaping regresses (unescaped `*`/`_` in listing output).

## Implementation notes (coder)

- Added `ultron.discord_format.escape_markdown` — same stock regex / ignore-links behavior as discord.py, but `re.sub(..., count=0, flags=re.MULTILINE)`.
- Switched `ultron/bot.py` and `ultron/redmine_listings.py` off `discord.utils.escape_markdown`.
- `tests/test_discord_format.py` locks parity with discord.utils (DeprecationWarning ignored for reference) and asserts our helper emits no DeprecationWarning.
- Patch bump **3.0.18 → 3.0.19** (`pyproject.toml` + `ultron/__init__.py`).
- Verify: `.venv/bin/pytest -q` → **278 passed** (no escape_markdown DeprecationWarnings; was 35×).

## Testing instructions

1. **Pytest (full suite + warning check)**
   ```bash
   .venv/bin/pip install -q -e .
   .venv/bin/pytest -q -W default
   ```
   Expect all green and **no** `DeprecationWarning: 'count' is passed as positional argument` from `discord.utils` / `escape_markdown`.

2. **Focused helper tests**
   ```bash
   .venv/bin/pytest -q tests/test_discord_format.py tests/test_find_issue.py tests/test_top_tickets.py tests/test_new_ticket.py
   ```
   Expect green; `test_escape_markdown_matches_discord_utils_defaults` and `test_escape_markdown_no_deprecation_warning` pass.

3. **Import / version spot-check**
   ```bash
   .venv/bin/python -c "from ultron.discord_format import escape_markdown; from ultron import __version__; print(__version__, escape_markdown('*x*'))"
   ```
   Expect `3.0.19 \*x\*`.

4. **Manual Discord (optional)**
   - Run `/find_issue` or `/top_tickets` on a subject with `*` / `_`; listing lines should still show escaped markdown (no unintended bold/italic).
