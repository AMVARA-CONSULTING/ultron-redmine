---
## Closing summary (TOP)

- **What happened:** Asking Ultron to summarize one journal note was routed to whole-ticket `summary`.
- **What was done:** Added `summary_note` (last/first/index), a note-only prompt, fast-path and router/planner split from `summary` and write `note`, plus selector and prompt tests. The change is still uncommitted on `main`.
- **What was tested:** `.venv/bin/pytest` on the four named modules passed (**41** in 1.40s). Live Discord phrases 1–6 were not run.
- **Why closed:** Automated acceptance criteria passed.
- **Closed at (UTC):** 2026-10-16 03:36
---

# CLOSED-0 — Summarize one journal note, not the whole ticket

## Tracker
- **Redmine:** none (operator report via Maestro, 2026-10-16)
- **GitHub:** none

## Meta
- **Status:** `closed`
- **Generated:** 2026-10-16T03:20:00Z
- **Assigned agent:** coder

---

## 1. Issue summary

When a user asks Ultron to summarize **one note** of a ticket (Spanish or English: "resume la nota del ticket N", "resumir la última nota de #N", "summarize the last note of issue N"), the bot summarizes the **whole ticket**.

Root cause (confirmed in code):

1. `ultron/nl_fastpath.py` `try_nl_fastpath` falls through to command `summary` whenever a short message has a summary verb and exactly one issue id (`_SUMMARY_VERB_RE` + `extract_issue_ids`, length <= 80). Words like `nota` / `note` / `journal` do not change the route. Example that hits this path: `resume la nota del ticket 123`.
2. There is no read command for a single journal. `summary` and `ask_issue` always call `format_issue_for_summary`, which sends the description plus the last 12 journal notes. The model then answers about the ticket.
3. Command `note` **writes** a journal. It must stay a write. Do not reuse it for "summarize the note".

## 2. Acceptance criteria

- [x] A new NL command `summary_note` summarizes **one** journal entry that has non-empty `notes`.
- [x] The LLM user prompt for that command contains that note text plus a one-line context (issue id, subject, journal id, author, created_on). It does **not** include the description or any other journal.
- [x] System prompt tells the model to summarize that note only. No ticket status recap, no other notes, no invented next steps.
- [x] Fast-path sends note-scoped phrases to `summary_note` and still sends whole-ticket phrases to `summary`.
- [x] Router (`NL_ROUTER_SYSTEM`) and planner (`NL_PLANNER_SYSTEM`) document the split. `note` remains "add a note", never "read/summarize a note".
- [x] Missing note, empty journal, or index out of range returns a short English error with the note count. It does **not** fall back to a whole-ticket summary.
- [x] `pytest` covers fast-path phrases and a pure selector (no network).
- [x] No secrets in commits or task notes.

## 3. Implementation scope

**IN SCOPE:**

- `ultron/nl_fastpath.py` and `tests/test_nl_fastpath.py`
- `ultron/nl_router.py` (`NL_ALLOWED_COMMANDS`, prompt, `_validate_args`) and `tests/test_nl_router.py`
- `ultron/amvara/planner.py` allowed-command list (same args schema)
- `ultron/workflows.py`: `summarize_journal_note` (mirror `summarize_issue` call style: metadata header optional, chain skip, logging)
- `ultron/textutil.py` or a small helper: pure `select_journal_note(issue, selector) -> journal dict | None`
- `ultron/bot.py`: dispatch next to the existing `summary` NL branch and a one-line help mention. Replies stay English, same as `/summary`.
- Help string that lists `@mention` commands, one short line only.

**OUT OF SCOPE:** `.env`, systemd restarts by the coder (loop dump handles runtime), unrelated commands, changing how whole-ticket `/summary` is formatted.

## 4. Technical notes

### Selector

Args:

- `issue_id` (positive int, required)
- `selector` (optional string, default `last`)

Allowed `selector` values:

- `last` — most recent journal with non-empty notes. Use this when the user says "la nota" / "the note" / "última" / "last" / "latest" with no index.
- `first` — oldest such journal ("primera" / "first").
- a positive decimal string (`1`, `2`, `3`) — 1-based index among journals with non-empty notes, in Redmine order (oldest = 1).

Reject any other selector in `_validate_args`.

### Fast-path (before the generic summary fallback)

If the user half (after reply-context strip) contains a summary verb **and** a note word (`nota`, `note`, `notes`, `journal`, `comentario`) **and** exactly one issue id from `extract_issue_ids`:

- invoke `summary_note`, never `summary`
- `last` unless the text has primera/first → `first`, or última/last/latest/reciente → `last`
- if a note index appears (`nota 3`, `note #3`, `3ª nota`, `nota número 3`) set selector to that index
- do this **before** the existing short-message summary fallback

Do **not** treat `summarize note 123` (no `ticket` / `issue` / `#`) as issue 123. Leave that to the LLM router.

These must stay command `summary` (whole ticket):

- `summarize #123`
- `resume el ticket 123`
- `resumen del ticket 123`
- `summarize ticket 42`

These must become `summary_note`:

- `resume la nota del ticket 123` → issue 123, selector `last`
- `resumir la última nota de #8066` → 8066, `last`
- `summarize the last note of issue 42` → 42, `last`
- `resume la nota 3 del ticket 10` → 10, selector `3`
- `summarize the first note of ticket 5` → 5, `first`

Negation (`not`, `no`, `sin`, `don't`) still falls through to the LLM, same as today for ticket summaries.

