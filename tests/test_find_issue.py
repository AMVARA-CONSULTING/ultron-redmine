from __future__ import annotations

import asyncio

from ultron.nl_router import NLInvoke, NLParseError, parse_router_json_text
from ultron.redmine import RedmineClient
from ultron.redmine_listings import (
    crop_issue_subject,
    format_find_issue_detail_line,
    markdown_find_issues,
    parse_search_issue_hit,
)


def test_parse_search_issue_hit_standard_title() -> None:
    hit = {
        "id": 10,
        "title": "Issue #10 (Closed): Login failure on SSO",
        "type": "issue closed",
    }
    assert parse_search_issue_hit(hit) == (10, "Login failure on SSO")


def test_parse_search_issue_hit_skips_non_issue() -> None:
    hit = {"id": 5, "title": "Wiki: Page", "type": "wiki-page"}
    assert parse_search_issue_hit(hit) is None


def test_crop_issue_subject_fifteen_chars() -> None:
    assert crop_issue_subject("0123456789ABCDEF") == "0123456789ABCDE"
    assert len(crop_issue_subject("0123456789ABCDEF")) == 15


def test_format_find_issue_detail_line() -> None:
    client = RedmineClient(base_url="https://redmine.example.com", api_key="x")
    line = format_find_issue_detail_line(42, "Very long subject here", client)
    assert line.startswith("Very long subje ")
    assert "[#42](https://redmine.example.com/issues/42)" in line


def test_parse_router_invoke_find_issue() -> None:
    raw = '{"kind":"invoke","command":"find_issue","args":{"text":"sso login"}}'
    out = parse_router_json_text(raw)
    assert isinstance(out, NLInvoke)
    assert out.command == "find_issue"
    assert out.args == {"text": "sso login"}


def test_parse_router_find_issue_alias_search_issue() -> None:
    raw = '{"kind":"invoke","command":"search_issue","args":{"text":"foo"}}'
    out = parse_router_json_text(raw)
    assert isinstance(out, NLInvoke)
    assert out.command == "find_issue"


def test_parse_router_find_issue_rejects_empty_text() -> None:
    raw = '{"kind":"invoke","command":"find_issue","args":{"text":"  "}}'
    out = parse_router_json_text(raw)
    assert isinstance(out, NLParseError)


def _amvara_projects() -> list[dict]:
    """Display name 10_AMVARA maps to identifier amvara-general (live Redmine shape)."""
    return [{"id": 2, "identifier": "amvara-general", "name": "10_AMVARA"}]


def test_markdown_find_issues_empty(monkeypatch) -> None:
    client = RedmineClient(base_url="https://redmine.example.com", api_key="x")

    async def _projects():
        return _amvara_projects()

    async def _collect(query, *, project_id, max_results=200):
        assert project_id == "amvara-general"
        return [], 0

    monkeypatch.setattr(client, "list_projects", _projects)
    monkeypatch.setattr(client, "search_issues_collect", _collect)

    async def _run():
        return await markdown_find_issues(
            redmine=client, text="xyzzy", project_id="10_AMVARA"
        )

    body, err, total = asyncio.run(_run())
    assert err is None
    assert total == 0
    assert body is not None
    assert "No issues matching" in body
    assert "amvara-general" in body


def test_markdown_find_issues_overflow(monkeypatch) -> None:
    client = RedmineClient(base_url="https://redmine.example.com", api_key="x")
    hits = [
        {
            "id": i,
            "title": f"Issue #{i} (New): Subject number {i}",
            "type": "issue",
        }
        for i in range(1, 26)
    ]

    async def _projects():
        return _amvara_projects()

    async def _collect(query, *, project_id, max_results=200):
        assert project_id == "amvara-general"
        return hits, 25

    monkeypatch.setattr(client, "list_projects", _projects)
    monkeypatch.setattr(client, "search_issues_collect", _collect)

    async def _run():
        return await markdown_find_issues(
            redmine=client, text="Subject", project_id="10_AMVARA"
        )

    body, err, total = asyncio.run(_run())
    assert err is None
    assert total == 25
    assert body is not None
    assert "Also matching:" in body
    assert "[#21](https://redmine.example.com/issues/21)" in body
    assert "Subject number 21" not in body
    assert body.count("\n") >= 20
    assert "10\\_AMVARA" in body or "10_AMVARA" in body
    assert "amvara-general" in body


def test_markdown_find_issues_resolves_display_name(monkeypatch) -> None:
    """Config default 10_AMVARA is the display name; search must use identifier."""
    client = RedmineClient(base_url="https://redmine.example.com", api_key="x")
    seen: dict[str, str] = {}

    async def _projects():
        return _amvara_projects()

    async def _collect(query, *, project_id, max_results=200):
        seen["project_id"] = project_id
        seen["query"] = query
        return [
            {
                "id": 7127,
                "title": "Issue #7127 (New): Discussion with Ralf",
                "type": "issue",
            }
        ], 1

    monkeypatch.setattr(client, "list_projects", _projects)
    monkeypatch.setattr(client, "search_issues_collect", _collect)

    async def _run():
        return await markdown_find_issues(
            redmine=client, text="Icinga", project_id="10_AMVARA"
        )

    body, err, total = asyncio.run(_run())
    assert err is None
    assert total == 1
    assert seen["project_id"] == "amvara-general"
    assert seen["query"] == "Icinga"
    assert body is not None
    assert "7127" in body


def test_markdown_find_issues_unknown_project(monkeypatch) -> None:
    client = RedmineClient(base_url="https://redmine.example.com", api_key="x")

    async def _projects():
        return _amvara_projects()

    monkeypatch.setattr(client, "list_projects", _projects)

    async def _run():
        return await markdown_find_issues(
            redmine=client, text="Icinga", project_id="no-such-project"
        )

    body, err, total = asyncio.run(_run())
    assert body is None
    assert total == -1
    assert err is not None
    assert "No Redmine project matching" in err
