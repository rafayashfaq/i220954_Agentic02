"""
Agent Run Viewer & SSE Streaming Router.
Provides real-time event streaming via Server-Sent Events (SSE) and full trace logs.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from apps.api.streaming import event_generator
from apps.api.routers.auth import CURRENT_USER
from apps.api.routers.jobs import load_jobs

router = APIRouter(prefix="/runs", tags=["runs"])

RECENT_RUNS: list[dict] = [
    {
        "run_id": "run-001",
        "job_id": "sample-job-001",
        "title": "Build customer churn baseline",
        "status": "completed",
        "nodes_executed": ["scout", "analyst", "risk_assessor", "fit_matcher", "decision_node", "pricing", "writer", "verifier", "critic", "compliance", "prepare_approval", "human_approval", "submit"],
        "tokens": 2840,
        "latency_s": 2.1,
        "cost_usd": 0.00056,
        "trace_url": "/runs/run-001/trace"
    },
    {
        "run_id": "run-002",
        "job_id": "sample-job-002",
        "title": "Unpaid trial project [SCAM]",
        "status": "skipped",
        "nodes_executed": ["scout", "analyst", "risk_assessor", "fit_matcher", "decision_node"],
        "tokens": 1220,
        "latency_s": 0.8,
        "cost_usd": 0.00024,
        "trace_url": "/runs/run-002/trace"
    }
]

@router.get("")
def list_runs():
    return RECENT_RUNS

@router.get("/stream/{job_id}")
async def stream_job_run(job_id: str):
    """Streams live LangGraph node-by-node updates for a job via Server-Sent Events."""
    jobs = load_jobs()
    job = next((j for j in jobs if j.get("job_id") == job_id), None)
    if not job:
        job = {
            "job_id": job_id,
            "title": f"Custom Job {job_id}",
            "description": "Custom requirement for automated execution.",
            "required_skills": ["Python", "FastAPI"],
            "budget": {"min": 350, "max": 750, "currency": "USD"}
        }

    return StreamingResponse(
        event_generator(job, persona_key=CURRENT_USER.persona_key),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@router.get("/{run_id}/trace")
def get_run_trace(run_id: str):
    return {
        "run_id": run_id,
        "trace_events": [
            {"step": 1, "node": "scout", "status": "ok", "latency_ms": 12},
            {"step": 2, "node": "analyst (parallel)", "status": "ok", "latency_ms": 140},
            {"step": 2, "node": "risk_assessor (parallel)", "status": "ok", "latency_ms": 155},
            {"step": 2, "node": "fit_matcher (parallel)", "status": "ok", "latency_ms": 180},
            {"step": 3, "node": "decision_node", "status": "ok", "decision": "bid", "latency_ms": 8},
            {"step": 4, "node": "pricing", "status": "ok", "proposed_bid": 350.0, "latency_ms": 15},
            {"step": 5, "node": "writer", "status": "ok", "latency_ms": 420},
            {"step": 6, "node": "verifier", "status": "ok", "unsupported_claims_removed": 1, "latency_ms": 35},
            {"step": 7, "node": "critic", "status": "ok", "passed": True, "latency_ms": 120},
            {"step": 8, "node": "compliance", "status": "ok", "compliant": True, "latency_ms": 25},
            {"step": 9, "node": "human_approval", "status": "resumed_by_human", "latency_ms": 0},
            {"step": 10, "node": "submit", "status": "submitted_to_gigsim", "latency_ms": 95}
        ]
    }

