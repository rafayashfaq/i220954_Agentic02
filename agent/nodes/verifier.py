"""
Claim Verifier Node: Splits drafted proposal into atomic claims and verifies grounding.
Rewrites or removes unsupported statements before the Critic sees the draft.
"""
from datetime import datetime
from agent.state import BidGraphState
from agent.handoffs import ProposalDraft
from rag.verify import verify_claims

def verifier_node(state: BidGraphState) -> dict:
    draft = state.get("proposal_draft")
    evidence = state.get("evidence", [])
    
    if not draft:
        return {}

    # Execute atomic claim verification
    v_report = verify_claims(draft.cover_letter, evidence)

    # Update draft with verified and grounded text
    verified_draft = ProposalDraft(
        job_id=draft.job_id,
        cover_letter=v_report["verified_draft"] or draft.cover_letter,
        screening_answers=draft.screening_answers,
        evidence_ids=draft.evidence_ids,
        revision_count=draft.revision_count,
        status="critiqued"
    )

    trace = {
        "node": "claim_verifier",
        "tool": None,
        "input": {"unsupported_before": v_report["unsupported_before"]},
        "output": {
            "unsupported_rate_before": v_report["unsupported_rate_before"],
            "unsupported_rate_after": v_report["unsupported_rate_after"],
            "is_clean": v_report["is_clean"]
        },
        "timestamp": datetime.utcnow().isoformat()
    }

    return {
        "proposal_draft": verified_draft,
        "claim_verification": v_report,
        "execution_traces": [trace]
    }

