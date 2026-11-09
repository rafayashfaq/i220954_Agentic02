"""
Variant V0: Mandatory Baseline.
Naive dense retrieval: fixed chunks, top-k cosine similarity computed against the full raw job post text.
"""
from typing import Any
from rag.index.vector_index import PortfolioIndex

def retrieve(query: str, index: PortfolioIndex, k: int = 5) -> list[dict[str, Any]]:
    """Retrieve top-k chunks using dense cosine similarity on the raw job post."""
    results = index.dense_search(query=query, top_k=k)
    return [chunk for chunk, score in results]
