# Release checklist

Use this list before tagging or publishing a release. It is the project’s explicit **definition of done** for a version bump.

## 1. Version and changelog

- [ ] Bump **`__version__`** in [`ultron/__init__.py`](../ultron/__init__.py).
- [ ] Bump **`version`** in [`pyproject.toml`](../pyproject.toml) to match (same semver).
- [ ] Update **release notes** (GitHub Releases, internal changelog, or tag annotation) with user-visible changes.

## 2. Automated tests

- [ ] Run **`pytest`** from the repository root (install dev deps: `pip install -e ".[dev]"`).

```bash
python -m pytest tests/ -q
```

## 3. Optional smoke checks

- [ ] Run **[`scripts/smoke_check.py`](../scripts/smoke_check.py)** (no Discord required). Offline Ultron **3.0** lines (**OK version**, **OK user_memory**, **OK nl_fastpath**, **OK write_confirm**) must pass; Redmine/LLM may SKIP without credentials.
- [ ] Run **`ultron doctor`** (or **`python -m ultron doctor`**) — same entry as `[project.scripts]` `ultron` — and confirm paths, bindings, Redmine, and LLM health lines look sane.

```bash
python scripts/smoke_check.py
ultron doctor
# or: python -m ultron doctor
```

- [ ] If the **wizard** extra is installed, run **`ultron wizard`** once and confirm the main menu loads (`pip install -e ".[wizard]"`).

## 4. Manual sanity (when changing Discord behavior)

- [ ] Start the bot against a **test** guild or token; confirm slash commands appear (guild sync if `DISCORD_GUILD_ID` is set).
- [ ] Smoke-test critical flows: **`/help`**, whitelist **`/token`** / **`/approve`**, and one Redmine command if applicable.
- [ ] **`/status`** — version line matches the release (`vX.Y.Z` from `pyproject.toml` / `__version__`).
- [ ] Durable memory: **`/remember`** a harmless key → **`/memory`** lists it → **`/forget`** removes it.
- [ ] One write Confirm/Cancel path: e.g. **`/log_time`** (or **`/note`** / **`/new_ticket`**) → **Confirm** writes; repeat and **Cancel** aborts with no write.
- [ ] For Ultron **3.0** releases: also run the fuller **Manual Discord smoke** checklist in [OPERATIONS.md](OPERATIONS.md) (NL fast-path summarize, etc.).

## 5. Git tag (optional)

- [ ] Create an annotated tag matching **`pyproject.toml`** / `__version__` at release time, e.g. `vX.Y.Z` (Ultron 3.x: `v3.0.7`).
- [ ] Push commits and tags to the remote.

## Success criteria

- Tests pass.
- Version numbers are consistent across `__init__.py` and `pyproject.toml`.
- Release notes describe what changed for operators and/or users.
