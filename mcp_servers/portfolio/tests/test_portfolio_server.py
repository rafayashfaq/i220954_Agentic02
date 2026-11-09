"""
Unit tests for Portfolio MCP server.
"""
import pytest
from mcp_servers.portfolio.tools import search_evidence, get_case_study, list_skills
from mcp_servers.portfolio.resources import load_case_resource, load_proposal_resource
from mcp_servers.portfolio.prompts import screening_question_prompt

def test_search_evidence():
    results = search_evidence("RAG pipeline and LangGraph", k=3, persona_key="ai_engineer")
    assert isinstance(results, list)
    assert len(results) > 0
    item = results[0]
    assert "evidence_id" in item
    assert "title" in item
    assert "skills" in item
    assert "outcome" in item

def test_get_case_study():
    items = search_evidence("Python", k=1, persona_key="ai_engineer")
    assert len(items) > 0
    case_id = items[0]["evidence_id"]
    case = get_case_study(case_id, persona_key="ai_engineer")
    assert case["status"] == "found"
    assert case["case_id"] == case_id
    assert len(case["content"]) > 10

def test_list_skills():
    skills = list_skills("ai_engineer")
    assert isinstance(skills, list)
    assert "Python" in skills or len(skills) > 0

def test_resources():
    content = load_case_resource("case-ai_-001", "ai_engineer")
    assert isinstance(content, str)

def test_prompt_template():
    p = screening_question_prompt("How do you handle rate limits?", "Backend Developer")
    assert "Backend Developer" in p
    assert "screening question" in p.lower()

