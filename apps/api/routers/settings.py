"""
Settings & Long-Term Memory Management Router.
Allows configuring autonomy level, weekly Connects budgets, saved searches,
and inspecting or deleting learned Style Memory rules.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from apps.api.schemas.api_schemas import SettingsResponse
from agent.memory.store import get_memory_store

router = APIRouter(prefix="/settings", tags=["settings"])

SYSTEM_SETTINGS = {
    "autonomy_level": "auto_skip_only",
    "weekly_budget": 80,
    "saved_searches": [
        "Python LangGraph RAG",
        "Next.js Tailwind TypeScript",
        "dbt Snowflake BigQuery",
        "FastAPI PostgreSQL Docker"
    ],
    "connected_accounts": [
        {"platform": "GigSim Simulator", "status": "connected", "type": "internal_simulator"},
        {"platform": "Upwork Official MCP", "status": "ready (live mode)", "type": "oauth2_pkce"},
        {"platform": "GitHub MCP", "status": "connected", "type": "personal_access_token"}
    ]
}

class UpdateSettingsRequest(BaseModel):
    autonomy_level: str
    weekly_budget: int

@router.get("", response_model=SettingsResponse)
def get_settings():
    mem = get_memory_store()
    style_rules = mem.state.get("style_rules", [])
    return SettingsResponse(
        autonomy_level=SYSTEM_SETTINGS["autonomy_level"],
        weekly_budget=SYSTEM_SETTINGS["weekly_budget"],
        saved_searches=SYSTEM_SETTINGS["saved_searches"],
        connected_accounts=SYSTEM_SETTINGS["connected_accounts"],
        style_memory_rules=style_rules
    )

@router.post("")
def update_settings(req: UpdateSettingsRequest):
    SYSTEM_SETTINGS["autonomy_level"] = req.autonomy_level
    SYSTEM_SETTINGS["weekly_budget"] = req.weekly_budget
    return {"status": "updated", "settings": SYSTEM_SETTINGS}

@router.delete("/memory/{rule_id}")
def delete_memory_rule(rule_id: str):
    """Deletes a learned style memory rule from the persistent store."""
    mem = get_memory_store()
    deleted = mem.delete_rule(rule_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Rule {rule_id} not found in memory store.")
    return {"status": "deleted", "rule_id": rule_id}

