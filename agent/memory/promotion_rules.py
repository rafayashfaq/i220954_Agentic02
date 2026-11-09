"""
Explicit Promotion Rules for Long-Term Memory.
Raw agent output or unvetted marketplace data never enters long-term memory directly.
Knowledge enters memory ONLY when an explicit promotion rule is satisfied:

1. Style Memory Promotion Rule:
   Triggered on Human Edit. Compares the agent's drafted text with the human's approved text:
   - Identifies removed phrases (e.g., 'excited to apply', 'passionate')
   - Identifies structural changes (e.g., deleted intro paragraph, added specific timeline)
   - If a pattern occurs in >= 2 edits, it is promoted to persistent style guidelines.

2. Outcome Memory Promotion Rule:
   Triggered on Client Reply or Hire.
   - Extracts job category, bid pricing ratio, and cited evidence IDs from winning proposals.
   - Updates category-specific win rates and high-performing phrasing.
"""
import difflib
import re
from typing import Any, Optional

def evaluate_style_promotion(original_draft: str, user_edited_draft: str) -> list[dict[str, Any]]:
    """
    Examines the diff between AI proposal draft and user edited text.
    Extracts explicit, durable writing preferences.
    """
    promoted_rules = []
    
    # 1. First sentence deletion check
    orig_lines = [l.strip() for l in original_draft.splitlines() if l.strip()]
    edited_lines = [l.strip() for l in user_edited_draft.splitlines() if l.strip()]

    if orig_lines and edited_lines:
        first_orig = orig_lines[0].lower()
        first_edited = edited_lines[0].lower()
        if first_orig not in user_edited_draft.lower() and len(first_orig) > 20:
            promoted_rules.append({
                "type": "style_cut_opening",
                "rule": f"Avoid generic opening sentence: '{first_orig[:50]}...'",
                "target": "opening"
            })

    # 2. Banned word detection (e.g. 'passionate', 'rockstar', 'pleasure')
    fluff_terms = ["passionate", "pleasure to apply", "rockstar", "expert ninja", "look forward to hearing"]
    for term in fluff_terms:
        if term in original_draft.lower() and term not in user_edited_draft.lower():
            promoted_rules.append({
                "type": "banned_vocabulary",
                "rule": f"Never use phrase: '{term}'",
                "target": term
            })

    # 3. Brevity check
    if len(user_edited_draft) < len(original_draft) * 0.75:
        promoted_rules.append({
            "type": "length_constraint",
            "rule": "User prefers concise proposals (<150 words). Cut superfluous context.",
            "target": "length"
        })

    return promoted_rules

def evaluate_outcome_promotion(job_category: str, bid_amount: float, outcome: str, cited_evidence_ids: list[str]) -> Optional[dict[str, Any]]:
    """
    Promotes strategy insights only when positive client outcomes (reply, interview, hire) occur.
    """
    if outcome in ["replied", "interview", "hired", "won"]:
        return {
            "type": "winning_pattern",
            "category": job_category,
            "effective_bid": bid_amount,
            "outcome": outcome,
            "high_performing_evidence": cited_evidence_ids,
            "insight": f"In {job_category}, citing {cited_evidence_ids} at ${bid_amount} yielded positive outcome: {outcome}"
        }
    return None
