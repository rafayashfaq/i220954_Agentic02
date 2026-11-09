"""
GigSim Marketplace Adapter.
Implements the marketplace operations against GigSim API simulator.
"""
from typing import Any, Optional
from gigsim.client import GigSimClient
from mcp_servers.marketplace.schemas import (
    SearchJobsInput, GetJobInput, GetClientHistoryInput,
    CreateProposalDraftInput, SubmitProposalInput, SendMessageInput
)

class GigSimAdapter:
    def __init__(self):
        self.client = GigSimClient()

    async def search_jobs(self, inp: SearchJobsInput) -> list[dict[str, Any]]:
        return await self.client.search_jobs(query=inp.query, limit=inp.limit)

    async def get_job(self, inp: GetJobInput) -> dict[str, Any]:
        return await self.client.get_job(job_id=inp.job_id)

    async def get_client_history(self, inp: GetClientHistoryInput) -> dict[str, Any]:
        return await self.client.get_client_history(client_id=inp.client_id)

    async def get_connects_balance(self) -> dict[str, Any]:
        return await self.client.get_connects_balance()

    async def list_messages(self, thread_id: Optional[str] = None) -> list[dict[str, Any]]:
        return await self.client.get_messages(thread_id=thread_id)

    async def create_proposal_draft(self, inp: CreateProposalDraftInput) -> dict[str, Any]:
        return await self.client.create_proposal_draft(inp.model_dump())

    async def submit_proposal(self, inp: SubmitProposalInput) -> dict[str, Any]:
        return await self.client.submit_proposal(inp.model_dump(), idempotency_key=inp.idempotency_key)

    async def send_message(self, inp: SendMessageInput) -> dict[str, Any]:
        return await self.client.send_message(
            client_id=inp.client_id,
            body=inp.body,
            idempotency_key=inp.idempotency_key,
            proposed_slots=inp.proposed_slots,
            thread_id=inp.thread_id
        )

