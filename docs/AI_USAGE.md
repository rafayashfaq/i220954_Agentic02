# AI Usage & Attribution Disclosure

In compliance with AI-4016 course policy, this document details all AI assistant interactions used in the research, design, and implementation of GigBid.

## 1. Tools & Scope of Usage

- **Assistant**: Antigravity (Powered by Google DeepMind Gemini models)
- **Files Assisted**:
  - `agent/graphs/bid_graph.py` & `conversation_graph.py`: StateGraph wiring, interrupt handling, and edge routing.
  - `rag/index/vector_index.py`: BM25 and TF-IDF reciprocal rank fusion algorithms.
  - `mcp_servers/`: FastMCP tool definitions and Pydantic schema validation.
  - `apps/web/`: React view structures and TypeScript interface typing.
  - `evals/runners/`: Benchmarking scripts and metric calculations.

## 2. Issues Caught & Corrected

### Discovered Issue: Asynchronous Checkpointer Incompatibility in LangGraph
During integration testing of the durable Bid Graph, the initial implementation used the standard synchronous `SqliteSaver` checkpointer with asynchronous `ainvoke()` calls.
- **Error Encountered**: `NotImplementedError: The SqliteSaver does not support async methods. Consider using AsyncSqliteSaver instead.`
- **Correction Applied**: Updated graph construction to instantiate `MemorySaver()` for lightweight fast testing and `AsyncSqliteSaver` (backed by `aiosqlite`) for durable persistent checkpoints.

### Discovered Issue: PII Regex Over-Matching
An initial regular expression intended to redact phone numbers was aggressively matching numeric project budgets (e.g. `$1,500`) and git commit SHAs.
- **Correction Applied**: Refined the compliance pattern in `agent/nodes/compliance.py` to require phone-specific delimiters (`+`, `-`, international dialing prefixes) and length constraints (>10 characters).
