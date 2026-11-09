"""
Messages Router.
Manages client conversation threads, AI-suggested responses, interview scheduling, and message approvals.
"""
import uuid
from fastapi import APIRouter, HTTPException
from typing import Optional
from apps.api.schemas.api_schemas import MessageThread, SendMessageRequest
from mcp_servers.workspace.server import tool_get_free_calendar_slots, tool_create_tentative_hold
from mcp_servers.marketplace.server import tool_send_message

router = APIRouter(prefix="/messages", tags=["messages"])

THREADS: dict[str, dict] = {
    "thread-sample-client-001": {
        "thread_id": "thread-sample-client-001",
        "client_id": "sample-client-001",
        "messages": [
            {
                "sender": "client",
                "body": "Hi Alex! We reviewed your proposal and case study for the churn model. Are you available for a 15-min technical sync this Wednesday or Thursday?",
                "timestamp": "2026-11-09T09:15:00Z"
            }
        ],
        "suggested_reply": "Hi! Thank you for reviewing my proposal. I would be glad to connect. I have tentative openings at 10:00 AM UTC or 3:00 PM UTC on Wednesday.",
        "suggested_interview_slots": [
            "2026-11-11T10:00:00Z",
            "2026-11-11T15:00:00Z"
        ],
        "status": "awaiting_approval"
    }
}

@router.get("", response_model=list[MessageThread])
def list_threads():
    return [MessageThread(**t) for t in THREADS.values()]

@router.get("/{thread_id}", response_model=MessageThread)
def get_thread(thread_id: str):
    t = THREADS.get(thread_id)
    if not t:
        raise HTTPException(status_code=404, detail=f"Thread {thread_id} not found")
    return MessageThread(**t)

@router.post("/{thread_id}/send")
async def send_client_reply(thread_id: str, req: SendMessageRequest):
    t = THREADS.get(thread_id)
    if not t:
        raise HTTPException(status_code=404, detail=f"Thread {thread_id} not found")

    idem_key = f"msg-api-{uuid.uuid4().hex[:8]}"
    res = await tool_send_message(
        client_id=req.client_id,
        body=req.body,
        idempotency_key=idem_key,
        proposed_slots=req.proposed_slots,
        thread_id=thread_id
    )

    t["messages"].append({
        "sender": "freelancer",
        "body": req.body,
        "proposed_slots": req.proposed_slots,
        "timestamp": "2026-11-09T10:30:00Z"
    })
    t["status"] = "replied"
    return {"status": "sent", "result": res}

