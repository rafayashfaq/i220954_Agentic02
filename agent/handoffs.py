"""
Structured Hand-offs for Multi-Agent Orchestration.
All inter-agent communication uses strongly-typed Pydantic models.
"""
from typing import Optional, Any, Literal
from pydantic import BaseModel, Field

class JobSpec(BaseModel):
    job_id: str
    title: str
    deliverables: list[str] = Field(default_factory=list, description="Extracted discrete deliverables")
    required_skills: list[str] = Field(default_factory=list, description="Explicit technical skills required")
    implied_skills: list[str] = Field(default_factory=list, description="Implied competencies from problem description")
    budget_min: float = Field(default=0.0)
    budget_max: float = Field(default=0.0)
    currency: str = Field(default="USD")
    duration_days: int = Field(default=14)
    screening_questions: list[str] = Field(default_factory=list)
    client_id: Optional[str] = None
    connects_cost: int = Field(default=6)

class RiskReport(BaseModel):
    score: float = Field(ge=0.0, le=1.0, description="Risk probability score (0: safe, 1: dangerous)")
    flags: list[str] = Field(default_factory=list, description="Detected warning flags (scam, unpaid_work, off_platform)")
    injected_instructions: list[str] = Field(default_factory=list, description="Extracted prompt injection attempts")
    client_rating: float = Field(default=5.0)
    payment_verified: bool = Field(default=True)
    explanation: str = Field(default="No significant risk detected.")

class FitReport(BaseModel):
    score: float = Field(ge=0.0, le=1.0, description="Match score between job requirements and portfolio")
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list, description="Citations to verified portfolio case studies/repos")
    reasons: list[str] = Field(default_factory=list)

class BidDecision(BaseModel):
    action: Literal["bid", "skip", "watch"] = Field(..., description="Chosen action for the job")
    reason: str = Field(..., description="Justification based on fit, risk, and connects budget")
    auto_skipped: bool = Field(default=False)

class PriceQuote(BaseModel):
    proposed_bid: float = Field(..., gt=0)
    rationale: str = Field(..., description="Pricing rationale from client history and market statistics")
    connects_cost: int = Field(default=6)
    expected_roi: str = Field(default="Positive")

class ProposalDraft(BaseModel):
    job_id: str
    cover_letter: str = Field(..., min_length=20)
    screening_answers: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    revision_count: int = Field(default=0)
    status: Literal["draft", "critiqued", "ready_for_approval"] = "draft"

class Critique(BaseModel):
    passed: bool = Field(default=True)
    grounding_score: float = Field(ge=0.0, le=1.0)
    unsupported_claims: list[str] = Field(default_factory=list)
    feedback: str = Field(default="Draft is well-grounded and concise.")
    requires_rewrite: bool = Field(default=False)

class ComplianceVerdict(BaseModel):
    compliant: bool = Field(default=True)
    violations: list[str] = Field(default_factory=list)
    redacted_items: list[str] = Field(default_factory=list)
    explanation: str = Field(default="Complies fully with marketplace policy pack.")

class ConversationIntent(BaseModel):
    intent: Literal["question", "negotiation", "interview_request", "scam_signal", "general"]
    confidence: float = Field(ge=0.0, le=1.0)
    key_points: list[str] = Field(default_factory=list)
    proposed_action: str

class ApprovalPayload(BaseModel):
    thread_id: str
    job_id: str
    draft: ProposalDraft
    evidence_items: list[dict[str, Any]] = Field(default_factory=list)
    risk_report: RiskReport
    price_quote: PriceQuote
    dry_run_preview: dict[str, Any]
    approval_status: Literal["pending", "approved", "rejected", "edited"] = "pending"
    user_feedback: Optional[str] = None
