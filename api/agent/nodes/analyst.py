"""
Job Analyst Node: Extracts structured JobSpec Pydantic object from untrusted job text.
Runs in parallel with Risk Assessor and Fit Matcher.
"""
import os
import re
from datetime import datetime
from agent.state import BidGraphState
from agent.handoffs import JobSpec

def load_prompt() -> str:
    prompt_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "prompts", "analyst_v1.md")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()

def analyst_node(state: BidGraphState) -> dict:
    job = state.get("job", {})
    title = job.get("title", "")
    desc = job.get("description", "")
    
    # Delimit untrusted input and extract structured components
    # Extract deliverables
    deliverables = []
    lines = desc.splitlines()
    for line in lines:
        l = line.strip().lstrip("-*•123456789. ")
        if len(l) > 12 and not l.startswith("#"):
            deliverables.append(l)
    if not deliverables:
        deliverables = [f"Complete project deliverable for {title}"]

    # Skills parsing
    skills = job.get("required_skills", [])
    if not skills:
        common_tech = ["Python", "PyTorch", "FastAPI", "React", "TypeScript", "SQL", "Docker", "PostgreSQL"]
        skills = [t for t in common_tech if t.lower() in desc.lower()]
        if not skills:
            skills = ["Software Engineering"]

    budget_info = job.get("budget", {})
    if isinstance(budget_info, dict):
        b_min = float(budget_info.get("min", 250))
        b_max = float(budget_info.get("max", 600))
    else:
        b_min, b_max = 250.0, 600.0

    job_spec = JobSpec(
        job_id=job.get("job_id", "sample-job"),
        title=title,
        deliverables=deliverables[:5],
        required_skills=skills,
        implied_skills=["Architecture", "System Design"],
        budget_min=b_min,
        budget_max=b_max,
        duration_days=job.get("duration_days", 14),
        screening_questions=job.get("screening_questions", []),
        client_id=job.get("client_id", "client-default"),
        connects_cost=job.get("connects_cost", 6)
    )

    trace = {
        "node": "analyst",
        "tool": None,
        "input": {"job_id": job_spec.job_id},
        "output": job_spec.model_dump(),
        "timestamp": datetime.utcnow().isoformat()
    }

    return {
        "job_spec": job_spec,
        "execution_traces": [trace]
    }
