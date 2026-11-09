# Tools Documentation & MCP Surface

Every agent interaction with external systems (Marketplace, Portfolio, Workspace, GitHub, Upwork) flows through strongly-typed Model Context Protocol (MCP) tools with declared schemas, idempotency semantics, and strict access controls.

## Complete MCP Tools Matrix

| Tool Name | MCP Server | Operation Type | Schema & Annotations | Auth / Access Control | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `search_evidence` | `portfolio` | Read-only | `readOnlyHint: true`<br>`idempotentHint: true` | None (Local portfolio) | Searches portfolio evidence items (case studies, repos, proposals) matching a requirement. |
| `get_case_study` | `portfolio` | Read-only | `readOnlyHint: true`<br>`idempotentHint: true` | None (Local portfolio) | Fetches complete text, problem statement, architecture, and verified metrics for a case study. |
| `list_skills` | `portfolio` | Read-only | `readOnlyHint: true`<br>`idempotentHint: true` | None (Local portfolio) | Enumerates all verified technical skills present across the freelancer's portfolio. |
| `search_jobs` | `marketplace` | Read-only | `readOnlyHint: true`<br>`idempotentHint: true` | Bearer Token, 30 req/min | Searches active marketplace jobs by keywords or filters. |
| `get_job` | `marketplace` | Read-only | `readOnlyHint: true`<br>`idempotentHint: true` | Bearer Token, 30 req/min | Retrieves full JobSpec, client ID, budget range, connects cost, and screening questions. |
| `get_client_history` | `marketplace` | Read-only | `readOnlyHint: true`<br>`idempotentHint: true` | Bearer Token, 30 req/min | Inspects client past projects, total spend, rating, and payment verification status. |
| `get_connects_balance` | `marketplace` | Read-only | `readOnlyHint: true`<br>`idempotentHint: true` | Bearer Token, 30 req/min | Checks available Connects balance and spending history. |
| `list_messages` | `marketplace` | Read-only | `readOnlyHint: true`<br>`idempotentHint: true` | Bearer Token, 30 req/min | Retrieves message threads and incoming client replies. |
| `create_proposal_draft` | `marketplace` | Read / Write | `readOnlyHint: false`<br>`destructiveHint: false`<br>`idempotentHint: true` | Bearer Token, 30 req/min | Creates a proposal draft or simulates submission when `dry_run=true`. |
| `submit_proposal` | `marketplace` | Write (Destructive) | `readOnlyHint: false`<br>`destructiveHint: true`<br>`idempotentHint: true` | Bearer Token, Idempotency Key | Submits approved proposal to marketplace and deducts Connects. Protected by LangGraph `interrupt()`. |
| `send_message` | `marketplace` | Write (Destructive) | `readOnlyHint: false`<br>`destructiveHint: true`<br>`idempotentHint: true` | Bearer Token, Idempotency Key | Sends approved reply or proposed interview slots to a client thread. |
| `get_free_calendar_slots` | `workspace` | Read-only | `readOnlyHint: true`<br>`idempotentHint: true` | Local Workspace Sandbox | Returns available freelancer interview windows in ISO 8601 format. |
| `create_tentative_hold` | `workspace` | Write | `readOnlyHint: false`<br>`destructiveHint: false` | Local Workspace Sandbox | Creates tentative hold on freelancer calendar for prospective client interview. |
| `create_email_draft` | `workspace` | Write | `readOnlyHint: false`<br>`destructiveHint: false` | Local Workspace Sandbox | Prepares draft follow-up email in freelancer's workspace inbox. |
| `get_repo_contents` | `github` (3rd party) | Read-only | `readOnlyHint: true`<br>`idempotentHint: true` | GitHub Personal Access Token | Ingests repository READMEs, architectures, and sample code for automated case study verification. |
| `upwork_mcp_gateway` | `upwork` (3rd party) | Read / Draft-only | `readOnlyHint: false`<br>`destructiveHint: false` | OAuth 2.1 PKCE Per-Tenant | Connects to official Upwork MCP server (`https://mcp.upwork.com/mcp`) creating platform drafts only. |

## Third-Party MCP Server Trust Rationales (A5)

1. **Official Upwork MCP Server (`https://mcp.upwork.com/mcp`)**:
   - *Trust Rationale*: Managed and authenticated directly by Upwork Global Inc. under OAuth 2.1 PKCE with per-user scoped tokens. All write endpoints strictly enforce draft creation rather than direct submission, guaranteeing platform safety compliance.
2. **GitHub MCP Server (`github/mcp-server`)**:
   - *Trust Rationale*: Read-only ingestion token with restricted repository-read scope (`repo:read`), sandboxed strictly to the freelancer's public or explicitly shared portfolio repositories without write or administrative permissions.

## Client Discipline & Agent Allow-lists (A6)

Each agent in the LangGraph graph is strictly limited to an explicit allow-list of tools:

- **Scout**: `search_jobs`, `get_job`
- **Job Analyst**: *No tools* (pure structured extraction from raw text)
- **Risk Assessor**: `get_client_history`, `get_job`
- **Fit Matcher**: `search_evidence`, `get_case_study`, `list_skills`
- **Pricing Strategist**: `get_job`, `get_client_history`, `get_connects_balance`
- **Proposal Writer**: `get_case_study`, `search_evidence`
- **Critic / Verifier**: `search_evidence`, `get_case_study`
- **Compliance Guard**: *No tools* (pure deterministic policy enforcement)
- **Client Liaison**: `list_messages`, `send_message` (after approval), `get_free_calendar_slots`, `create_tentative_hold`

## Degraded Mode Behavior
If the marketplace server is killed or becomes unreachable (503 Service Unavailable / connection failure):
1. The API catches the upstream failure and transitions the system to degraded mode.
2. The UI displays an alert banner: `"Marketplace connection degraded: Actions are queued for automatic recovery"`.
3. Outbound calls are queued idempotently and replayed once the marketplace server recovers, without dropping user approvals or double-charging Connects.
