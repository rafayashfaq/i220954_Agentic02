"""
Pydantic Schemas for Marketplace MCP Tools.
Includes field constraints, declared outputs, and tool annotations:
- readOnlyHint
- destructiveHint
- idempotentHint
"""
from typing import Optional, Any
from pydantic import BaseModel, Field

# Input Schemas
class SearchJobsInput(BaseModel):
    query: str = Field(default="", description="Search keywords, e.g. 'Python RAG' or 'Next.js'")
    limit: int = Field(default=20, ge=1, le=100, description="Maximum number of jobs to return")

class GetJobInput(BaseModel):
    job_id: str = Field(..., min_length=3, description="Unique job identifier")

class GetClientHistoryInput(BaseModel):
    client_id: str = Field(..., min_length=3, description="Unique client identifier")

class GetConnectsBalanceInput(BaseModel):
    pass

class ListMessagesInput(BaseModel):
    thread_id: Optional[str] = Field(default=None, description="Optional thread ID to filter messages")

class CreateProposalDraftInput(BaseModel):
    job_id: str = Field(..., min_length=3, description="Target job ID")
    cover_letter: str = Field(..., min_length=20, max_length=5000, description="Proposal cover letter body")
    bid_amount: float = Field(..., gt=0, description="Proposed contract bid in USD")
    screening_answers: list[str] = Field(default_factory=list, description="Answers to client screening questions")
    evidence_ids: list[str] = Field(default_factory=list, description="Portfolio evidence item IDs cited in proposal")
    dry_run: bool = Field(default=False, description="If true, simulates action without creating persistent draft")

class SubmitProposalInput(BaseModel):
    job_id: str = Field(..., min_length=3, description="Target job ID")
    cover_letter: str = Field(..., min_length=20, max_length=5000, description="Proposal cover letter body")
    bid_amount: float = Field(..., gt=0, description="Proposed contract bid in USD")
    screening_answers: list[str] = Field(default_factory=list, description="Answers to client screening questions")
    evidence_ids: list[str] = Field(default_factory=list, description="Portfolio evidence item IDs cited in proposal")
    idempotency_key: str = Field(..., min_length=8, description="Unique UUID idempotency token to prevent double-spending")

class SendMessageInput(BaseModel):
    client_id: str = Field(..., min_length=3, description="Target client ID")
    body: str = Field(..., min_length=2, max_length=4000, description="Message text")
    idempotency_key: str = Field(..., min_length=8, description="Unique UUID idempotency token")
    proposed_slots: list[str] = Field(default_factory=list, description="List of proposed interview ISO timestamp slots")
    thread_id: Optional[str] = Field(default=None, description="Thread ID")

# Output Schemas
class ProposalDraftOutput(BaseModel):
    draft_id: str
    job_id: str
    bid_amount: float
    connects_required: int
    user_balance_after: int
    cover_letter_preview: str
    evidence_ids: list[str]
    dry_run: bool
    ready_for_submission: bool

class ProposalSubmitOutput(BaseModel):
    submission_id: str
    job_id: str
    status: str
    connects_spent: int
    remaining_balance: int
    idempotency_key: str
    submitted_at: str
    simulated_outcome: Optional[dict[str, Any]] = None

class MessageSendOutput(BaseModel):
    status: str
    message: dict[str, Any]

# Tool metadata and annotations
TOOL_ANNOTATIONS = {
    "search_jobs": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True},
    "get_job": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True},
    "get_client_history": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True},
    "get_connects_balance": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True},
    "list_messages": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True},
    "create_proposal_draft": {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True},
    "submit_proposal": {"readOnlyHint": False, "destructiveHint": True, "idempotentHint": True},
    "send_message": {"readOnlyHint": False, "destructiveHint": True, "idempotentHint": True},
}

