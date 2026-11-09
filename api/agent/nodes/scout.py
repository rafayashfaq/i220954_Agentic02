"""
Scout Node: Ingests incoming jobs, applies deduplication, and initializes job tracking.
"""
import os
from datetime import datetime
from agent.state import BidGraphState

SEEN_JOBS: set[str] = set()

def load_prompt() -> str:
    prompt_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "prompts", "scout_v1.md")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()

def scout_node(state: BidGraphState) -> dict:
    job = state.get("job", {})
    job_id = job.get("job_id", "unknown-job")
    
    # Check deduplication
    is_duplicate = job.get("is_duplicate", False) or (job_id in SEEN_JOBS)
    SEEN_JOBS.add(job_id)

    trace = {
        "node": "scout",
        "tool": "search_jobs",
        "input": {"job_id": job_id},
        "output": {"is_duplicate": is_duplicate, "title": job.get("title")},
        "timestamp": datetime.utcnow().isoformat()
    }

    if is_duplicate:
        return {
            "execution_traces": [trace],
            "needs_attention": True,
            "attention_reason": "Duplicate job detected by Scout."
        }

    return {
        "step_count": state.get("step_count", 0) + 1,
        "execution_traces": [trace]
    }
