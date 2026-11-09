"""
Workspace MCP Server.
Provides MCP tools for:
- Free calendar availability discovery
- Creating tentative calendar interview holds
- Creating email drafts
Operates against a robust, persistent local workspace mock.
"""
import os
import json
import uuid
from datetime import datetime, timedelta
from typing import Any, Optional
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Workspace", dependencies=["pydantic"])

WORKSPACE_STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "workspace_data.json")

def load_workspace_data() -> dict[str, Any]:
    if os.path.exists(WORKSPACE_STATE_FILE):
        try:
            with open(WORKSPACE_STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "calendar_holds": [],
        "email_drafts": []
    }

def save_workspace_data(data: dict[str, Any]):
    with open(WORKSPACE_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

@mcp.tool(
    name="get_free_calendar_slots",
    description="Check freelancer calendar availability and return a list of free interview slots in ISO 8601 format."
)
def tool_get_free_calendar_slots(days_ahead: int = 5, duration_minutes: int = 30) -> list[str]:
    """Generates standard available morning and afternoon time windows for upcoming weekdays."""
    slots = []
    base_time = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    for day in range(1, days_ahead + 1):
        candidate_day = base_time + timedelta(days=day)
        # Weekdays only (Monday = 0, Friday = 4)
        if candidate_day.weekday() < 5:
            # Morning slot: 10:00 AM UTC
            slot_morning = candidate_day.replace(hour=10, minute=0).isoformat() + "Z"
            # Afternoon slot: 3:00 PM UTC
            slot_afternoon = candidate_day.replace(hour=15, minute=0).isoformat() + "Z"
            slots.extend([slot_morning, slot_afternoon])
    return slots[:6]

@mcp.tool(
    name="create_tentative_interview_hold",
    description="Create a tentative calendar hold for a prospective client interview."
)
def tool_create_tentative_hold(title: str, slot: str, client_name: str) -> dict[str, Any]:
    data = load_workspace_data()
    hold_id = f"cal-hold-{uuid.uuid4().hex[:8]}"
    hold = {
        "hold_id": hold_id,
        "title": title,
        "slot": slot,
        "client_name": client_name,
        "status": "tentative",
        "created_at": datetime.utcnow().isoformat()
    }
    data["calendar_holds"].append(hold)
    save_workspace_data(data)
    return hold

@mcp.tool(
    name="create_email_draft",
    description="Create a draft email in the freelancer's workspace inbox for manual review."
)
def tool_create_email_draft(recipient: str, subject: str, body: str) -> dict[str, Any]:
    data = load_workspace_data()
    draft_id = f"email-draft-{uuid.uuid4().hex[:8]}"
    draft = {
        "draft_id": draft_id,
        "recipient": recipient,
        "subject": subject,
        "body": body,
        "status": "draft",
        "created_at": datetime.utcnow().isoformat()
    }
    data["email_drafts"].append(draft)
    save_workspace_data(data)
    return draft

if __name__ == "__main__":
    mcp.run()
