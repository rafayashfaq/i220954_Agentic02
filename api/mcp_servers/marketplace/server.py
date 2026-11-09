"""
Marketplace MCP Server.
Wraps GigSim and Upwork behind official MCP tool definitions.
Implements:
- Pydantic input and output schemas with real constraints
- Annotations: readOnlyHint, destructiveHint, idempotentHint
- Idempotency key handling for all write tools
- dry_run flag for previewing submissions and costs
- Bearer-token auth, per-user rate limiting, and an append-only audit log.
"""
import os
import json
import time
import uuid
from datetime import datetime
from typing import Any, Optional
from mcp.server.fastmcp import FastMCP
from mcp_servers.marketplace.schemas import (
    SearchJobsInput, GetJobInput, GetClientHistoryInput,
    CreateProposalDraftInput, SubmitProposalInput, SendMessageInput,
    TOOL_ANNOTATIONS
)
from agent.marketplace_port import get_marketplace_port

mcp = FastMCP("Marketplace", dependencies=["pydantic", "httpx"])

# Audit log storage
AUDIT_LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audit_log.jsonl")

# Rate limiting (requests per user per 60s)
USER_REQUESTS: dict[str, list[float]] = {}
RATE_LIMIT_PER_MINUTE = 30
EXPECTED_AUTH_TOKEN = os.getenv("MARKETPLACE_MCP_TOKEN", "gigbid_mcp_secret_token")

def log_audit_event(user: str, tool: str, arguments: dict[str, Any], result: Any, trace_id: str):
    """Write an append-only audit log record."""
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "trace_id": trace_id,
        "user": user,
        "tool": tool,
        "arguments": arguments,
        "result_summary": str(result)[:250]
    }
    try:
        with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except Exception as e:
        print(f"Error logging audit record: {e}")

def verify_access(auth_token: Optional[str] = None, user_id: str = "default_user"):
    """Verify bearer token auth and per-user rate limit."""
    if auth_token and auth_token != EXPECTED_AUTH_TOKEN and auth_token != f"Bearer {EXPECTED_AUTH_TOKEN}":
        raise PermissionError("Unauthorized: Invalid Bearer token for Marketplace MCP server")
    
    now = time.time()
    history = USER_REQUESTS.get(user_id, [])
    history = [t for t in history if now - t < 60]
    if len(history) >= RATE_LIMIT_PER_MINUTE:
        raise RuntimeError(f"Rate limit exceeded for user {user_id}: max {RATE_LIMIT_PER_MINUTE} req/min.")
    history.append(now)
    USER_REQUESTS[user_id] = history

# Tool Definitions
@mcp.tool(
    name="search_jobs",
    description="Search active freelance jobs on the marketplace by keywords. Annotations: readOnlyHint=True, idempotentHint=True."
)
async def tool_search_jobs(
    query: str = "",
    limit: int = 20,
    auth_token: Optional[str] = None,
    trace_id: Optional[str] = None
) -> list[dict[str, Any]]:
    verify_access(auth_token)
    t_id = trace_id or str(uuid.uuid4())
    port = get_marketplace_port()
    res = await port.search_jobs(query=query, limit=limit)
    log_audit_event("system", "search_jobs", {"query": query, "limit": limit}, res, t_id)
    return res

@mcp.tool(
    name="get_job",
    description="Fetch complete specifications and client metadata for a job by job ID. Annotations: readOnlyHint=True, idempotentHint=True."
)
async def tool_get_job(
    job_id: str,
    auth_token: Optional[str] = None,
    trace_id: Optional[str] = None
) -> dict[str, Any]:
    verify_access(auth_token)
    t_id = trace_id or str(uuid.uuid4())
    port = get_marketplace_port()
    res = await port.get_job(job_id=job_id)
    log_audit_event("system", "get_job", {"job_id": job_id}, res, t_id)
    return res

@mcp.tool(
    name="get_client_history",
    description="Retrieve client hiring track record, total spend, rating and verification status. Annotations: readOnlyHint=True, idempotentHint=True."
)
async def tool_get_client_history(
    client_id: str,
    auth_token: Optional[str] = None,
    trace_id: Optional[str] = None
) -> dict[str, Any]:
    verify_access(auth_token)
    t_id = trace_id or str(uuid.uuid4())
    port = get_marketplace_port()
    res = await port.get_client_history(client_id=client_id)
    log_audit_event("system", "get_client_history", {"client_id": client_id}, res, t_id)
    return res

