# GigBid Operations & Deployment Runbook

## 1. Local Development Setup

### Prerequisites
- Python 3.11+
- Node.js 20+ & npm
- Docker & Docker Compose (optional for containerized deployment)

### Initial Setup
```bash
# Clone and install dependencies
python -m pip install -e ".[dev]"
pip install mcp langchain-mcp-adapters scikit-learn langgraph-checkpoint-sqlite aiosqlite

# Generate seed datasets & corpora
python data/generate_dataset.py

# Run Unit, MCP Contract, and Integration Tests
pytest tests/ mcp_servers/ -v
```

### Running Services
```bash
# Terminal 1: GigSim Simulator
python -m gigsim.server

# Terminal 2: FastAPI Backend API
uvicorn apps.api.main:app --port 8000 --reload

# Terminal 3: React / Vite Web Interface
cd apps/web && npm install && npm run dev

# Terminal 4: Background Scouting Worker
python worker/worker.py
```

## 2. Background Polling Intervals & Live Mode Schedule Justification

- **GigSim Mode**: Polling interval is set to **60 seconds** for interactive evaluation and grading.
- **Live Upwork Mode**: Polling interval is strictly configured to **15 minutes (900 seconds)** with exponential backoff on jitter:
  - *Justification*: Upwork Terms of Service strictly forbid rapid scraping or robotic polling. Polling every 15 minutes respects the 40 requests/hour safe threshold, prevents IP rate-limiting, and minimizes API token consumption.

## 3. Idempotency & Worker Crash Recovery

- Every write operation requires an `idempotency_key` (UUID v4) hashed with the `job_id`.
- The Marketplace MCP server maintains an append-only set of executed idempotency keys.
- If the background worker or web server crashes and restarts mid-run, replayed tasks identify prior keys and return the existing submission record without double-charging Connects or double-posting proposals.

## 4. Degraded Mode & Fault Recovery

When upstream marketplace services fail (e.g. simulated 503 or network drop):
1. The API catches the `HTTPException(503)` and enters degraded mode.
2. The UI immediately displays the **Marketplace Degraded Mode Banner**.
3. Outbound submissions are parked in persistent SQLite checkpoints.
4. Once the marketplace recovers, approving in the UI or restarting the worker drains the pending queue cleanly.
