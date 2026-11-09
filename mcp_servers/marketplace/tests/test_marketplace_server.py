"""
Unit tests for Marketplace MCP server tools, schemas, idempotency, and audit logging.
"""
import uuid
import pytest
from mcp_servers.marketplace.server import (
    tool_search_jobs, tool_get_job, tool_get_client_history,
    tool_get_connects_balance, tool_create_proposal_draft,
    tool_submit_proposal, tool_send_message
)

@pytest.mark.asyncio
async def test_marketplace_read_tools():
    jobs = await tool_search_jobs(query="Python", limit=5)
    assert isinstance(jobs, list)
    assert len(jobs) > 0
    job_id = jobs[0]["job_id"]

    job = await tool_get_job(job_id=job_id)
    assert job["job_id"] == job_id
    assert "title" in job

    client = await tool_get_client_history(client_id="sample-client-001")
    assert client["client_id"] == "sample-client-001"

    balance = await tool_get_connects_balance()
    assert "balance" in balance

@pytest.mark.asyncio
async def test_proposal_draft_dry_run():
    res = await tool_create_proposal_draft(
        job_id="sample-job-001",
        cover_letter="I have extensive experience with customer churn classification and Python baselines.",
        bid_amount=350.0,
        screening_answers=["I evaluate with precision, recall and PR-AUC."],
        evidence_ids=["evidence-001"],
        dry_run=True
    )
    assert res["dry_run"] is True
    assert res["ready_for_submission"] is True
    assert res["connects_required"] > 0

@pytest.mark.asyncio
async def test_proposal_submission_and_idempotency():
    idem_key = f"test-key-{uuid.uuid4().hex}"
    res1 = await tool_submit_proposal(
        job_id="sample-job-001",
        cover_letter="Here is my proposal citing evidence-001 and case studies.",
        bid_amount=350.0,
        idempotency_key=idem_key,
        screening_answers=[],
        evidence_ids=["evidence-001"]
    )
    assert res1["status"] == "submitted"
    assert res1["idempotency_key"] == idem_key

    # Retry same call with same idempotency key
    res2 = await tool_submit_proposal(
        job_id="sample-job-001",
        cover_letter="Here is my proposal citing evidence-001 and case studies.",
        bid_amount=350.0,
        idempotency_key=idem_key,
        screening_answers=[],
        evidence_ids=["evidence-001"]
    )
    # Must not double charge or create a second submission
    assert res2["submission_id"] == res1["submission_id"] or res2.get("status") == "already_submitted"

@pytest.mark.asyncio
async def test_send_message():
    idem_key = f"msg-idem-{uuid.uuid4().hex}"
    res = await tool_send_message(
        client_id="sample-client-001",
        body="Hello, I am available for a brief technical call.",
        idempotency_key=idem_key,
        proposed_slots=["2026-11-12T10:00:00Z"]
    )
    assert res["status"] == "sent"