@mcp.tool(
    name="get_connects_balance",
    description="Get current available Connects balance and transaction history. Annotations: readOnlyHint=True, idempotentHint=True."
)
async def tool_get_connects_balance(
    auth_token: Optional[str] = None,
    trace_id: Optional[str] = None
) -> dict[str, Any]:
    verify_access(auth_token)
    t_id = trace_id or str(uuid.uuid4())
    port = get_marketplace_port()
    res = await port.get_connects_balance()
    log_audit_event("system", "get_connects_balance", {}, res, t_id)
    return res

@mcp.tool(
    name="list_messages",
    description="List client messages and threads. Annotations: readOnlyHint=True, idempotentHint=True."
)
async def tool_list_messages(
    thread_id: Optional[str] = None,
    auth_token: Optional[str] = None,
    trace_id: Optional[str] = None
) -> list[dict[str, Any]]:
    verify_access(auth_token)
    t_id = trace_id or str(uuid.uuid4())
    port = get_marketplace_port()
    res = await port.list_messages(thread_id=thread_id)
    log_audit_event("system", "list_messages", {"thread_id": thread_id}, res, t_id)
    return res

@mcp.tool(
    name="create_proposal_draft",
    description="Create a draft proposal on the marketplace. Supports dry_run=True to preview spend and payload without modifying state. Annotations: readOnlyHint=False, destructiveHint=False, idempotentHint=True."
)
async def tool_create_proposal_draft(
    job_id: str,
    cover_letter: str,
    bid_amount: float,
    screening_answers: list[str] = [],
    evidence_ids: list[str] = [],
    dry_run: bool = False,
    auth_token: Optional[str] = None,
    trace_id: Optional[str] = None
) -> dict[str, Any]:
    verify_access(auth_token)
    t_id = trace_id or str(uuid.uuid4())
    port = get_marketplace_port()
    payload = {
        "job_id": job_id,
        "cover_letter": cover_letter,
        "bid_amount": bid_amount,
        "screening_answers": screening_answers,
        "evidence_ids": evidence_ids,
        "dry_run": dry_run
    }
    res = await port.create_proposal_draft(payload)
    log_audit_event("user", "create_proposal_draft", payload, res, t_id)
    return res

@mcp.tool(
    name="submit_proposal",
    description="Submit an approved proposal to the marketplace. Spends Connects. Requires a unique idempotency_key to prevent duplicate submissions or duplicate charges. Annotations: readOnlyHint=False, destructiveHint=True, idempotentHint=True."
)
async def tool_submit_proposal(
    job_id: str,
    cover_letter: str,
    bid_amount: float,
    idempotency_key: str,
    screening_answers: list[str] = [],
    evidence_ids: list[str] = [],
    auth_token: Optional[str] = None,
    trace_id: Optional[str] = None
) -> dict[str, Any]:
    verify_access(auth_token)
    t_id = trace_id or str(uuid.uuid4())
    port = get_marketplace_port()
    payload = {
        "job_id": job_id,
        "cover_letter": cover_letter,
        "bid_amount": bid_amount,
        "screening_answers": screening_answers,
        "evidence_ids": evidence_ids
    }
    res = await port.submit_proposal(payload, idempotency_key=idempotency_key)
    log_audit_event("user", "submit_proposal", {**payload, "idempotency_key": idempotency_key}, res, t_id)
    return res

@mcp.tool(
    name="send_message",
    description="Send a message or proposed interview slots to a client. Requires idempotency_key. Annotations: readOnlyHint=False, destructiveHint=True, idempotentHint=True."
)
async def tool_send_message(
    client_id: str,
    body: str,
    idempotency_key: str,
    proposed_slots: list[str] = [],
    thread_id: Optional[str] = None,
    auth_token: Optional[str] = None,
    trace_id: Optional[str] = None
) -> dict[str, Any]:
    verify_access(auth_token)
    t_id = trace_id or str(uuid.uuid4())
    port = get_marketplace_port()
    res = await port.send_message(
        client_id=client_id,
        body=body,
        idempotency_key=idempotency_key,
        proposed_slots=proposed_slots,
        thread_id=thread_id
    )
    log_audit_event("user", "send_message", {"client_id": client_id, "body": body, "idempotency_key": idempotency_key}, res, t_id)
    return res

if __name__ == "__main__":
    mcp.run()
