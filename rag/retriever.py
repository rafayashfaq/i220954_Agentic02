"""
Retriever Factory for GigBid RAG variants.
Permits selecting and testing variants via configuration:
- v0_naive
- v1_decomposition
- v2_hybrid (default shipped)
- v3_reranker
- v4_outcome_aware
- v8_self_rag
"""
import os
import yaml
from typing import Any, Optional
from rag.ingest.loader import PortfolioIngestionLoader
from rag.index.vector_index import PortfolioIndex
from rag.variants import (
    v0_naive,
    v1_decomposition,
    v2_hybrid,
    v3_reranker,
    v4_outcome_aware,
    v8_self_rag
)

VARIANTS = {
    "v0_naive": v0_naive.retrieve,
    "v1_decomposition": v1_decomposition.retrieve,
    "v2_hybrid": v2_hybrid.retrieve,
    "v3_reranker": v3_reranker.retrieve,
    "v4_outcome_aware": v4_outcome_aware.retrieve,
    "v8_self_rag": v8_self_rag.retrieve,
}

# Cache indexes per persona
INDEX_CACHE: dict[str, PortfolioIndex] = {}

def get_portfolio_index(persona_key: str = "ai_engineer") -> PortfolioIndex:
    if persona_key not in INDEX_CACHE:
        loader = PortfolioIngestionLoader()
        chunks = loader.load_all_chunks(persona_key=persona_key)
        INDEX_CACHE[persona_key] = PortfolioIndex(chunks=chunks)
    return INDEX_CACHE[persona_key]

class ConfiguredRetriever:
    def __init__(self, variant: Optional[str] = None, persona_key: str = "ai_engineer"):
        self.variant = variant or self._load_variant_from_config()
        self.persona_key = persona_key
        self.retrieve_fn = VARIANTS.get(self.variant, v2_hybrid.retrieve)

    def _load_variant_from_config(self) -> str:
        cfg_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "agent", "config.yaml")
        if os.path.exists(cfg_path):
            try:
                with open(cfg_path, "r", encoding="utf-8") as f:
                    cfg = yaml.safe_load(f)
                    return cfg.get("rag", {}).get("variant", "v2_hybrid")
            except Exception:
                pass
        return "v2_hybrid"

    def retrieve(self, query: str, k: int = 5) -> list[dict[str, Any]]:
        index = get_portfolio_index(self.persona_key)
        return self.retrieve_fn(query=query, index=index, k=k)

def get_retriever(variant: Optional[str] = None, persona_key: str = "ai_engineer") -> ConfiguredRetriever:
    return ConfiguredRetriever(variant=variant, persona_key=persona_key)

