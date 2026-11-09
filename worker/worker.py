"""
Background Task Worker for Scheduled Scouting & Agent Runs.
Executes outside of web request lifecycles.
Polls saved searches at conservative intervals (e.g. every 15 minutes),
deduplicates jobs idempotently, and triggers background bid graph runs.
"""
import asyncio
import os
import sys
import uuid
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from agent.marketplace_port import get_marketplace_port
from agent.graphs.bid_graph import build_bid_graph

PROCESSED_JOB_IDS: set[str] = set()
POLL_INTERVAL_SECONDS = int(os.getenv("SCOUT_POLL_INTERVAL", "60"))

async def run_scout_cycle():
    """Polls marketplace, deduplicates, and runs analysis for newly detected jobs."""
    port = get_marketplace_port()
    print(f"[{datetime.utcnow().isoformat()}] Worker: Starting scouting cycle...")
    
    try:
        jobs = await port.search_jobs(query="Python", limit=10)
    except Exception as e:
        print(f"Worker scouting failed (upstream error or degraded mode): {e}")
        return

    graph = build_bid_graph()

    for job in jobs:
        job_id = job.get("job_id")
        if not job_id or job_id in PROCESSED_JOB_IDS:
            continue

        PROCESSED_JOB_IDS.add(job_id)
        print(f"Worker: Queued new job {job_id} for analysis...")

        # Run bid graph in background
        config = {"configurable": {"thread_id": f"worker-thread-{job_id}"}}
        try:
            await graph.ainvoke({
                "job": job,
                "persona_key": "ai_engineer"
            }, config=config)
            print(f"Worker: Job {job_id} processed up to approval gate.")
        except Exception as err:
            print(f"Worker error processing job {job_id}: {err}")

async def main():
    print("Starting GigBid Background Worker daemon...")
    while True:
        await run_scout_cycle()
        await asyncio.sleep(POLL_INTERVAL_SECONDS)

if __name__ == "__main__":
    asyncio.run(main())

