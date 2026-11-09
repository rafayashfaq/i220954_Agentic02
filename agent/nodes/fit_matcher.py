"""
Fit Matcher Node: Maps job requirements to verified portfolio evidence items.
Runs in parallel with Job Analyst and Risk Assessor.
"""
import os
from datetime import datetime
from agent.state import BidGraphState
from agent.handoffs import FitReport
from rag.retriever import get_retriever

def load_prompt() -> str:
    prompt_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "prompts", "fit_matcher_v1.md")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()

def fit_matcher_node(state: BidGraphState) -> dict:
    job = state.get("job", {})
    persona_key = state.get("persona_key", "ai_engineer")
    skills = job.get("required_skills", [])
    title = job.get("title", "")
    desc = job.get("description", "")
    
    # Retrieve evidence from active portfolio
    retriever = get_retriever(persona_key=persona_key)
    query_text = f"{title} {' '.join(skills)} {desc[:200]}"
    retrieved_chunks = retriever.retrieve(query=query_text, k=4)

    # Compute skills overlap
    portfolio_skills = set()
    for c in retrieved_chunks:
        for s in c.get("skills", []):
            portfolio_skills.add(s.lower())

    matched = []
    missing = []
    for s in skills:
        if s.lower() in portfolio_skills:
            matched.append(s)
        else:
            missing.append(s)

    # Calculate Fit Score
    match_ratio = len(matched) / max(1, len(skills))
    fit_score = round(min(1.0, 0.4 + (0.6 * match_ratio)), 2)
    if not skills:
        fit_score = 0.70

    evidence_ids = [c.get("chunk_id", c.get("evidence_id", "evidence-01")) for c in retrieved_chunks]
    
    reasons = [
        f"Matched {len(matched)} of {len(skills)} required skills ({', '.join(matched) or 'General software engineering'}).",
        f"Citing {len(evidence_ids)} portfolio evidence projects."
    ]
    if missing:
        reasons.append(f"Minor missing skills: {', '.join(missing)}.")

    fit_report = FitReport(
        score=fit_score,
        matched_skills=matched,
        missing_skills=missing,
        evidence_ids=evidence_ids,
        reasons=reasons
    )

    trace = {
        "node": "fit_matcher",
        "tool": "search_evidence",
        "input": {"query": query_text, "persona": persona_key},
        "output": fit_report.model_dump(),
        "timestamp": datetime.utcnow().isoformat()
    }

    return {
        "fit_report": fit_report,
        "evidence": retrieved_chunks,
        "execution_traces": [trace]
    }
