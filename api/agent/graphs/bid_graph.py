"""
Bid Graph: LangGraph StateGraph orchestrating the freelance bidding pipeline.
Features:
- Scout ingestion
- Parallel execution of Job Analyst, Risk Assessor, and Fit Matcher
- Decision routing (skip, watch, bid) with budgets and dead-letter state
- Pricing Strategist, Proposal Writer, Claim Verification
- Bounded Critic loop (max 2 revisions)
- Compliance Guard enforcement
- Human approval interrupt (`interrupt()`) before submitting or spending Connects
- Durable SQLite checkpointing for crash-recovery and resume
"""
import os
import uuid
import sqlite3
from typing import Literal, Optional
from datetime import datetime

from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt
from langgraph.checkpoint.sqlite import SqliteSaver

from agent.state import BidGraphState
from agent.handoffs import BidDecision, ApprovalPayload
from agent.nodes.scout import scout_node
from agent.nodes.analyst import analyst_node
from agent.nodes.risk_assessor import risk_assessor_node
from agent.nodes.fit_matcher import fit_matcher_node
from agent.nodes.pricing import pricing_node
from agent.nodes.writer import writer_node
from agent.nodes.verifier import verifier_node
from agent.nodes.critic import critic_node
from agent.nodes.compliance import compliance_node
from agent.memory.store import get_memory_store
from mcp_servers.marketplace.server import tool_create_proposal_draft, tool_submit_proposal

