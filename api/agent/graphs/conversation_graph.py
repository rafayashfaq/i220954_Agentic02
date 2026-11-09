"""
Conversation Graph: Durable LangGraph StateGraph managing ongoing client communications.
Features:
- Client Liaison intent classification
- Proposes interview slots from calendar via Workspace MCP tool
- Interrupt-based human approval before any outbound message is sent
- Durable SQLite checkpointing
"""
import os
import uuid
import sqlite3
from typing import Literal
from datetime import datetime

from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt
from langgraph.checkpoint.sqlite import SqliteSaver

from agent.state import ConversationGraphState
from agent.nodes.client_liaison import client_liaison_node
from mcp_servers.marketplace.server import tool_send_message

CONV_CHECKPOINT_DB = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "processed", "conversation_checkpoints.db"
)
os.makedirs(os.path.dirname(CONV_CHECKPOINT_DB), exist_ok=True)

def human_approval_message_node(state: ConversationGraphState) -> dict:
    """Interrupts graph execution to wait for user approval before sending client reply."""
    client_id = state.get("client_id", "client-default")
    proposed_reply = state.get("proposed_reply", "")
    slots = state.get("proposed_interview_slots", [])

    # LangGraph interrupt
    human_response = interrupt({
        "type": "message_approval_required",
        "client_id": client_id,
        "proposed_reply": proposed_reply,
        "proposed_slots": slots
    })

    status = human_response.get("action", "approved")
    edited_reply = human_response.get("edited_reply")

    updates = {"approval_status": status}
    if status == "edited" and edited_reply:
        updates["proposed_reply"] = edited_reply

    return updates

async def send_approved_message_node(state: ConversationGraphState) -> dict:
    """Sends the approved message to the marketplace with an idempotency key."""
    status = state.get("approval_status")
    if status not in ["approved", "edited"]:
        return {"final_message_sent": {"status": "rejected_by_user"}}

    client_id = state.get("client_id", "sample-client-001")
    thread_id = state.get("thread_id", f"thread-{client_id}")
    body = state.get("proposed_reply", "")
    slots = state.get("proposed_interview_slots", [])

    idempotency_key = f"msg-idem-{uuid.uuid4().hex[:8]}"

    res = await tool_send_message(
        client_id=client_id,
        body=body,
        idempotency_key=idempotency_key,
        proposed_slots=slots,
        thread_id=thread_id
    )

    return {
        "final_message_sent": res,
        "approval_status": "sent"
    }

from langgraph.checkpoint.memory import MemorySaver

def build_conversation_graph(checkpointer=None):
    """Builds and compiles the durable LangGraph Conversation Graph."""
    builder = StateGraph(ConversationGraphState)

    builder.add_node("client_liaison", client_liaison_node)
    builder.add_node("human_approval", human_approval_message_node)
    builder.add_node("send_message", send_approved_message_node)

    builder.add_edge(START, "client_liaison")
    builder.add_edge("client_liaison", "human_approval")
    builder.add_edge("human_approval", "send_message")
    builder.add_edge("send_message", END)

    cp = checkpointer if checkpointer is not None else MemorySaver()
    return builder.compile(checkpointer=cp)
