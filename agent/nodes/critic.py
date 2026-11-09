"""
Critic Node: Audits grounded proposal drafts and enforces bounded critique loops.
Can send back for revision at most TWICE (max 2 revisions).
"""
import os
from datetime import datetime
from agent.state import BidGraphState
from agent.handoffs import Critique

def load_prompt() -> str:
    prompt_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "prompts", "critic_v1.md")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()

def critic_node(state: BidGraphState) -> dict:
    draft = state.get("proposal_draft")
    revision_count = state.get("revision_count", 0)
    v_report = state.get("claim_verification", {})

    cover = draft.cover_letter if draft else ""
    unsupported = v_report.get("unsupported_rate_after", 0.0)

    # Check length and grounding
    word_count = len(cover.split())
    too_long = word_count > 300
    poorly_grounded = unsupported > 0.0

    needs_rewrite = (too_long or poorly_grounded) and (revision_count < 2)

    feedback = "Draft is grounded in evidence and concise."
    if too_long:
        feedback = f"Proposal is too long ({word_count} words). Shorten to under 250 words."
    elif poorly_grounded:
        feedback = "Ensure all technical claims cite specific portfolio evidence IDs."
    elif revision_count >= 2:
        feedback = "Maximum revision limit reached (2); moving to Compliance Guard."

    critique = Critique(
        passed=not needs_rewrite,
        grounding_score=1.0 if not poorly_grounded else 0.6,
        unsupported_claims=[],
        feedback=feedback,
        requires_rewrite=needs_rewrite
    )

    trace = {
        "node": "critic",
        "tool": "get_case_study",
        "input": {"revision_count": revision_count, "word_count": word_count},
        "output": critique.model_dump(),
        "timestamp": datetime.utcnow().isoformat()
    }

    new_revision_count = revision_count + 1 if needs_rewrite else revision_count

    return {
        "critique": critique,
        "revision_count": new_revision_count,
        "execution_traces": [trace]
    }
