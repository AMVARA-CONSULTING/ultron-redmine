from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable

from ultron.llm import ChainSkipCallback, LLMBackend
from ultron.llm_cursor_fallback import llm_chain_client
from ultron.readlog import log_read_payload
from ultron.redmine import IssueNotFound, RedmineClient
from ultron.textutil import format_issue_for_summary, format_issue_metadata_header
from ultron.workflow_log import wf_info

SUMMARY_SYSTEM = (
    "You summarize Redmine issues for a technical team. Be concise and actionable. "
    "Sections: context, status, blockers (if any), next steps. "
    "Same language as the ticket when obvious; else English. Keep under ~400 words."
)

ASK_ABOUT_ISSUE_SYSTEM = (
    "You answer questions about a Redmine issue. "
    "Use only the ticket text (description, metadata, journal notes). "
    "If information is missing, say so. Be concise. "
    "Same language as the question when obvious; else English."
)

NOTE_SYSTEM = (
    "You write the body of one Redmine journal note as plain text. "
    "Output ONLY that note text and nothing else (no preamble, no labels). "
    "Do not add a byline or a 'Note written by … from Discord' line; the application prepends that after generation. "
    "Never repeat or quote the issue subject/title, issue number, project name, or tracker unless the user explicitly asked for them in their message. "
    "If the user asks a direct question—including simple arithmetic—answer it inside the note. "
    "Preserve factual claims and names; improve clarity and professional tone. "
    "Do not invent information not implied by the user's text. "
    "Use markdown only if the user already used it."
)

logger = logging.getLogger(__name__)

# Step tags: FETCH = Redmine read + prompt built, LLM_CALL / LLM_DONE = model boundary,
# REDMINE_WRITE = journal update. Lines are prefixed with WORKFLOW | … via wf_info.
_WF_FETCH = "FETCH"
_WF_LLM_CALL = "LLM_CALL"
_WF_LLM_DONE = "LLM_DONE"
_WF_REDMINE_WRITE = "REDMINE_WRITE"


def _llm_complete_kwargs(
    *,
    start_provider: str | None,
    model_override: str | None,
) -> dict[str, str | None]:
    return {"start_provider": start_provider, "model_override": model_override}


def _memory_prefix(memory_block: str | None) -> str:
    """Optional standing-user-prefs block prepended to LLM user prompts."""
    block = (memory_block or "").strip()
    if not block:
        return ""
    return f"{block}\n\n---\n\n"


async def summarize_issue(
    *,
    redmine: RedmineClient,
    llm: LLMBackend,
    issue_id: int,
    log_read_messages: bool = False,
    on_before_llm: Callable[[str], Awaitable[None]] | None = None,
    on_llm_chain_skip: ChainSkipCallback | None = None,
    issue_metadata_header: bool = True,
    start_provider: str | None = None,
    model_override: str | None = None,
    llm_display_model: str | None = None,
    memory_block: str | None = None,
) -> str:
    """Fetch a Redmine issue and ask the LLM for a concise summary."""
    issue = await redmine.get_issue(issue_id)
    meta = format_issue_metadata_header(issue) if issue_metadata_header else ""
    body = format_issue_for_summary(issue)
    ticket_block = f"{meta}\n\n{body}" if meta else body
    user_prompt = (
        f"{_memory_prefix(memory_block)}"
        f"Summarize this Redmine ticket as requested by a teammate.\n\n{ticket_block}"
    )
    if log_read_messages:
        log_read_payload(label=f"summary.issue_id={issue_id}.formatted_body", text=ticket_block)
        log_read_payload(label=f"summary.issue_id={issue_id}.llm_system", text=SUMMARY_SYSTEM)
        log_read_payload(label=f"summary.issue_id={issue_id}.llm_user", text=user_prompt)
    wf_info(
        logger,
        "summarize_issue",
        _WF_FETCH,
        "issue_id=%s prompt_chars=%s",
        issue_id,
        len(user_prompt),
    )
    wf_info(logger, "summarize_issue", _WF_LLM_CALL, "issue_id=%s", issue_id)
    if isinstance(llm_display_model, str) and llm_display_model.strip():
        display = llm_display_model.strip()
    else:
        chain = llm_chain_client(llm)
        display = chain.display_model_for_start(start_provider) if chain is not None else llm.model
    if on_before_llm is not None:
        await on_before_llm(display)
    kw = _llm_complete_kwargs(start_provider=start_provider, model_override=model_override)
    chain = llm_chain_client(llm)
    if chain is not None and on_llm_chain_skip is not None:
        out = await llm.complete(
            system=SUMMARY_SYSTEM,
            user=user_prompt,
            on_chain_skip=on_llm_chain_skip,
            **kw,
        )
    else:
        out = await llm.complete(system=SUMMARY_SYSTEM, user=user_prompt, **kw)
    wf_info(
        logger,
        "summarize_issue",
        _WF_LLM_DONE,
        "issue_id=%s response_chars=%s",
        issue_id,
        len(out),
    )
    if meta:
        return f"{meta}\n\n{out.strip()}"
    return out


