"""
GigSim: Deterministic freelance marketplace simulator for AI-4016 GigBid assignment.
Provides a REST API (FastAPI) and in-process Python client simulating Upwork/GigSim platform.
Includes simulated clients with hidden preferences and LLM/heuristic decision logic.
"""
import os
import json
import uuid
import time
from typing import Any, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, Header, Depends, Query, status
from pydantic import BaseModel, Field

app = FastAPI(title="GigSim Marketplace Simulator", version="1.0.0")

# Storage paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "data")
SAMPLE_DIR = os.path.join(DATA_DIR, "sample")
JOBS_FILE = os.path.join(SAMPLE_DIR, "jobs.json")
CLIENTS_FILE = os.path.join(SAMPLE_DIR, "client_history.json")

# In-memory simulator state
state = {
    "jobs": {},
    "clients": {},
    "proposals": {},
    "connects": {"balance": 80, "history": []},
    "messages": [],
    "idempotency_keys": set(),
    "audit_log": [],
    "rate_limits": {},
    "error_mode": None,  # None, "503", "429"
}

def load_seed_data():
    """Load seed jobs and clients into memory."""
    if os.path.exists(JOBS_FILE):
        with open(JOBS_FILE, "r", encoding="utf-8") as f:
            for job in json.load(f):
                state["jobs"][job["job_id"]] = job
    
    # Also load from dev set if available
    dev_jobs_file = os.path.join(DATA_DIR, "processed", "jobs_stream.json")
    if os.path.exists(dev_jobs_file):
        with open(dev_jobs_file, "r", encoding="utf-8") as f:
            for job in json.load(f):
                state["jobs"][job["job_id"]] = job

    if os.path.exists(CLIENTS_FILE):
        with open(CLIENTS_FILE, "r", encoding="utf-8") as f:
            for client in json.load(f):
                state["clients"][client["client_id"]] = client

load_seed_data()

# Models
class ProposalDraftRequest(BaseModel):
    job_id: str
    cover_letter: str
    bid_amount: float = Field(gt=0)
    screening_answers: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    dry_run: bool = False

class ProposalSubmitRequest(BaseModel):
    draft_id: Optional[str] = None
    job_id: str
    cover_letter: str
    bid_amount: float = Field(gt=0)
    screening_answers: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    idempotency_key: str

class MessageSendRequest(BaseModel):
    client_id: str
    thread_id: Optional[str] = None
    body: str
    proposed_slots: list[str] = Field(default_factory=list)
    idempotency_key: str

def check_rate_limit(client_id: str = "default_user"):
    now = time.time()
    history = state["rate_limits"].get(client_id, [])
    # 60 second sliding window
    history = [t for t in history if now - t < 60]
    if len(history) >= 60:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Maximum 60 requests per minute."
        )
    history.append(now)
    state["rate_limits"][client_id] = history

    if state["error_mode"] == "503":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GigSim marketplace server is currently degraded/unavailable."
        )
    if state["error_mode"] == "429":
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Simulated upstream rate limit reached."
        )

# Routes
@app.get("/health")
def health():
    return {"status": "ok", "mode": state["error_mode"] or "normal", "jobs_count": len(state["jobs"])}

@app.post("/admin/simulate_error")
def simulate_error(mode: Optional[str] = Query(None, description="None, 503, or 429")):
    state["error_mode"] = mode
    return {"message": f"Simulated error mode set to {mode}"}

@app.get("/jobs")
def get_jobs(query: Optional[str] = None, limit: int = 50):
    check_rate_limit()
    results = list(state["jobs"].values())
    if query:
        q = query.lower()
        results = [
            j for j in results
            if q in j.get("title", "").lower()
            or q in j.get("description", "").lower()
            or any(q in s.lower() for s in j.get("required_skills", []))
        ]
    return results[:limit]

@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    check_rate_limit()
    job = state["jobs"].get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return job

@app.get("/clients/{client_id}")
def get_client(client_id: str):
    check_rate_limit()
    client = state["clients"].get(client_id)
    if not client:
        # Default mock client history if not found
        return {
            "client_id": client_id,
            "completed_projects": 4,
            "average_rating": 4.9,
            "payment_verified": True,
            "total_spent_usd": 12500,
            "notes": "Verified client with consistent payment track record."
        }
    return client

@app.get("/connects")
def get_connects():
    check_rate_limit()
    return state["connects"]

@app.post("/proposals/draft")
def create_draft(req: ProposalDraftRequest):
    check_rate_limit()
    job = state["jobs"].get(req.job_id)
    connects_cost = job.get("connects_cost", 6) if job else 6
    
    draft_id = f"draft-{uuid.uuid4().hex[:8]}"
    preview = {
        "draft_id": draft_id,
        "job_id": req.job_id,
        "bid_amount": req.bid_amount,
        "connects_required": connects_cost,
        "user_balance_after": max(0, state["connects"]["balance"] - connects_cost),
        "cover_letter_preview": req.cover_letter[:150] + "...",
        "evidence_ids": req.evidence_ids,
        "dry_run": req.dry_run,
        "ready_for_submission": True
    }
    if not req.dry_run:
        state["proposals"][draft_id] = {
            "draft_id": draft_id,
            "payload": req.model_dump(),
            "status": "drafted",
            "created_at": datetime.utcnow().isoformat()
        }
    return preview

