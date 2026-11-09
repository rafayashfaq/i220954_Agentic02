"""
Portfolio MCP Resources.
Provides URI template resource loaders:
- portfolio://case/{id}
- portfolio://proposal/{id}
"""
from typing import Any
from mcp_servers.portfolio.tools import get_case_study, get_proposals

def load_case_resource(case_id: str, persona_key: str = "ai_engineer") -> str:
    res = get_case_study(case_id, persona_key)
    return res.get("content", f"Case study {case_id} not found.")

def load_proposal_resource(proposal_id: str, persona_key: str = "ai_engineer") -> str:
    proposals = get_proposals(persona_key)
    for p in proposals:
        if p.get("proposal_id") == proposal_id:
            return f"# Past Proposal {proposal_id}\n\nOutcome: {p.get('outcome')}\nSkills: {', '.join(p.get('skills', []))}\n\n{p.get('text')}"
    return f"Proposal {proposal_id} not found."

