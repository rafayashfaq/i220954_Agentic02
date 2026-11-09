"""
Unit tests for Workspace MCP server.
"""
from mcp_servers.workspace.server import (
    tool_get_free_calendar_slots,
    tool_create_tentative_hold,
    tool_create_email_draft
)

def test_get_free_calendar_slots():
    slots = tool_get_free_calendar_slots(days_ahead=3)
    assert isinstance(slots, list)
    assert len(slots) > 0
    assert "T" in slots[0]

def test_create_tentative_hold():
    res = tool_create_tentative_hold(
        title="Technical Discovery Call",
        slot="2026-11-12T10:00:00Z",
        client_name="Acme Health"
    )
    assert res["status"] == "tentative"
    assert "cal-hold-" in res["hold_id"]

def test_create_email_draft():
    res = tool_create_email_draft(
        recipient="hiring@techcorp.com",
        subject="Clarification regarding deliverable timeline",
        body="Hi, I reviewed your project scope..."
    )
    assert res["status"] == "draft"
    assert "email-draft-" in res["draft_id"]