@app.post("/proposals/submit")
def submit_proposal(req: ProposalSubmitRequest):
    check_rate_limit()
    if req.idempotency_key in state["idempotency_keys"]:
        # Return existing proposal submission
        for p in state["proposals"].values():
            if p.get("idempotency_key") == req.idempotency_key:
                return p
        return {"status": "already_submitted", "idempotency_key": req.idempotency_key}

    job = state["jobs"].get(req.job_id)
    connects_cost = job.get("connects_cost", 6) if job else 6
    if state["connects"]["balance"] < connects_cost:
        raise HTTPException(status_code=400, detail="Insufficient Connects balance")

    submission_id = f"sub-{uuid.uuid4().hex[:8]}"
    state["connects"]["balance"] -= connects_cost
    state["connects"]["history"].append({
        "action": "proposal_submit",
        "job_id": req.job_id,
        "amount": -connects_cost,
        "timestamp": datetime.utcnow().isoformat()
    })
    state["idempotency_keys"].add(req.idempotency_key)

    # Simulated client reaction logic
    reply_decision = evaluate_proposal_reaction(job, req.cover_letter, req.bid_amount, req.evidence_ids)

    submission = {
        "submission_id": submission_id,
        "job_id": req.job_id,
        "status": "submitted",
        "connects_spent": connects_cost,
        "remaining_balance": state["connects"]["balance"],
        "idempotency_key": req.idempotency_key,
        "submitted_at": datetime.utcnow().isoformat(),
        "simulated_outcome": reply_decision
    }
    state["proposals"][submission_id] = submission

    # If client replied, schedule a client message in the thread
    if reply_decision["replied"]:
        client_id = job.get("client_id", "sample-client-001") if job else "sample-client-001"
        thread_id = f"thread-{req.job_id}"
        state["messages"].append({
            "message_id": f"msg-{uuid.uuid4().hex[:8]}",
            "thread_id": thread_id,
            "client_id": client_id,
            "sender": "client",
            "body": reply_decision["message"],
            "timestamp": datetime.utcnow().isoformat(),
            "status": "received"
        })

    return submission

@app.get("/messages")
def get_messages(thread_id: Optional[str] = None):
    check_rate_limit()
    if thread_id:
        return [m for m in state["messages"] if m["thread_id"] == thread_id]
    return state["messages"]

@app.post("/messages")
def send_message(req: MessageSendRequest):
    check_rate_limit()
    if req.idempotency_key in state["idempotency_keys"]:
        return {"status": "duplicate_ignored", "idempotency_key": req.idempotency_key}
    
    state["idempotency_keys"].add(req.idempotency_key)
    msg_id = f"msg-{uuid.uuid4().hex[:8]}"
    msg = {
        "message_id": msg_id,
        "thread_id": req.thread_id or f"thread-{req.client_id}",
        "client_id": req.client_id,
        "sender": "freelancer",
        "body": req.body,
        "proposed_slots": req.proposed_slots,
        "timestamp": datetime.utcnow().isoformat(),
        "status": "sent"
    }
    state["messages"].append(msg)
    return {"status": "sent", "message": msg}

def evaluate_proposal_reaction(job: Optional[dict], cover_letter: str, bid: float, evidence_ids: list[str]) -> dict:
    """
    Simulated client evaluation engine:
    Checks budget ceiling, must-have skills, evidence citation, and penalizes generic openings.
    """
    if not job:
        return {"replied": True, "interview": True, "hire": False, "message": "Thanks for your proposal! Let's chat."}

    text = cover_letter.lower()
    budget = job.get("budget", {})
    b_max = budget.get("max", 500) if isinstance(budget, dict) else 500
    
    score = 0.5
    # Penalize generic boilerplate openings
    generic_openings = ["dear hiring manager", "i am excited to apply", "i am the perfect fit for this job", "i am writing to express my interest"]
    if any(open_phrase in text[:120] for open_phrase in generic_openings):
        score -= 0.35

    # Reward concrete evidence citations
    if evidence_ids or "evidence-" in text or "case study" in text or "github.com" in text:
        score += 0.25

    # Reward addressing required skills specifically
    req_skills = job.get("required_skills", [])
    matched_skills = [s for s in req_skills if s.lower() in text]
    skill_match_ratio = len(matched_skills) / max(1, len(req_skills))
    score += 0.3 * skill_match_ratio

    # Budget penalty if exceeding max budget
    if bid > b_max * 1.15:
        score -= 0.3

    replied = score >= 0.55
    interview = score >= 0.72
    hired = score >= 0.88

    if hired:
        msg = "We were impressed with your verified portfolio evidence. We'd like to extend an offer."
    elif interview:
        msg = f"Your approach looks solid, especially regarding {matched_skills[:2]}. Are you free for a quick 15-min sync this week?"
    elif replied:
        msg = "Hi, thank you for the detailed bid. Could you clarify your timeline for this deliverable?"
    else:
        msg = ""

    return {
        "score": round(score, 2),
        "replied": replied,
        "interview": interview,
        "hire": hired,
        "message": msg
    }

