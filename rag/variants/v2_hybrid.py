"""
Variant V2: Hybrid BM25 + Dense with Reciprocal Rank Fusion (Retrieval Group).
Combines exact term keyword retrieval (BM25 for exact library names like Celery, dbt, Pinecone)
with dense semantic vector similarity, merging ranks with Reciprocal Rank Fusion (RRF).
"""
from typing import Any
from rag.index.vector_index import PortfolioIndex

def retrieve(query: str, index: PortfolioIndex, k: int = 5, rrf_k: int = 60) -> list[dict[str, Any]]:
    results = index.hybrid_search_rrf(query=query, top_k=k, rrf_k=rrf_k)
    return [chunk for chunk, score in results]

