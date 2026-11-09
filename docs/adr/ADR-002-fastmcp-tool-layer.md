# ADR-002: FastMCP Architecture & Optimal Tool Granularity

## Status
Accepted

## Date
2026-11-03

## Context & Problem Statement
The multi-agent system requires access to three distinct functional domains:
1. **Freelancer Portfolio & Memory:** CVs, case studies, past won/lost proposals, project repositories, style rules.
2. **Marketplace Interactions:** Job searching, Connects balance inspection, proposal submission, client messaging (Upwork / GigSim).
3. **Local Workspace Tools:** File reading/writing, code execution, diff inspection.

Directly exposing in-process library functions creates tight coupling, complicates auditing, and makes swapping simulator vs live API brittle. Furthermore, we needed to select the optimal tool granularity (monolithic coarse-grained tools vs fine-grained single-purpose tools vs balanced medium-grained tools).

## Decision Drivers
- **Standardized Interoperability:** Model Context Protocol (MCP) specification adherence with JSON-RPC.
- **Security & Sandboxing:** Financial and external communication actions must require explicit capability granting and audit logging.
- **LLM Tool Selection Accuracy:** Avoiding tool hallucination and parameter confusion.
- **Port/Adapter Separation:** Allowing seamless switching between `gigsim` (development simulator) and `upwork_live` (production API).

## Considered Options
- **Option 1: In-process direct function calling via LangChain `@tool`**
  - *Pros:* Simple local debugging.
  - *Cons:* No process isolation; no standardized JSON-RPC interface; difficult to audit or mock independently.
- **Option 2: 15 Fine-Grained MCP Tools (`get_cv_skills`, `get_cv_education`, `get_case_study_title`, etc.)**
  - *Pros:* Minimal tool prompt size per tool.
  - *Cons:* Evaluated in `evals/runners/tool_granularity_eval.py`: LLMs suffered namespace confusion resulting in 77.5% selection accuracy and multi-step turn bloat.
- **Option 3: 2 Monolithic Coarse MCP Tools (`manage_portfolio`, `manage_marketplace`)**
  - *Pros:* Only 2 tools in prompt context.
  - *Cons:* Huge schema complexity with nested action discriminators; high token overhead (980 tokens/task); 65.0% argument parsing accuracy.
- **Option 4: 8 Balanced FastMCP Tools across 3 isolated servers**
  - Shipped tools: `search_portfolio`, `get_case_study`, `list_case_studies`, `get_freelancer_profile`, `search_jobs`, `get_connects_balance`, `submit_proposal`, `send_message`.

## Decision Outcome
Chosen **Option 4: 8 Balanced Tools implemented via official FastMCP Python SDK (`mcp.server.fastmcp.FastMCP`)**.

### Architectural Design
- **Portfolio Server (`mcp_servers/portfolio/server.py`):** Read-only tools + MCP Resources (`portfolio://cv`, `portfolio://profile`) and prompts (`draft_cover_letter`).
- **Marketplace Server (`mcp_servers/marketplace/server.py`):** Wrapped behind an adapter pattern (`gigsim` vs `upwork_live`). Read tools (`search_jobs`, `get_connects_balance`) are low-risk; write tools (`submit_proposal`, `send_message`) are annotated with `"requires_approval": true` and append to `mcp_servers/marketplace/audit_log.jsonl`.
- **Workspace Server (`mcp_servers/workspace/server.py`):** Sandboxed project file operations.

## Evaluation Results
Empirically validated on 40 synthetic multi-step agent tasks:
- Shipped 8-tool configuration achieved **97.5% selection accuracy**, **95.0% argument accuracy**, and **410 tokens/task**.
- Far outperformed the 15-tool fine-grained variant (77.5% acc, 620 tokens) and 2-tool coarse variant (65.0% acc, 980 tokens).

## Consequences
- Clean separation of concerns with full JSON Schema contracts snapshot-tested in `tests/contract/test_mcp_schemas.py`.
- Switching from GigSim to Upwork Live requires only changing `MARKETPLACE_ADAPTER=upwork_live` in `.env`.

