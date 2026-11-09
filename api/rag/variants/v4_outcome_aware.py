"""
Variant V4: Outcome-Aware Ranking (Ranking Group).
Boosts evidence chunks and proposal excerpts whose historical outcomes were 'won' or 'replied',
penalizing patterns and phrasing associated with 'ignored' proposals.
"""
from typing import Any
from rag.index.vector_index import PortfolioIndex

def retrieve(query: str, index: PortfolioIndex, k: int = 5) -> list[dict[str, Any]]:
    # Retrieve hybrid candidates
    candidates = index.hybrid_search_rrf(query=query, top_k=k * 3)
    
    scored_candidates = []
    for chunk, rrf_score in candidates:
        outcome = chunk.get("outcome", "verified")
        # Outcome weight multipliers
        if outcome == "won":
            multiplier = 1.45
        elif outcome == "replied":
            multiplier = 1.25
        elif outcome == "ignored":
            multiplier = 0.70
        else:
            multiplier = 1.0  # Verified case studies/repos maintain steady baseline

        final_score = rrf_score * multiplier
        scored_candidates.append((chunk, final_score))

    scored_candidates.sort(key=lambda x: x[1], reverse=True)
    return [chunk for chunk, _ in scored_candidates[:k]]

