"""
Typed API Request and Response Schemas for FastAPI OpenAPI contract.
"""
from typing import Optional, Any, Literal
from pydantic import BaseModel, Field

class UserProfile(BaseModel):
    user_id: str
    persona_key: str = "ai_engineer"
    display_name: str
    headline: str
    hourly_rate: float
    min_budget: float
    weekly_connects_budget: int = 80
    marketplace_mode: str = "gigsim"

class OnboardingRequest(BaseModel):
    persona_key: str
    display_name: str
    hourly_rate: float
    min_budget: float
    weekly_connects_budget: int = 80
    marketplace_mode: str = "gigsim"

class JobSummary(BaseModel):
    job_id: str
    title: str
    description: str
    required_skills: list[str]
    budget_min: float
    budget_max: float
    connects_cost: int
    fit_score: float
    risk_score: float
    recommended_action: Literal["bid", "skip", "watch"]
    warning_signals: list[str] = Field(default_factory=list)
    has_injection: bool = False

class JobDetailResponse(BaseModel):
    job_id: str
    title: str
    description: str
    deliverables: list[str]
    required_skills: list[str]
    implied_skills: list[str]
    budget_min: float
    budget_max: float
    connects_cost: int
    fit_score: float
    risk_score: float
    recommended_action: str
    bid_or_skip_reason: str
    price_rationale: str
    proposed_bid: float
    warning_signals: list[str]
    requirement_evidence_matrix: list[dict[str, Any]]

class ProposalStudioResponse(BaseModel):
    thread_id: str
    job_id: str
    cover_letter: str
    claims_with_evidence: list[dict[str, Any]]
    screening_answers: list[str]
    critic_feedback: str
    compliance_explanation: str
    is_compliant: bool
    dry_run_preview: dict[str, Any]
    approval_status: str

class RegenerateParagraphRequest(BaseModel):
    paragraph_index: int
    current_text: str
    guidance: Optional[str] = None

class ApprovalActionRequest(BaseModel):
    thread_id: str
    action: Literal["approved", "edited", "rejected"]
    edited_text: Optional[str] = None
    reason: Optional[str] = None

class MessageThread(BaseModel):
    thread_id: str
    client_id: str
    messages: list[dict[str, Any]]
    suggested_reply: Optional[str] = None
    suggested_interview_slots: list[str] = Field(default_factory=list)
    status: str

class SendMessageRequest(BaseModel):
    client_id: str
    body: str
    proposed_slots: list[str] = Field(default_factory=list)

class PipelineCard(BaseModel):
    card_id: str
    job_id: str
    title: str
    client_id: str
    stage: Literal["drafted", "submitted", "viewed", "replied", "interview", "hired", "lost"]
    bid_amount: float
    connects_spent: int
    updated_at: str

class AnalyticsOverview(BaseModel):
    total_jobs_scouted: int
    total_proposals_submitted: int
    reply_rate_percentage: float
    hire_rate_percentage: float
    connects_spent_total: int
    average_cost_per_proposal_usd: float
    p95_latency_ms: float
    rejection_taxonomy: list[dict[str, Any]]
    outcomes_by_category: list[dict[str, Any]]

class SettingsResponse(BaseModel):
    autonomy_level: str  # manual, auto_skip_only
    weekly_budget: int
    saved_searches: list[str]
    connected_accounts: list[dict[str, Any]]
    style_memory_rules: list[dict[str, Any]]

