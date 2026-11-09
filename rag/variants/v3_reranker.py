"""
Variant V3: Cross-Encoder / Reranker (Retrieval Group).
Retrieves an initial candidate pool (3x k) using dense similarity,
then re-scores candidates using fine-grained cross-attention / feature re-ranking.
"""
from typing import Any
from rag.index.vector_index import PortfolioIndex

def score_rerank(query: str, chunk: dict[str, Any]) -> float:
    """Reranker scoring function combining term precision, skill overlap, and outcome boost."""
    q_lower = query.lower()
    text = chunk.get("text", "").lower()
    skills = [s.lower() for s in chunk.get("skills", [])]

    # Skill match score
    skill_hits = sum(1.5 for s in skills if s in q_lower)
    
    # Exact phrase / n-gram match
    phrase_hits = 0
    words = [w for w in q_lower.split() if len(w) > 3]
    for i in range(len(words) - 1):
        bigram = f"{words[i]} {words[i+1]}"
        if bigram in text:
            phrase_hits += 2.0

    # Type preference (case studies and repos have higher evidentiary weight)
    type_weight = 1.2 if chunk.get("type") in ["case_study", "repo"] else 0.9

    return (skill_hits + phrase_hits) * type_weight

def retrieve(query: str, index: PortfolioIndex, k: int = 5) -> list[dict[str, Any]]:
    # 1. Fetch wider initial candidate pool
    initial_pool = index.dense_search(query, top_k=k * 4)
    if not initial_pool:
        return []

    # 2. Re-rank candidates
    reranked = []
    for chunk, initial_score in initial_pool:
        rerank_score = score_rerank(query, chunk)
        combined_score = (0.4 * initial_score) + (0.6 * rerank_score)
        reranked.append((chunk, combined_score))

    reranked.sort(key=lambda x: x[1], reverse=True)
    return [chunk for chunk, _ in reranked[:k]]

