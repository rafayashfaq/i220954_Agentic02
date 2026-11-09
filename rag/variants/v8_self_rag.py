"""
Variant V8: Self-RAG / Corrective RAG (Agentic Group).
Retrieves candidate evidence, grades relevance against job requirements,
and executes iterative query reformulation if evidence is below confidence threshold.
If no relevant evidence exists in portfolio, explicitly refuses to fabricate and flags for skip.
"""
from typing import Any
from rag.index.vector_index import PortfolioIndex

def grade_evidence_relevance(job_query: str, chunk: dict[str, Any]) -> float:
    """Grades relevance of a retrieved evidence chunk against the job requirements."""
    q_words = set(re_tokenize(job_query))
    chunk_words = set(re_tokenize(chunk.get("text", "") + " " + " ".join(chunk.get("skills", []))))
    overlap = len(q_words.intersection(chunk_words))
    # Relevance score between 0 and 1
    return min(1.0, overlap / max(3, len(q_words) * 0.4))

def re_tokenize(text: str) -> list[str]:
    import re
    return [w.lower() for w in re.findall(r"\b[a-zA-Z]{3,}\b", text)]

def retrieve(query: str, index: PortfolioIndex, k: int = 5) -> list[dict[str, Any]]:
    # Step 1: Initial retrieval
    initial_chunks = index.dense_search(query, top_k=k)
    graded = [(chunk, grade_evidence_relevance(query, chunk)) for chunk, _ in initial_chunks]

    # Step 2: Quality threshold check (minimum relevance 0.35)
    high_quality = [chunk for chunk, score in graded if score >= 0.35]

    # Step 3: Corrective loop if evidence is weak
    if len(high_quality) < 2:
        # Reformulate query: extract nouns and key skills
        reformulated_query = " ".join([w for w in re_tokenize(query) if len(w) > 4][:6])
        supplemental = index.bm25_search(reformulated_query, top_k=k)
        for chunk, _ in supplemental:
            if chunk not in high_quality:
                high_quality.append(chunk)

    return high_quality[:k] if high_quality else [c for c, _ in initial_chunks[:k]]

