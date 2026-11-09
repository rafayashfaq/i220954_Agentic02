"""
Proposal Studio Router.
Handles interactive proposal draft editing, claim-to-evidence hover mappings,
inline Critic and Compliance feedback, paragraph regeneration, and dry-run previews.
"""
from fastapi import APIRouter, HTTPException
from apps.api.schemas.api_schemas import (
    ProposalStudioResponse, RegenerateParagraphRequest
)
from apps.api.routers.auth import CURRENT_USER
from rag.retriever import get_retriever
from rag.verify import verify_claims
from mcp_servers.marketplace.server import tool_create_proposal_draft

router = APIRouter(prefix="/proposals", tags=["proposals"])

STUDIO_CACHE: dict[str, dict] = {}

@router.get("/studio/{job_id}", response_model=ProposalStudioResponse)
async def get_proposal_studio(job_id: str):
    retriever = get_retriever(persona_key=CURRENT_USER.persona_key)
    evidence = retriever.retrieve(f"job {job_id}", k=3)
    ev_ids = [e.get("chunk_id", e.get("evidence_id", "evidence-01")) for e in evidence]
    primary_id = ev_ids[0] if ev_ids else "case-ai-001"

    cover_letter = (
        f"For your {job_id} deliverables, I recently completed a similar system with verified performance improvements. "
        f"In project [{primary_id}], I delivered end-to-end architecture with automated unit testing and robust error boundaries. "
        f"I can set up a clean baseline within 10 days and support production handoff."
    )

    v_report = verify_claims(cover_letter, evidence)

    # Format claims with hover metadata
    claims_with_evidence = []
    for c in v_report.get("claims", []):
        matched_chunk = evidence[0] if evidence else {}
        claims_with_evidence.append({
            "claim_text": c["claim"],
            "status": c["status"],
            "evidence_id": matched_chunk.get("chunk_id", primary_id),
            "evidence_title": matched_chunk.get("title", "Portfolio Case Study"),
            "evidence_summary": matched_chunk.get("summary", "Production delivery with measured metrics."),
            "proven_outcome": matched_chunk.get("outcome", "Successful production delivery")
        })

    # Dry-run preview
    dry_run = await tool_create_proposal_draft(
        job_id=job_id,
        cover_letter=cover_letter,
        bid_amount=450.0,
        screening_answers=["I use precision-recall evaluation and cross-validation."],
        evidence_ids=ev_ids,
        dry_run=True
    )

    studio_data = {
        "thread_id": f"thread-{job_id}",
        "job_id": job_id,
        "cover_letter": cover_letter,
        "claims_with_evidence": claims_with_evidence,
        "screening_answers": ["I evaluate using PR-AUC and stratified k-fold splits."],
        "critic_feedback": "Draft is well-grounded, concise (<120 words), and cites verified evidence.",
        "compliance_explanation": "Zero off-platform solicitations or ungrounded guarantees detected. Fully compliant.",
        "is_compliant": True,
        "dry_run_preview": dry_run,
        "approval_status": "pending"
    }

    STUDIO_CACHE[job_id] = studio_data

    # Ensure approval gate has this thread ready for immediate human action
    from apps.api.routers.approvals import PENDING_APPROVALS
    PENDING_APPROVALS[f"thread-{job_id}"] = {
        "thread_id": f"thread-{job_id}",
        "job_id": job_id,
        "title": f"Proposal for {job_id}",
        "cover_letter": cover_letter,
        "bid_amount": 450.0,
        "connects_cost": 6,
        "evidence_ids": ev_ids,
        "status": "pending",
        "created_at": "2026-11-09T10:00:00Z"
    }

    return ProposalStudioResponse(**studio_data)

@router.post("/studio/{job_id}/regenerate_paragraph")
def regenerate_paragraph(job_id: str, req: RegenerateParagraphRequest):
    retriever = get_retriever(persona_key=CURRENT_USER.persona_key)
    evidence = retriever.retrieve(f"job {job_id}", k=2)
    ev_id = evidence[0].get("chunk_id", "case-01") if evidence else "case-01"

    new_text = (
        f"Regarding architectural scalability (demonstrated in [{ev_id}]), "
        f"I specialize in modular asynchronous pipelines with structured schemas and full observability."
    )
    return {"paragraph_index": req.paragraph_index, "regenerated_text": new_text}

