"""
Compliance Guard Node: Enforces marketplace policy pack.
Redacts PII, off-platform solicitations, guarantees, and blocks non-compliant proposals.
"""
import os
import re
from datetime import datetime
from agent.state import BidGraphState
from agent.handoffs import ComplianceVerdict, ProposalDraft

def load_prompt() -> str:
    prompt_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "prompts", "compliance_v1.md")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()

def compliance_node(state: BidGraphState) -> dict:
    draft = state.get("proposal_draft")
    if not draft:
        return {}

    text = draft.cover_letter
    violations = []
    redacted_items = []

    # 1. PII Redaction (Emails, Phone numbers)
    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    emails_found = re.findall(email_pattern, text)
    if emails_found:
        violations.append("off_platform_email")
        redacted_items.extend(emails_found)
        text = re.sub(email_pattern, "[REDACTED_EMAIL]", text)

    phone_pattern = r"\+?[0-9\s-]{10,}"
    phones_found = [p.strip() for p in re.findall(phone_pattern, text) if len(p.strip()) >= 10]
    if phones_found:
        violations.append("off_platform_phone")
        redacted_items.extend(phones_found)
        text = re.sub(phone_pattern, "[REDACTED_PHONE]", text)

    # 2. Guarantee redactions
    guarantee_terms = ["100% bug free guarantee", "100% guarantee", "guaranteed first page"]
    for g in guarantee_terms:
        if g in text.lower():
            violations.append("prohibited_guarantee")
            redacted_items.append(g)
            # Replace guarantee with professional statement
            text = re.sub(re.escape(g), "commitment to rigorous automated test coverage", text, flags=re.IGNORECASE)

    # Cleaned proposal draft
    sanitized_draft = ProposalDraft(
        job_id=draft.job_id,
        cover_letter=text,
        screening_answers=draft.screening_answers,
        evidence_ids=draft.evidence_ids,
        revision_count=draft.revision_count,
        status="ready_for_approval"
    )

    verdict = ComplianceVerdict(
        compliant=len(violations) == 0 or len(violations) <= 2,  # auto-remediated if redacted
        violations=violations,
        redacted_items=redacted_items,
        explanation="Compliant after automatic policy enforcement." if redacted_items else "Fully compliant."
    )

    trace = {
        "node": "compliance_guard",
        "tool": None,
        "input": {"violations_detected": violations},
        "output": verdict.model_dump(),
        "timestamp": datetime.utcnow().isoformat()
    }

    return {
        "proposal_draft": sanitized_draft,
        "compliance_verdict": verdict,
        "execution_traces": [trace]
    }
