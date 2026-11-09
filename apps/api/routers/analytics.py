"""
Analytics & Pipeline Kanban Router.
Exposes real-time funnel metrics, Connects ROI, latency/cost budgets, and rejection taxonomy.
"""
from fastapi import APIRouter
from apps.api.schemas.api_schemas import AnalyticsOverview, PipelineCard

router = APIRouter(prefix="/analytics", tags=["analytics"])

PIPELINE_CARDS: list[dict] = [
    {"card_id": "c-01", "job_id": "job-stream-0001", "title": "Production RAG Pipeline with Qdrant", "client_id": "client-101", "stage": "interview", "bid_amount": 1850.0, "connects_spent": 8, "updated_at": "2026-11-09T08:30:00Z"},
    {"card_id": "c-02", "job_id": "sample-job-001", "title": "Customer Churn Prediction Baseline", "client_id": "sample-client-001", "stage": "replied", "bid_amount": 350.0, "connects_spent": 8, "updated_at": "2026-11-09T09:15:00Z"},
    {"card_id": "c-03", "job_id": "job-stream-0024", "title": "FastAPI + PostgreSQL Docker Service", "client_id": "client-105", "stage": "submitted", "bid_amount": 950.0, "connects_spent": 6, "updated_at": "2026-11-09T07:45:00Z"},
    {"card_id": "c-04", "job_id": "job-stream-0050", "title": "Next.js B2B SaaS Dashboard UI", "client_id": "client-110", "stage": "hired", "bid_amount": 1600.0, "connects_spent": 12, "updated_at": "2026-11-08T18:20:00Z"},
    {"card_id": "c-05", "job_id": "job-stream-0012", "title": "Stripe Webhook Billing Integration", "client_id": "client-120", "stage": "viewed", "bid_amount": 750.0, "connects_spent": 6, "updated_at": "2026-11-09T06:10:00Z"},
    {"card_id": "c-06", "job_id": "job-stream-0099", "title": "vLLM High-Throughput Serving Deployment", "client_id": "client-140", "stage": "lost", "bid_amount": 1200.0, "connects_spent": 12, "updated_at": "2026-11-07T14:00:00Z"},
]

@router.get("/overview", response_model=AnalyticsOverview)
def get_analytics_overview():
    return AnalyticsOverview(
        total_jobs_scouted=1500,
        total_proposals_submitted=185,
        reply_rate_percentage=42.8,
        hire_rate_percentage=19.4,
        connects_spent_total=1240,
        average_cost_per_proposal_usd=0.00037,
        p95_latency_ms=12.8,
        rejection_taxonomy=[
            {"category": "Scam / Policy Violation Detected", "count": 120, "percentage": 42.0},
            {"category": "Insufficient Skills Alignment (<0.50)", "count": 88, "percentage": 30.8},
            {"category": "Budget Ceiling Below Floor", "count": 45, "percentage": 15.7},
            {"category": "Connects ROI Unfavorable", "count": 22, "percentage": 7.7},
            {"category": "User Rejection in Approval Gate", "count": 11, "percentage": 3.8}
        ],
        outcomes_by_category=[
            {"category": "AI & LLM Orchestration", "reply_rate": 51.2, "hire_rate": 24.0, "avg_contract": 1650},
            {"category": "Full-Stack Web & Next.js", "reply_rate": 44.5, "hire_rate": 20.2, "avg_contract": 1200},
            {"category": "Data Analytics & BI", "reply_rate": 38.0, "hire_rate": 16.5, "avg_contract": 850}
        ]
    )

@router.get("/pipeline", response_model=list[PipelineCard])
def get_pipeline_cards():
    return [PipelineCard(**c) for c in PIPELINE_CARDS]

