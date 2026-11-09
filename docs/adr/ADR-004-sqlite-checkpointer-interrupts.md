# ADR-004: Durable Human-in-the-Loop Approval via SQLite Checkpointing and Native Interrupts

## Status
Accepted

## Date
2026-11-04

## Context & Problem Statement
In automated freelancing, actions such as submitting a bid, spending non-refundable platform credits (Connects), and dispatching messages to prospective clients have immediate irreversible real-world and financial consequences. To satisfy the prompt-to-submit safety barrier, every outbound action must halt and await human verification. However, humans do not respond instantaneously: a freelancer might review an automated draft minutes or days after the scout identified the opportunity. Furthermore, daemon workers and server processes can crash, restart, or deploy during these waiting windows.

## Decision Drivers
- **Guaranteed Human Gatekeeping:** Zero autonomous submissions without explicit cryptographically logged approval.
- **Process Durability:** Complete preservation of graph execution state, handoffs, and traces across process restarts.
- **Stateless Web API Compatibility:** Allowing REST/SSE endpoints to inspect paused runs and resume them seamlessly with user edits.
- **Replayability & Auditability:** Ability to time-travel or inspect previous node states.

## Considered Options
- **Option 1: In-memory pause via Python `asyncio.Event` or `threading.Event`**
  - *Pros:* Simple local implementation.
  - *Cons:* Complete state loss on worker restart; cannot distribute across multiple worker instances; memory leaks for pending approvals.
- **Option 2: External Task Queue with Manual State Serialization (e.g. Celery + Redis)**
  - *Pros:* Decoupled task dispatch.
  - *Cons:* Tedious manual re-hydration of multi-agent execution context; high complexity in branching/joining graphs.
- **Option 3: LangGraph Native `interrupt()` with SQLite Checkpointer (`SqliteSaver` / `AsyncSqliteSaver` / `MemorySaver` in-memory fallback)**
  - *Pros:* Standardized LangGraph checkpoint protocol; graph execution suspends cleanly at node boundaries; native `graph.stream(Command(resume=...))` resumes from the exact snapshot.
  - *Cons:* Requires managing thread IDs and database schemas.

## Decision Outcome
Chosen **Option 3: Native `interrupt()` paired with SQLite Checkpointing**.

### Implementation Details
1. **Interrupt Trigger:**
   The `bid_graph` contains an explicit conditional routing node `approval_gate`:
   ```python
   # Inside agent/graphs/bid_graph.py
   approval_request = interrupt({
       "type": "proposal_approval",
       "job_id": state["job_spec"].job_id,
       "proposal": state["proposal_draft"].model_dump(),
       "compliance": state["compliance_verdict"].model_dump(),
   })
   ```
2. **Persistence Layer:**
   Configured with persistent SQLite storage `agent_state.db` using `langgraph-checkpoint-sqlite`.
3. **Resume via REST API:**
   The approval endpoint (`apps/api/routers/approvals.py`) accepts `approve`, `reject`, or `edit` actions:
   ```python
   graph.stream(Command(resume={"action": "approve", "edited_proposal": ...}), config={"configurable": {"thread_id": thread_id}})
   ```
4. **Crash-Resilience Verification:**
   Verified in `tests/integration/test_graph_flow.py::test_crash_and_resume_durability`, where a running graph is paused at interrupt, the in-memory graph instance is discarded, a new graph is instantiated against the SQLite database, and the pipeline resumes to completion without data loss.

## Consequences
- **Positive:**
  - Guaranteed 100% human-in-the-loop compliance: not a single proposal reaches `submit_proposal` without user confirmation.
  - Freelancers can edit proposal text or adjust pricing directly in the Proposal Studio UI; the edited payload is injected into the resumed state.
  - Zero state loss during server deployments or container restarts.
- **Negative:**
  - SQLite database locks require proper connection management and async driver (`aiosqlite`) configuration.
