"""
Typed State Definitions for GigBid Multi-Agent Graphs.
Enforces strict separation between:
1. State: ephemeral working context required right now for routing and generation.
2. Execution Trace: complete record of tool names, arguments, observations, and node transitions for auditability.
3. Long-term Memory: promoted durable insights managed via LangGraph store with explicit promotion rules.
"""
import operator
from typing import Annotated, Any, Optional, TypedDict
from agent.handoffs import (
    JobSpec, RiskReport, FitReport, BidDecision, PriceQuote,
    ProposalDraft, Critique, ComplianceVerdict, ApprovalPayload, ConversationIntent
)

def merge_dicts(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    """Reducer for updating dictionary state across parallel branches."""
    res = dict(left) if left else {}
    if right:
        res.update(right)
    return res

class ExecutionTraceItem(TypedDict):
    node: str
    tool: Optional[str]
    input: Any
    output: Any
    timestamp: str

class BidGraphState(TypedDict, total=False):
    # Core job context
    job: dict[str, Any]
    persona_key: str
    
    # Parallel Analysis Branches (Job Analyst, Risk Assessor, Fit Matcher)
    job_spec: Optional[JobSpec]
    risk_report: Optional[RiskReport]
    fit_report: Optional[FitReport]
    
    # Evidence & Routing Decision
    evidence: list[dict[str, Any]]
    decision: Optional[BidDecision]
    
    # Downstream generation & verification
    price_quote: Optional[PriceQuote]
    proposal_draft: Optional[ProposalDraft]
    claim_verification: Optional[dict[str, Any]]
    critique: Optional[Critique]
    compliance_verdict: Optional[ComplianceVerdict]
    
    # Budgets & loop counters
    revision_count: int
    step_count: int
    token_count: int
    needs_attention: bool
    attention_reason: Optional[str]
    
    # Human in the Loop Approval
    approval_payload: Optional[ApprovalPayload]
    approval_status: str  # pending, approved, rejected, edited
    submission_result: Optional[dict[str, Any]]
    
    # Reducers for parallel branch accumulation and audit traces
    execution_traces: Annotated[list[dict[str, Any]], operator.add]
    errors: Annotated[list[str], operator.add]

class ConversationGraphState(TypedDict, total=False):
    # Incoming message context
    client_id: str
    thread_id: str
    messages: list[dict[str, Any]]
    
    # Agent analysis & drafting
    intent: Optional[ConversationIntent]
    proposed_reply: Optional[str]
    proposed_interview_slots: list[str]
    
    # Human approval gate
    approval_status: str
    final_message_sent: Optional[dict[str, Any]]
    
    # Traces and errors
    execution_traces: Annotated[list[dict[str, Any]], operator.add]
    errors: Annotated[list[str], operator.add]
