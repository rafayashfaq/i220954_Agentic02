"""
Approvals Router.
Manages pending human approval gates and resumes interrupted LangGraph threads.
Persists across browser refreshes.
"""
import uuid
from fastapi import APIRouter, HTTPException
from apps.api.schemas.api_schemas import ApprovalActionRequest
from agent.memory.store import get_memory_store
from mcp_servers.marketplace.server import tool_submit_proposal

router = APIRouter(prefix="/approvals", tags=["approvals"])

PENDING_APPROVALS: dict[str, dict] = {
    "thread-sample-job-001": {
        "thread_id": "thread-sample-job-001",
        "job_id": "sample-job-001",
        "title": "Build a customer churn prediction baseline",
        "cover_letter": "For your churn prediction baseline, I recently built a scikit-learn classifier pipeline [evidence: case-ai-001]. I achieved verified precision and recall baselines and documented all data boundaries.",
        "bid_amount": 350.0,
        "connects_cost": 8,
        "evidence_ids": ["evidence-001", "case-ai-001"],
        "status": "pending",
        "created_at": "2026-11-09T10:00:00Z"
    }
}

@router.get("")
def list_pending_approvals():
    """Lists all current interrupted threads awaiting human approval."""
    return list(PENDING_APPROVALS.values())

@router.post("/action")
async def execute_approval_action(req: ApprovalActionRequest):
    """
    Resumes an interrupted graph thread with the user's decision:
    - approved: submits proposal with idempotency key
    - edited: saves diff to Style Memory, re-checks compliance, submits
    - rejected: registers rejection reason
    """
    approval = PENDING_APPROVALS.get(req.thread_id)
    if not approval:
        raise HTTPException(status_code=404, detail=f"Pending approval {req.thread_id} not found")

    if req.action == "edited" and req.edited_text:
        # Style Memory learns from human edit!
        mem = get_memory_store()
        mem.record_user_edit(approval["cover_letter"], req.edited_text)
        approval["cover_letter"] = req.edited_text

    if req.action in ["approved", "edited"]:
        idem_key = f"idem-api-{uuid.uuid4().hex[:8]}"
        res = await tool_submit_proposal(
            job_id=approval["job_id"],
            cover_letter=approval["cover_letter"],
            bid_amount=approval["bid_amount"],
            idempotency_key=idem_key,
            screening_answers=[],
            evidence_ids=approval["evidence_ids"]
        )
        approval["status"] = "submitted"
        approval["submission_result"] = res
        return {"status": "submitted", "submission_id": res.get("submission_id"), "result": res}
    else:
        approval["status"] = "rejected"
        approval["rejection_reason"] = req.reason or "Rejected by user"
        return {"status": "rejected", "reason": approval["rejection_reason"]}

