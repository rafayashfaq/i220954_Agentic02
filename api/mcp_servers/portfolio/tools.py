"""
Portfolio MCP Server Tools.
Provides read-only access to freelancer case studies, skills, and evidence items.
"""
import os
import json
from typing import Any, Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

def get_portfolio_items(persona_key: str = "ai_engineer") -> list[dict[str, Any]]:
    """Load portfolio items for the active persona."""
    persona_file = os.path.join(DATA_DIR, "personas", persona_key, "portfolio_items.json")
    if os.path.exists(persona_file):
        with open(persona_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    # Fallback to sample
    sample_file = os.path.join(DATA_DIR, "sample", "portfolio_items.json")
    if os.path.exists(sample_file):
        with open(sample_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def get_proposals(persona_key: str = "ai_engineer") -> list[dict[str, Any]]:
    p_file = os.path.join(DATA_DIR, "personas", persona_key, "past_proposals.json")
    if os.path.exists(p_file):
        with open(p_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def search_evidence(
    requirement: str,
    k: int = 5,
    filters: Optional[dict[str, Any]] = None,
    persona_key: str = "ai_engineer"
) -> list[dict[str, Any]]:
    """
    Search portfolio evidence items matching a specific technical requirement.
    Returns items with type, source, date, skills, and outcome.
    """
    items = get_portfolio_items(persona_key)
    query_terms = requirement.lower().split()

    scored_items = []
    for item in items:
        # Apply filters if provided
        if filters:
            if "type" in filters and item.get("type") != filters["type"]:
                continue
            if "skill" in filters and filters["skill"].lower() not in [s.lower() for s in item.get("skills", [])]:
                continue
            if "client_industry" in filters and item.get("client_industry") != filters["client_industry"]:
                continue

        text = (
            item.get("title", "") + " " +
            item.get("summary", "") + " " +
            " ".join(item.get("skills", []))
        ).lower()

        # Word overlap relevance score
        score = sum(1.5 for term in query_terms if term in text)
        for skill in item.get("skills", []):
            if skill.lower() in requirement.lower():
                score += 2.0

        if score > 0 or not query_terms:
            scored_items.append((score, item))

    scored_items.sort(key=lambda x: x[0], reverse=True)
    results = [item for _, item in scored_items[:k]]
    
    # If no results matched query terms, return top-k generic evidence items
    if not results and items:
        results = items[:k]

    return [
        {
            "evidence_id": r.get("evidence_id"),
            "type": r.get("type", "case_study"),
            "title": r.get("title"),
            "summary": r.get("summary"),
            "skills": r.get("skills", []),
            "date": r.get("date", "2025-01-01"),
            "source": r.get("source", "portfolio"),
            "outcome": r.get("outcome", "verified"),
            "client_industry": r.get("client_industry", "Technology")
        }
        for r in results
    ]

def get_case_study(case_id: str, persona_key: str = "ai_engineer") -> dict[str, Any]:
    """Retrieve full text and metadata for a specific case study by ID."""
    case_path = os.path.join(DATA_DIR, "personas", persona_key, "case_studies", f"{case_id}.md")
    if os.path.exists(case_path):
        with open(case_path, "r", encoding="utf-8") as f:
            content = f.read()
        return {
            "case_id": case_id,
            "content": content,
            "status": "found"
        }
    
    # Search in portfolio items
    items = get_portfolio_items(persona_key)
    for it in items:
        if it.get("evidence_id") == case_id:
            return {
                "case_id": case_id,
                "content": f"# {it.get('title')}\n\n{it.get('summary')}\n\n**Skills**: {', '.join(it.get('skills', []))}\n**Outcome**: {it.get('outcome')}",
                "status": "found"
            }

    return {"case_id": case_id, "content": f"Case study {case_id} not found.", "status": "not_found"}

def list_skills(persona_key: str = "ai_engineer") -> list[str]:
    """List all unique verified skills present across the portfolio."""
    items = get_portfolio_items(persona_key)
    skills = set()
    for item in items:
        for s in item.get("skills", []):
            skills.add(s)
    return sorted(list(skills))

