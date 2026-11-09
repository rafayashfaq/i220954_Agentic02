# GigBid System Architecture & Design Specification

GigBid is a production-grade multi-agent freelancer copilot designed to eliminate generic, ungrounded proposals and scam vulnerability while strictly preserving human authority over external platform actions.

## 1. High-Level Architecture Diagram

```
                 +-----------------------------------------+
                 |       Web App (React/Vite/TS)           |
                 |  Inbox | Studio | Pipeline | Run Viewer |
                 +--------------------+--------------------+
                                      | HTTP REST / SSE Stream
                                      v
                 +-----------------------------------------+
                 |          FastAPI Application            |
                 | Routers, Auth, Streaming, Checkpointers |
                 +--------------------+--------------------+
                                      |
         +----------------------------+----------------------------+
         |                                                         |
         v                                                         v
+-----------------------------+                           +-----------------------------+
|          BID GRAPH          |                           |     CONVERSATION GRAPH      |
|    (One Thread per Job)     |                           |    (Thread per Client)      |
+-----------------------------+                           +-----------------------------+
| 1. Scout Agent              |                           | 1. Client Liaison Agent     |
|    |                        |                           |    (Intent Classifier)      |
|    v                        |                           |    |                        |
| 2. Parallel Fan-Out:        |                           |    v                        |
|    - Job Analyst            |                           | 2. Workspace MCP Sync       |
|    - Risk Assessor          |                           |    (Calendar Slot Holds)    |
|    - Fit Matcher            |                           |    |                        |
|    |                        |                           |    v                        |
|    v                        |                           | 3. Human Approval Gate      |
| 3. Decision Node (Skip/Bid) |                           |    (interrupt())            |
|    | (if Bid)               |                           |    |                        |
|    v                        |                           |    v                        |
| 4. Pricing Strategist       |                           | 4. Send Approved Message    |
|    |                        |                           +-----------------------------+
|    v                        |
| 5. Proposal Writer          |
|    |                        |
|    v                        |
| 6. Claim Verifier           |
|    |                        |
|    v                        |
| 7. Critic Audit Loop        |
|    (Max 2 Revisions)        |
|    |                        |
|    v                        |
| 8. Compliance Guard         |
|    (PII & Policy Redaction) |
|    |                        |
|    v                        |
| 9. Human Approval Gate      |
|    (interrupt())            |
|    |                        |
|    v                        |
| 10. Submit Proposal Draft   |
+-----------------------------+
         |                                                         |
         +----------------------------+----------------------------+
                                      |
                                      v
                 +-----------------------------------------+
                 |            Marketplace Port             |
                 |      (Config-Switched Port Layer)       |
                 +--------------------+--------------------+
                                      |
                    +-----------------+-----------------+
                    |                                   |
                    v                                   v
+---------------------------------------+   +---------------------------------------+
|            GigSim Adapter             |   |           Upwork Live Adapter         |
|  (In-process / REST Simulator API)    |   |     (Official MCP / OAuth 2.1 PKCE)   |
+---------------------------------------+   +---------------------------------------+
```

## 2. Agent Roles and Allow-lists

Every agent is isolated to its declared MCP tool set:

| Role | Responsibility | Tools Permitted | Input Hand-off | Output Hand-off |
| :--- | :--- | :--- | :--- | :--- |
| **Scout** | Ingests job stream, deduplicates against seen jobs. | `search_jobs`, `get_job` | Raw feed | Raw Job Dict |
| **Job Analyst** | Extracts structured deliverables and skills. | *No tools* | Raw Job Dict | `JobSpec` |
| **Risk Assessor** | Scores scam likelihood, flags unpaid work and prompt injections. | `get_client_history`, `get_job` | Raw Job Dict | `RiskReport` |
| **Fit Matcher** | Maps deliverables to portfolio evidence, calculates fit score. | `search_evidence`, `get_case_study` | `JobSpec` | `FitReport` |
| **Pricing Strategist**| Determines competitive bid based on client ceiling & floor. | `get_job`, `get_connects_balance` | `JobSpec`, `FitReport` | `PriceQuote` |
| **Proposal Writer** | Drafts evidence-grounded cover letter and screening answers. | `search_evidence`, `get_case_study` | `JobSpec`, Evidence | `ProposalDraft` |
| **Claim Verifier** | Splits draft into atomic factual claims, verifies provenance. | *No tools* | `ProposalDraft`, Evidence | Verified `ProposalDraft` |
| **Critic** | Evaluates grounding and brevity; loops back if needed (max 2).| `get_case_study` | `ProposalDraft` | `Critique` |
| **Compliance Guard**| Redacts PII, guarantees, and off-platform solicitations. | *No tools* | `ProposalDraft` | `ComplianceVerdict` |
| **Client Liaison** | Classifies client message intent and prepares calendar holds. | `get_free_calendar_slots`, `create_tentative_hold` | Client Messages | `ConversationIntent` |

## 3. Strict State Discipline (C2)

GigBid explicitly enforces separation of three orthogonal data categories:
1. **Working State (`BidGraphState`)**: Volatile context required solely for active thread transitions (e.g. current draft, scores, step counters).
2. **Execution Traces (`execution_traces`)**: Append-only list of every tool call, argument, latency timestamp, and intermediate output kept for auditing and replay.
3. **Long-Term Memory (`LongTermMemoryStore`)**: Promoted, curated insights governed by explicit rules. Raw tool output NEVER enters memory directly.

## 4. Human-in-the-Loop & Durability Guarantee (C5, C6)

External write operations (proposal submissions, connects spending, and outbound messages) execute ONLY after passing an `interrupt()` gate:
- The approval payload carries the complete draft, cited evidence IDs, risk analysis, pricing rationale, and dry-run preview.
- State is persisted via SQLite / Postgres checkpointers (`AsyncSqliteSaver`). If the API crashes or restarts while an approval is pending, restarting the server restores the thread at the exact interrupt node without data loss or double-spending.