### Prompt rule (router)

- Whole ticket / issue / descripción → `summary` with `issue_id` only.
- One existing note / journal / comentario → `summary_note`.
- Adding text onto a ticket → `note` (write). Never use `note` to summarize.

### Note selection

`get_issue` already includes `journals`. Keep journals whose `notes` strip to non-empty. Ignore empty status-only journals.

### Tests

- Extend `tests/test_nl_fastpath.py` with the phrases above.
- Unit-test `select_journal_note` with a fake issue dict: empty notes skipped, last/first/index, index past the end returns None.
- Router parse test: `summary_note` accepts `issue_id` + `selector` `last` and rejects `selector` `bogus`.

Python 3.11+. Run `.venv/bin/pytest -q tests/test_nl_fastpath.py tests/test_nl_router.py` plus any new test module.

## 5. Testing instructions

Automated (no Redmine network):

```bash
cd /root/Repos/ultron-redmine
.venv/bin/pytest -q tests/test_nl_fastpath.py tests/test_nl_router.py tests/test_textutil.py tests/test_summary_note.py
```

Expect pass. `tests/test_summary_note.py` checks the LLM user prompt is one note (no description, no other journal) and that an out-of-range selector raises `JournalNoteNotFound` with the note count and does not call the model.

Manual (whitelisted Discord user, NL routing on, a ticket that has at least two non-empty journal notes):

1. `@Ultron resume la nota del ticket <id>` — reply summarizes only the latest note, not the description or earlier notes.
2. `@Ultron summarize the first note of ticket <id>` — oldest note with text only.
3. `@Ultron resume la nota 2 del ticket <id>` — second note with text (empty status-only journals do not count).
4. `@Ultron summarize ticket <id>` — still a whole-ticket summary.
5. `@Ultron resume la nota 99 del ticket <id>` — short English error that includes how many notes have text. No whole-ticket summary.
6. `@Ultron summarize note 123` (no `ticket` / `issue` / `#`) — not a fast-path summary of issue 123.

## Test report

- **Date/time (UTC):** 2026-10-16T03:33:53Z start → 2026-10-16T03:35:02Z end
- **Environment:** branch `main` @ `9a914a1`, `.venv` Python 3.13.5, pytest via `.venv/bin/pytest`. Working tree still has the uncommitted note-summary implementation (not edited by this tester).

### What was tested

Automated suite from the testing instructions (no Redmine network):

```bash
.venv/bin/pytest -q tests/test_nl_fastpath.py tests/test_nl_router.py tests/test_textutil.py tests/test_summary_note.py
```

Source read for prompt text, fast-path order, router/planner wording, and Discord dispatch. Live Discord steps 1–6 were not exercised (no whitelisted session in this run).

### Results

| Criterion | Result | Evidence |
|-----------|--------|----------|
| `summary_note` summarizes one journal with non-empty notes | **PASS** | `summarize_journal_note` uses `select_journal_note`; `tests/test_summary_note.py::test_summarize_journal_note_prompt_is_one_note` |
| LLM user prompt is that note plus one-line context; no description or other journal | **PASS** | `format_single_journal_note` in `ultron/textutil.py`; test asserts `FIRST-NOTE` and `Journal id: 2`, rejects `SECRET-DESC-SHOULD-NOT-APPEAR` and `LAST-NOTE` |
| System prompt is note-only | **PASS** | `SUMMARY_NOTE_SYSTEM` (“Summarize that note only…”); same test asserts that sentence |
| Fast-path: note phrases → `summary_note`; whole ticket → `summary` | **PASS** | `test_summary_note_fastpath_phrases`, `test_whole_ticket_summary_phrases_stay_summary`; note path runs before the short summary fallback |
| Router and planner document the split; `note` stays a write | **PASS** | `NL_ROUTER_SYSTEM` and `NL_PLANNER_SYSTEM`: whole ticket → `summary`, one note → `summary_note`, add text → `note` |
| Missing / empty / out-of-range note is a short English error with the count; no whole-ticket fallback | **PASS** | `JournalNoteNotFound` “has {n} notes with text”; `test_summarize_journal_note_missing_does_not_call_llm` (`selector` `9`, “2 notes”, LLM user empty). Bot catches `JournalNoteNotFound` and replies with that string |
| Pytest covers fast-path phrases and a pure selector | **PASS** | `test_summary_note_fastpath_phrases`; `test_select_journal_note_skips_empty_and_indexes` (empty skipped, last/first/index, index past end is `None`) |
| No secrets in commits or task notes | **PASS** | No new commit; task notes and tests use fake note text only |
| `summarize note 123` is not fast-path issue 123 | **PASS** | `test_summarize_note_without_issue_marker_falls_through` returns `None` |
| Router accepts `selector` `last` and rejects `bogus` | **PASS** | `test_parse_router_summary_note_last`, `test_parse_router_summary_note_rejects_bogus_selector` |
| Live Discord phrases 1–6 | **not run** | No Discord client in this tester session |

**Pytest:** `41 passed in 1.40s` (15 + 15 + 9 + 2 collected).

### Overall: **PASS**

Operator feedback: Automated checks match the acceptance criteria: one-note prompts, fast-path split, and out-of-range errors that do not call the model. Live Discord still needs a whitelisted user on a ticket with at least two non-empty notes before operators treat the chat path as confirmed. The implementation remains uncommitted on `main`.
