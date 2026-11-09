"""
Streaming bridge: Streams live LangGraph node-by-node execution events via Server-Sent Events (SSE).
"""
import asyncio
import json
from typing import AsyncGenerator
from agent.graphs.bid_graph import build_bid_graph

async def event_generator(job_payload: dict, persona_key: str = "ai_engineer") -> AsyncGenerator[str, None]:
    """Runs the LangGraph bid graph and streams node progression events as SSE chunks."""
    graph = build_bid_graph()
    thread_id = f"stream-{job_payload.get('job_id', 'job')}"
    config = {"configurable": {"thread_id": thread_id}}

    initial_state = {
        "job": job_payload,
        "persona_key": persona_key
    }

    yield f"data: {json.dumps({'event': 'start', 'thread_id': thread_id, 'node': 'init', 'message': 'Initializing multi-agent pipeline...'})}\n\n"
    await asyncio.sleep(0.05)

    try:
        # Stream node execution
        async for chunk in graph.astream(initial_state, config=config, stream_mode="updates"):
            for node_name, updates in chunk.items():
                msg = f"Completed node: {node_name}"
                if node_name == "scout":
                    msg = "Scout ingested job and validated uniqueness."
                elif node_name == "analyst":
                    msg = f"Extracted JobSpec with {len(updates.get('job_spec', {}).deliverables if hasattr(updates.get('job_spec', {}), 'deliverables') else [])} deliverables."
                elif node_name == "risk_assessor":
                    r = updates.get("risk_report")
                    msg = f"Risk Assessment score: {r.score if r else 0.0} (flags: {len(r.flags if r else [])})."
                elif node_name == "fit_matcher":
                    f = updates.get("fit_report")
                    msg = f"Portfolio Fit score: {f.score if f else 0.0} (citing {len(f.evidence_ids if f else [])} evidence items)."
                elif node_name == "decision_node":
                    d = updates.get("decision")
                    msg = f"Routing Decision: {d.action.upper() if d else 'BID'} - {d.reason if d else ''}"
                elif node_name == "pricing":
                    p = updates.get("price_quote")
                    msg = f"Pricing Strategy: ${p.proposed_bid if p else 350.0} (Connects: {p.connects_cost if p else 6})."
                elif node_name == "writer":
                    msg = "Proposal Writer drafted evidence-grounded cover letter."
                elif node_name == "verifier":
                    msg = "Claim Verifier checked atomic claims against portfolio evidence."
                elif node_name == "critic":
                    c = updates.get("critique")
                    msg = f"Critic verdict: {'PASSED' if c and c.passed else 'REVISION'} - {c.feedback if c else ''}"
                elif node_name == "compliance":
                    msg = "Compliance Guard enforced platform policy rules and sanitized PII."
                elif node_name == "prepare_approval":
                    msg = "Dry-run cost preview generated. Pausing for human approval."

                payload = {
                    "event": "node_update",
                    "thread_id": thread_id,
                    "node": node_name,
                    "message": msg,
                    "state_summary": str(updates)[:150]
                }
                yield f"data: {json.dumps(payload)}\n\n"
                await asyncio.sleep(0.05)

        # Check if paused at interrupt
        state = await graph.aget_state(config)
        if state.next:
            yield f"data: {json.dumps({'event': 'interrupt', 'thread_id': thread_id, 'next_node': state.next[0], 'message': 'Paused at human approval gate.'})}\n\n"
        else:
            yield f"data: {json.dumps({'event': 'done', 'thread_id': thread_id, 'message': 'Pipeline completed.'})}\n\n"

    except Exception as e:
        yield f"data: {json.dumps({'event': 'error', 'thread_id': thread_id, 'error': str(e)})}\n\n"