async def ask_about_issue(
    *,
    redmine: RedmineClient,
    llm: LLMBackend,
    issue_id: int,
    question: str,
    log_read_messages: bool = False,
    on_before_llm: Callable[[str], Awaitable[None]] | None = None,
    on_llm_chain_skip: ChainSkipCallback | None = None,
    issue_metadata_header: bool = True,
    start_provider: str | None = None,
    model_override: str | None = None,
    llm_display_model: str | None = None,
    memory_block: str | None = None,
) -> str:
    """Answer a question about one Redmine issue using only ticket text."""
    issue = await redmine.get_issue(issue_id)
    meta = format_issue_metadata_header(issue) if issue_metadata_header else ""
    body = format_issue_for_summary(issue)
    ticket_block = f"{meta}\n\n{body}" if meta else body
    user_prompt = (
        f"{_memory_prefix(memory_block)}"
        f"Teammate question:\n{question}\n\n---\nRedmine ticket:\n{ticket_block}"
    )
    if log_read_messages:
        log_read_payload(label=f"ask_issue.issue_id={issue_id}.formatted_body", text=ticket_block)
        log_read_payload(label=f"ask_issue.issue_id={issue_id}.llm_system", text=ASK_ABOUT_ISSUE_SYSTEM)
        log_read_payload(label=f"ask_issue.issue_id={issue_id}.llm_user", text=user_prompt)
    wf_info(
        logger,
        "ask_about_issue",
        _WF_FETCH,
        "issue_id=%s prompt_chars=%s",
        issue_id,
        len(user_prompt),
    )
    wf_info(logger, "ask_about_issue", _WF_LLM_CALL, "issue_id=%s", issue_id)
    if isinstance(llm_display_model, str) and llm_display_model.strip():
        display = llm_display_model.strip()
    else:
        chain = llm_chain_client(llm)
        display = chain.display_model_for_start(start_provider) if chain is not None else llm.model
    if on_before_llm is not None:
        await on_before_llm(display)
    kw = _llm_complete_kwargs(start_provider=start_provider, model_override=model_override)
    if llm_chain_client(llm) is not None and on_llm_chain_skip is not None:
        out = await llm.complete(
            system=ASK_ABOUT_ISSUE_SYSTEM,
            user=user_prompt,
            on_chain_skip=on_llm_chain_skip,
            **kw,
        )
    else:
        out = await llm.complete(system=ASK_ABOUT_ISSUE_SYSTEM, user=user_prompt, **kw)
    wf_info(
        logger,
        "ask_about_issue",
        _WF_LLM_DONE,
        "issue_id=%s response_chars=%s",
        issue_id,
        len(out),
    )
    if meta:
        return f"{meta}\n\n{out.strip()}"
    return out


def _note_body_with_author(*, author_label: str | None, formatted: str) -> str:
    """Prefix italic attribution line before LLM body (Discord-style `_…_`)."""
    if not author_label or not author_label.strip():
        return formatted
    who = author_label.strip()
    header = f"_Note written by {who} from Discord_"
    return f"{header}\n\n{formatted}"


async def polish_note_text(
    *,
    llm: LLMBackend,
    issue_id: int,
    raw_text: str,
    log_read_messages: bool = False,
    on_llm_chain_skip: ChainSkipCallback | None = None,
    start_provider: str | None = None,
    model_override: str | None = None,
) -> str:
    """LLM-polish user text into a journal note body (no Redmine write)."""
    user_prompt = (
        "Transform the following user text into the final journal note content only.\n\n"
        + raw_text
    )
    if log_read_messages:
        log_read_payload(label=f"note.issue_id={issue_id}.discord_text", text=raw_text)
        log_read_payload(label=f"note.issue_id={issue_id}.llm_system", text=NOTE_SYSTEM)
        log_read_payload(label=f"note.issue_id={issue_id}.llm_user", text=user_prompt)
    wf_info(
        logger,
        "polish_note_text",
        _WF_FETCH,
        "issue_id=%s prompt_chars=%s",
        issue_id,
        len(user_prompt),
    )
    wf_info(logger, "polish_note_text", _WF_LLM_CALL, "issue_id=%s", issue_id)
    kw = _llm_complete_kwargs(start_provider=start_provider, model_override=model_override)
    if llm_chain_client(llm) is not None and on_llm_chain_skip is not None:
        formatted = await llm.complete(
            system=NOTE_SYSTEM,
            user=user_prompt,
            on_chain_skip=on_llm_chain_skip,
            **kw,
        )
    else:
        formatted = await llm.complete(system=NOTE_SYSTEM, user=user_prompt, **kw)
    wf_info(
        logger,
        "polish_note_text",
        _WF_LLM_DONE,
        "issue_id=%s response_chars=%s",
        issue_id,
        len(formatted),
    )
    if not formatted:
        raise RuntimeError("LLM returned an empty note")
    return formatted


async def add_formatted_note(
    *,
    redmine: RedmineClient,
    llm: LLMBackend,
    issue_id: int,
    raw_text: str,
    log_read_messages: bool = False,
    on_llm_chain_skip: ChainSkipCallback | None = None,
    note_author_label: str | None = None,
    start_provider: str | None = None,
    model_override: str | None = None,
    skip_post: bool = False,
) -> tuple[str, str]:
    """Polish note text and optionally post it.

    Returns (note_body, issue_url). When ``skip_post`` is True, only polishes
    (caller confirms, then posts via ``redmine.add_note``). Raises IssueNotFound
    if the issue is missing.
    """
    await redmine.get_issue(issue_id, includes="journals")
    url = redmine.issue_url(issue_id)
    formatted = await polish_note_text(
        llm=llm,
        issue_id=issue_id,
        raw_text=raw_text,
        log_read_messages=log_read_messages,
        on_llm_chain_skip=on_llm_chain_skip,
        start_provider=start_provider,
        model_override=model_override,
    )
    posted = _note_body_with_author(author_label=note_author_label, formatted=formatted)
    if skip_post:
        return posted, url
    await redmine.add_note(issue_id, posted)
    wf_info(
        logger,
        "add_formatted_note",
        _WF_REDMINE_WRITE,
        "issue_id=%s note_chars=%s",
        issue_id,
        len(posted),
    )
    return posted, url
