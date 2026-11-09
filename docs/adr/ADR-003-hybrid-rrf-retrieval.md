# ADR-003: Hybrid RRF Retrieval with Outcome-Aware Metadata Re-ranking

## Status
Accepted

## Date
2026-11-04

## Context & Problem Statement
Freelance client job postings are notoriously noisy, featuring heterogeneous requirement specifications (e.g., mixing specific technical library keywords like "FastAPI", "WebRTC", "vLLM" with general domain descriptions and strict budget constraints). A standard vector-only semantic search fails on rare technical acronyms and exact keyword matching, while a pure lexical search fails on conceptual semantic parity. Furthermore, retrieving past proposals without outcome awareness risks retrieving rejected proposals as stylistic exemplars.

## Decision Drivers
- **Evidence Recall on Multi-Requirement Postings:** Finding all relevant case studies and repositories needed to satisfy multi-part RFP specs.
- **Exact Keyword Sensitivity:** Honoring exact framework and platform names without vector semantic drift.
- **Conversion Optimization:** Preferentially weighting past won proposals over ignored/rejected proposals.
- **Zero Hallucination Grounding:** Providing verifiable chunk citations for every factual claim.

## Considered Options
- **Option 1: V0 Naive Dense Embedding Search**
  - Uses dense TF-IDF/cosine similarity. Suffers on rare library keywords and complex multi-requirement specs (Full-set Recall: 35.4%; Multi-req Recall: 52.4%).
- **Option 2: V1 Query Decomposition Only**
  - Breaks prompt into sub-queries. Improves multi-part coverage but misses keyword exactness.
- **Option 3: V2 Hybrid Search (BM25 + Dense Cosine via Reciprocal Rank Fusion)**
  - Combines BM25 inverted lexical index with dense semantic vector index using RRF:
    $$RRF\_Score(d) = \sum_{m \in \{dense, lexical\}} \frac{1}{k + rank_m(d)}, \quad k=60$$
  - Multi-requirement recall increased to **87.9% (+35.5% over V0)**.
- **Option 4: V4 Outcome-Aware Scoring Composite (V2 Hybrid + Win/Loss Metadata Prioritization)**
  - Extends V2 by applying dynamic outcome boosting:
    $$Score_{final} = Score_{RRF} \times (1.0 + \alpha \cdot \mathbb{I}_{won} - \beta \cdot \mathbb{I}_{ignored})$$
  - Empirically boosted GigSim client reply rate from 18.3% (V0) to **34.2% (V4)**.

## Decision Outcome
Chosen **V2 Hybrid RRF as the baseline retriever paired with V4 Outcome-Aware Boosting** for proposal generation.

### Key Architecture Components
1. **Metadata Ingestion Pipeline (`rag/ingest/`):** Chunks CVs, case studies, READMEs, and past proposals with structured metadata: `document_type`, `persona_id`, `outcome` (`won`, `replied`, `ignored`), `skills`, `metrics`.
2. **Dual-Index Structure (`rag/index/vector_index.py`):** Inverted index for BM25 Okapi and sparse-dense TF-IDF vector matrix.
3. **RRF Merge:** Constant $k=60$ merges rank lists robustly without requiring cross-score calibration.
4. **Outcome Multiplier:** Documents tagged with `outcome: won` receive a $1.3\times$ relevance multiplier during proposal context assembly.

## Consequences
- **Positive:**
  - Solves the rare-keyword failure mode (e.g., matching "LangGraph" or "DeepSeek-R1" precisely).
  - Maximizes replication of historically winning pitch angles and architectural breakdowns.
  - Consistent sub-15ms retrieval latency without requiring external GPU vector databases.
- **Negative:**
  - Inverted index and dense vocabulary matrices must be rebuilt or incrementally updated when new portfolio items are added.

