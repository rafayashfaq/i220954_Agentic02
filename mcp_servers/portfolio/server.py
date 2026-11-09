"""
Portfolio MCP Server.
Read-only MCP server exposing freelancer case studies, evidence search, skills, and resources.
Built with the official MCP Python SDK (FastMCP).
"""
import os
from typing import Optional, Any
from mcp.server.fastmcp import FastMCP
from mcp_servers.portfolio.tools import search_evidence, get_case_study, list_skills
from mcp_servers.portfolio.resources import load_case_resource, load_proposal_resource
from mcp_servers.portfolio.prompts import screening_question_prompt

# Instantiate FastMCP server
mcp = FastMCP("Portfolio", dependencies=["pydantic"])

@mcp.tool(
    name="search_evidence",
    description="Search portfolio evidence items (case studies, repos, past proposals) matching a technical requirement. Returns items with type, source, date, skills and outcome."
)
def tool_search_evidence(requirement: str, k: int = 5, persona_key: str = "ai_engineer") -> list[dict[str, Any]]:
    return search_evidence(requirement=requirement, k=k, persona_key=persona_key)

@mcp.tool(
    name="get_case_study",
    description="Retrieve the complete text and outcome metrics for a specific portfolio case study by ID."
)
def tool_get_case_study(case_id: str, persona_key: str = "ai_engineer") -> dict[str, Any]:
    return get_case_study(case_id=case_id, persona_key=persona_key)

@mcp.tool(
    name="list_skills",
    description="List all verified skills present across the freelancer's portfolio."
)
def tool_list_skills(persona_key: str = "ai_engineer") -> list[str]:
    return list_skills(persona_key=persona_key)

@mcp.resource("portfolio://case/{case_id}")
def resource_case_study(case_id: str) -> str:
    """Load full case study as an MCP resource."""
    return load_case_resource(case_id)

@mcp.resource("portfolio://proposal/{proposal_id}")
def resource_past_proposal(proposal_id: str) -> str:
    """Load past proposal as an MCP resource."""
    return load_proposal_resource(proposal_id)

@mcp.prompt()
def answer_screening_question(question: str, job_title: str) -> str:
    """Prompt template for drafting a verified answer to a client screening question."""
    return screening_question_prompt(question, job_title)

if __name__ == "__main__":
    mcp.run()
