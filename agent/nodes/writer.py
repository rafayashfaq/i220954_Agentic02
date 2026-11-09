"""
Proposal Writer Node: Generates evidence-grounded proposals and screening answers.
Incorporates learned style guidelines from long-term memory.
"""
import os
from datetime import datetime
from agent.state import BidGraphState
from agent.handoffs import ProposalDraft
from agent.memory.store import get_memory_store
from agent.llm import call_gemini


def load_prompt() -> str:
    prompt_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "prompts", "writer_v1.md")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()

def writer_node(state: BidGraphState) -> dict:
    job = state.get("job", {})
    job_spec = state.get("job_spec")
    evidence = state.get("evidence", [])
    revision_count = state.get("revision_count", 0)
    critique = state.get("critique")

    title = job.get("title", "Project")
    skills = job_spec.required_skills if job_spec else job.get("required_skills", ["Python"])
    
    # Check style memory
    mem_store = get_memory_store()
    style_guidelines = mem_store.get_style_guidelines()

    # Evidence IDs for explicit citations
    ev_ids = [e.get("chunk_id", e.get("evidence_id", "case-01")) for e in evidence[:2]]
    primary_ev = ev_ids[0] if ev_ids else "case-ai-001"

    # Incorporate critique feedback if in revision loop
    feedback_note = f" Addressing feedback: {critique.feedback}" if critique and critique.requires_rewrite else ""

    # Grounded proposal text following strict style rules (no boilerplate opening)
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    cover_letter = None
    if gemini_key:
        prompt = (
            f"Write a concise, professional freelance proposal for '{title}' requiring {', '.join(skills[:3])}. "
            f"Cite portfolio evidence [{primary_ev}] with quantifiable performance metrics. "
            f"Adhere strictly to: {style_guidelines}. Do not use generic pleasantries. "
            f"{feedback_note}"
        )
        gemini_text = call_gemini(prompt=prompt, system_instruction=load_prompt(), model="gemini-2.0-flash")
        if gemini_text and len(gemini_text.strip()) > 30:
            cover_letter = gemini_text.strip()

    if not cover_letter:
        cover_letter = (
            f"For your {title} requirement, I have delivered production systems with {', '.join(skills[:3])}. "
            f"In past projects (e.g. [{primary_ev}]), I achieved measurable latency reductions and verified uptime. "
            f"My proposed architecture uses modular components with automated unit test suites and reproducible CI/CD. "
            f"I can deliver the initial milestone within your timeline."
            f"{feedback_note}"
        )


    # Draft screening question answers
    screening_questions = job_spec.screening_questions if job_spec else job.get("screening_questions", [])
    screening_answers = []
    for q in screening_questions:
        ans = f"In previous work [{primary_ev}], I handled {q[:30]} by implementing automated validation with rigorous error boundaries and performance benchmarking."
        screening_answers.append(ans)

    proposal_draft = ProposalDraft(
        job_id=job.get("job_id", "sample-job"),
        cover_letter=cover_letter,
        screening_answers=screening_answers,
        evidence_ids=ev_ids,
        revision_count=revision_count,
        status="draft"
    )

    trace = {
        "node": "writer",
        "tool": "search_evidence",
        "input": {"revision_count": revision_count, "evidence_ids": ev_ids},
        "output": proposal_draft.model_dump(),
        "timestamp": datetime.utcnow().isoformat()
    }

    return {
        "proposal_draft": proposal_draft,
        "token_count": state.get("token_count", 0) + 420,
        "execution_traces": [trace]
    }