CHECKPOINT_DB = os.path.join(
    "/tmp" if (os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME")) else os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "processed"),
    "bid_checkpoints.db"
)
try:
    os.makedirs(os.path.dirname(CHECKPOINT_DB), exist_ok=True)
except Exception:
    CHECKPOINT_DB = ":memory:"

# -------------------------------------------------------------
# Decision and Routing Nodes
# -------------------------------------------------------------
def decision_node(state: BidGraphState) -> dict:
    """Evaluates RiskReport and FitReport against configured thresholds to decide bid vs skip."""
    risk = state.get("risk_report")
    fit = state.get("fit_report")
    job = state.get("job", {})

    risk_score = risk.score if risk else 0.0
    fit_score = fit.score if fit else 0.5

    # Check budgets
    step_count = state.get("step_count", 0)
    token_count = state.get("token_count", 0)
    if step_count > 30 or token_count > 12000:
        return {
            "decision": BidDecision(action="skip", reason="Exceeded step or token budget", auto_skipped=True),
            "needs_attention": True,
            "attention_reason": "Thread exceeded budget limits."
        }

    # High risk or scam
    if risk_score >= 0.70 or (risk and risk.flags):
        reasons = risk.flags if risk else ["High risk"]
        return {
            "decision": BidDecision(action="skip", reason=f"Risk score {risk_score} with flags: {', '.join(reasons)}", auto_skipped=True)
        }

    # Low fit
    if fit_score < 0.50:
        return {
            "decision": BidDecision(action="skip", reason=f"Fit score {fit_score} below minimum 0.50 threshold", auto_skipped=True)
        }

    return {
        "decision": BidDecision(action="bid", reason=f"Strong fit ({fit_score}) and acceptable risk ({risk_score})")
    }

def route_after_decision(state: BidGraphState) -> Literal["pricing", "end"]:
    decision = state.get("decision")
    if decision and decision.action == "bid":
        return "pricing"
    return "end"

def route_after_critic(state: BidGraphState) -> Literal["writer", "compliance"]:
    critique = state.get("critique")
    revision_count = state.get("revision_count", 0)
    if critique and critique.requires_rewrite and revision_count < 2:
        return "writer"
    return "compliance"

async def prepare_approval_node(state: BidGraphState) -> dict:
    """Performs dry-run preview and packages the approval payload."""
    job = state.get("job", {})
    draft = state.get("proposal_draft")
    quote = state.get("price_quote")
    risk = state.get("risk_report")
    evidence = state.get("evidence", [])

    job_id = job.get("job_id", "sample-job")
    bid_amount = quote.proposed_bid if quote else 350.0
    cover = draft.cover_letter if draft else ""

    # Call dry_run tool to get preview and Connects impact
    dry_run_preview = await tool_create_proposal_draft(
        job_id=job_id,
        cover_letter=cover,
        bid_amount=bid_amount,
        screening_answers=draft.screening_answers if draft else [],
        evidence_ids=draft.evidence_ids if draft else [],
        dry_run=True
    )

    approval_payload = ApprovalPayload(
        thread_id=job_id,
        job_id=job_id,
        draft=draft,
        evidence_items=evidence,
        risk_report=risk,
        price_quote=quote,
        dry_run_preview=dry_run_preview,
        approval_status="pending"
    )

    return {
        "approval_payload": approval_payload,
        "approval_status": "pending"
    }

def human_approval_interrupt_node(state: BidGraphState) -> dict:
    """
    Interrupts graph execution to wait for human review in the Web UI.
    Carries the full draft, cited evidence, risk analysis, and dry-run cost preview.
    Resumes when human approves, edits, or rejects.
    """
    payload = state.get("approval_payload")
    # LangGraph interrupt
    human_response = interrupt({
        "type": "approval_required",
        "action": "submit_proposal",
        "payload": payload.model_dump() if payload else {}
    })

    # When resumed, human_response contains user's choice:
    # {"action": "approve"|"edit"|"reject", "edited_text": "...", "reason": "..."}
    status = human_response.get("action", "approved")
    edited_text = human_response.get("edited_text")
    user_reason = human_response.get("reason", "")

    updates = {"approval_status": status}

    if status == "edited" and edited_text and payload and payload.draft:
        # Style memory learns from diff!
        mem = get_memory_store()
        mem.record_user_edit(payload.draft.cover_letter, edited_text)
        
        # Update draft with human edit
        updated_draft = payload.draft.model_copy(update={"cover_letter": edited_text})
        updates["proposal_draft"] = updated_draft

    elif status == "rejected":
        updates["needs_attention"] = False
        updates["attention_reason"] = f"Rejected by user: {user_reason}"

    return updates

async def submit_proposal_node(state: BidGraphState) -> dict:
    """Submits the human-approved proposal to the marketplace with an idempotency key."""
    status = state.get("approval_status")
    if status not in ["approved", "edited"]:
        return {"submission_result": {"status": "skipped_or_rejected"}}

    job = state.get("job", {})
    draft = state.get("proposal_draft")
    quote = state.get("price_quote")
    job_id = job.get("job_id", "sample-job")
    bid_amount = quote.proposed_bid if quote else 350.0

    idempotency_key = f"idem-{job_id}-{uuid.uuid4().hex[:8]}"

    res = await tool_submit_proposal(
        job_id=job_id,
        cover_letter=draft.cover_letter if draft else "",
        bid_amount=bid_amount,
        idempotency_key=idempotency_key,
        screening_answers=draft.screening_answers if draft else [],
        evidence_ids=draft.evidence_ids if draft else []
    )

    # Record outcome promotion if client replied in simulation
    sim_outcome = res.get("simulated_outcome", {})
    if sim_outcome.get("replied") or sim_outcome.get("hire"):
        mem = get_memory_store()
        category = job.get("category", "Software Engineering")
        mem.record_outcome(
            category=category,
            bid=bid_amount,
            outcome="hired" if sim_outcome.get("hire") else "replied",
            evidence_ids=draft.evidence_ids if draft else []
        )

    return {
        "submission_result": res,
        "approval_status": "submitted"
    }

from langgraph.checkpoint.memory import MemorySaver

# -------------------------------------------------------------
# Graph Construction
# -------------------------------------------------------------
def build_bid_graph(checkpointer=None):
    """Builds and compiles the durable LangGraph Bid Graph."""
    builder = StateGraph(BidGraphState)

    # Add Nodes
    builder.add_node("scout", scout_node)
    builder.add_node("analyst", analyst_node)
    builder.add_node("risk_assessor", risk_assessor_node)
    builder.add_node("fit_matcher", fit_matcher_node)
    builder.add_node("decision_node", decision_node)
    builder.add_node("pricing", pricing_node)
    builder.add_node("writer", writer_node)
    builder.add_node("verifier", verifier_node)
    builder.add_node("critic", critic_node)
    builder.add_node("compliance", compliance_node)
    builder.add_node("prepare_approval", prepare_approval_node)
    builder.add_node("human_approval", human_approval_interrupt_node)
    builder.add_node("submit", submit_proposal_node)

    # Wire Edges
    builder.add_edge(START, "scout")

    # Parallel fan-out: Scout -> [Analyst, Risk Assessor, Fit Matcher]
    builder.add_edge("scout", "analyst")
    builder.add_edge("scout", "risk_assessor")
    builder.add_edge("scout", "fit_matcher")

    # Parallel fan-in: [Analyst, Risk Assessor, Fit Matcher] -> Decision Node
    builder.add_edge("analyst", "decision_node")
    builder.add_edge("risk_assessor", "decision_node")
    builder.add_edge("fit_matcher", "decision_node")

    # Conditional Branching after Decision
    builder.add_conditional_edges(
        "decision_node",
        route_after_decision,
        {"pricing": "pricing", "end": END}
    )

    # Proposal Generation Pipeline
    builder.add_edge("pricing", "writer")
    builder.add_edge("writer", "verifier")
    builder.add_edge("verifier", "critic")

    # Bounded Loop from Critic
    builder.add_conditional_edges(
        "critic",
        route_after_critic,
        {"writer": "writer", "compliance": "compliance"}
    )

    # Compliance Guard to Human-in-the-Loop Gate
    builder.add_edge("compliance", "prepare_approval")
    builder.add_edge("prepare_approval", "human_approval")
    builder.add_edge("human_approval", "submit")
    builder.add_edge("submit", END)

    cp = checkpointer if checkpointer is not None else MemorySaver()
    return builder.compile(checkpointer=cp)
