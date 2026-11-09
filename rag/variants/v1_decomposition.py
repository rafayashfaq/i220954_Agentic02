"""
Variant V1: Requirement Decomposition (Query Group).
Decomposes a complex job post into individual discrete requirements/deliverables,
executes a targeted dense retrieval for each individual requirement,
and merges the retrieved candidates using reciprocal rank fusion.
"""
import re
from typing import Any
from rag.index.vector_index import PortfolioIndex

def extract_requirements(job_text: str) -> list[str]:
    """Extract individual requirements or deliverables from job posting text."""
    lines = job_text.splitlines()
    reqs = []
    for line in lines:
        line_clean = line.strip().lstrip("-*•123456789. ")
        if len(line_clean) > 15 and not line_clean.startswith("#"):
            reqs.append(line_clean)
    
    # If no line breaks, split by clauses or punctuation
    if len(reqs) < 2:
        clauses = re.split(r"[.;]\s+", job_text)
        reqs = [c.strip() for c in clauses if len(c.strip()) > 15]

    return reqs[:5] if reqs else [job_text]

def retrieve(query: str, index: PortfolioIndex, k: int = 5) -> list[dict[str, Any]]:
    requirements = extract_requirements(query)
    candidate_scores: dict[str, float] = {}
    chunk_map: dict[str, dict[str, Any]] = {}

    for req in requirements:
        results = index.dense_search(req, top_k=k * 2)
        for rank, (chunk, score) in enumerate(results):
            cid = chunk["chunk_id"]
            chunk_map[cid] = chunk
            # RRF across requirement queries
            candidate_scores[cid] = candidate_scores.get(cid, 0.0) + (1.0 / (60 + rank + 1))

    sorted_cids = sorted(candidate_scores.keys(), key=lambda cid: candidate_scores[cid], reverse=True)
    return [chunk_map[cid] for cid in sorted_cids[:k]]

