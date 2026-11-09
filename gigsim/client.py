"""
GigSim Python Client:
Provides unified async access to GigSim either in-process (for fast testing/evals)
or over HTTP (when running in containerized/separate service mode).
"""
import os
import httpx
from typing import Any, Optional
from gigsim import app, state

class GigSimClient:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or os.getenv("GIGSIM_URL", "http://127.0.0.1:8001")
        self.in_process = os.getenv("GIGSIM_IN_PROCESS", "true").lower() == "true"
        self._async_client = None

    async def get_client(self) -> httpx.AsyncClient:
        if self._async_client is None:
            if self.in_process:
                transport = httpx.ASGITransport(app=app)
                self._async_client = httpx.AsyncClient(transport=transport, base_url="http://test")
            else:
                self._async_client = httpx.AsyncClient(base_url=self.base_url, timeout=10.0)
        return self._async_client

    async def search_jobs(self, query: str = "", limit: int = 50) -> list[dict[str, Any]]:
        client = await self.get_client()
        resp = await client.get("/jobs", params={"query": query, "limit": limit})
        resp.raise_for_status()
        return resp.json()

    async def get_job(self, job_id: str) -> dict[str, Any]:
        client = await self.get_client()
        resp = await client.get(f"/jobs/{job_id}")
        resp.raise_for_status()
        return resp.json()

    async def get_client_history(self, client_id: str) -> dict[str, Any]:
        client = await self.get_client()
        resp = await client.get(f"/clients/{client_id}")
        resp.raise_for_status()
        return resp.json()

    async def get_connects_balance(self) -> dict[str, Any]:
        client = await self.get_client()
        resp = await client.get("/connects")
        resp.raise_for_status()
        return resp.json()

    async def create_proposal_draft(self, payload: dict[str, Any]) -> dict[str, Any]:
        client = await self.get_client()
        resp = await client.post("/proposals/draft", json=payload)
        resp.raise_for_status()
        return resp.json()

    async def submit_proposal(self, payload: dict[str, Any], idempotency_key: str) -> dict[str, Any]:
        client = await self.get_client()
        data = {**payload, "idempotency_key": idempotency_key}
        resp = await client.post("/proposals/submit", json=data)
        resp.raise_for_status()
        return resp.json()

    async def get_messages(self, thread_id: Optional[str] = None) -> list[dict[str, Any]]:
        client = await self.get_client()
        params = {"thread_id": thread_id} if thread_id else {}
        resp = await client.get("/messages", params=params)
        resp.raise_for_status()
        return resp.json()

    async def send_message(self, client_id: str, body: str, idempotency_key: str, proposed_slots: list[str] = None, thread_id: str = None) -> dict[str, Any]:
        client = await self.get_client()
        payload = {
            "client_id": client_id,
            "thread_id": thread_id,
            "body": body,
            "proposed_slots": proposed_slots or [],
            "idempotency_key": idempotency_key
        }
        resp = await client.post("/messages", json=payload)
        resp.raise_for_status()
        return resp.json()

