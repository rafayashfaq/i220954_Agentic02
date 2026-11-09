"""
Client Liaison Node: Analyzes incoming messages, classifies intent,
proposes interview slots from calendar, and drafts responses.
"""
import os
from datetime import datetime
from agent.state import ConversationGraphState
from agent.handoffs import ConversationIntent
from mcp_servers.workspace.server import tool_get_free_calendar_slots

def load_prompt() -> str:
    prompt_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "prompts", "client_liaison_v1.md")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()

def client_liaison_node(state: ConversationGraphState) -> dict:
    messages = state.get("messages", [])
    last_msg = messages[-1] if messages else {"body": "Hi, are you free for a call?"}
    body = last_msg.get("body", "").lower()

    # Intent Classification
    if any(k in body for k in ["interview", "call", "chat", "zoom", "sync", "meet", "free for a"]):
        intent_type = "interview_request"
        confidence = 0.95
    elif any(k in body for k in ["rate", "discount", "budget", "cheaper", "cost", "price"]):
        intent_type = "negotiation"
        confidence = 0.88
    elif any(k in body for k in ["telegram", "whatsapp", "crypto", "pay off-platform", "deposit"]):
        intent_type = "scam_signal"
        confidence = 0.98
    elif "?" in body or any(k in body for k in ["how", "what", "can you", "experience"]):
        intent_type = "question"
        confidence = 0.90
    else:
        intent_type = "general"
        confidence = 0.75

    proposed_slots = []
    if intent_type == "interview_request":
        # Get free slots from Workspace MCP tool
        proposed_slots = tool_get_free_calendar_slots(days_ahead=3)
        formatted_slots = [s[:16].replace("T", " at ") + " UTC" for s in proposed_slots[:2]]
        proposed_reply = (
            f"Thank you for reaching out! I would be delighted to connect. "
            f"I am available for a 20-minute discussion at either of these times:\n"
            f"- {formatted_slots[0]}\n"
            f"- {formatted_slots[1]}\n"
            f"Please let me know which works best for your schedule."
        )
    elif intent_type == "negotiation":
        proposed_reply = (
            "Thank you for considering my proposal. My rate reflects end-to-end delivery, "
            "comprehensive test coverage, and proven architecture. Depending on the exact scope "
            "of the initial milestone, we could explore phasing deliverables to align with your current budget."
        )
    elif intent_type == "scam_signal":
        proposed_reply = (
            "Per platform security terms, all project communications and milestones must remain "
            "directly within the platform workspace."
        )
    else:
        proposed_reply = (
            "Thank you for your message. I have reviewed your questions and confirmed our architecture "
            "directly addresses the performance benchmarks required for this deliverable."
        )

    intent = ConversationIntent(
        intent=intent_type,
        confidence=confidence,
        key_points=[body[:60]],
        proposed_action=f"Reply with {intent_type} strategy"
    )

    trace = {
        "node": "client_liaison",
        "tool": "get_free_calendar_slots" if proposed_slots else "list_messages",
        "input": {"message_body": body[:80]},
        "output": intent.model_dump(),
        "timestamp": datetime.utcnow().isoformat()
    }

    return {
        "intent": intent,
        "proposed_reply": proposed_reply,
        "proposed_interview_slots": proposed_slots,
        "execution_traces": [trace]
    }
