"""
Marketplace Port: The single internal interface for marketplace access.
Switched via configuration (`agent/config.yaml` or environment variable):
- GigSimAdapter (default for local development, simulation, grading)
- UpworkLiveAdapter (for live Upwork MCP server)
"""
import os
import yaml
from typing import Protocol, Any, Optional
from mcp_servers.marketplace.schemas import (
    SearchJobsInput, GetJobInput, GetClientHistoryInput,
    CreateProposalDraftInput, SubmitProposalInput, SendMessageInput
)
from mcp_servers.marketplace.adapters.gigsim import GigSimAdapter
from mcp_servers.marketplace.adapters.upwork_live import UpworkLiveAdapter

class MarketplacePort(Protocol):
    async def search_jobs(self, query: str = "", limit: int = 20) -> list[dict[str, Any]]: ...
    async def get_job(self, job_id: str) -> dict[str, Any]: ...
    async def get_client_history(self, client_id: str) -> dict[str, Any]: ...
    async def get_connects_balance(self) -> dict[str, Any]: ...
    async def list_messages(self, thread_id: Optional[str] = None) -> list[dict[str, Any]]: ...
    async def create_proposal_draft(self, payload: dict[str, Any]) -> dict[str, Any]: ...
    async def submit_proposal(self, payload: dict[str, Any], idempotency_key: str) -> dict[str, Any]: ...
    async def send_message(self, client_id: str, body: str, idempotency_key: str, proposed_slots: list[str] = None, thread_id: str = None) -> dict[str, Any]: ...

class ConfiguredMarketplacePort:
    def __init__(self, mode: Optional[str] = None):
        self.mode = mode or self._detect_mode()
        if self.mode == "upwork_live":
            self.adapter = UpworkLiveAdapter()
        else:
            self.adapter = GigSimAdapter()

    def _detect_mode(self) -> str:
        # Check environment first
        env_mode = os.getenv("MARKETPLACE_MODE")
        if env_mode:
            return env_mode.lower()

        # Check agent/config.yaml
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    cfg = yaml.safe_load(f)
                    return cfg.get("marketplace", {}).get("mode", "gigsim").lower()
            except Exception:
                pass
        return "gigsim"

    async def search_jobs(self, query: str = "", limit: int = 20) -> list[dict[str, Any]]:
        return await self.adapter.search_jobs(SearchJobsInput(query=query, limit=limit))

    async def get_job(self, job_id: str) -> dict[str, Any]:
        return await self.adapter.get_job(GetJobInput(job_id=job_id))

    async def get_client_history(self, client_id: str) -> dict[str, Any]:
        return await self.adapter.get_client_history(GetClientHistoryInput(client_id=client_id))

    async def get_connects_balance(self) -> dict[str, Any]:
        return await self.adapter.get_connects_balance()

    async def list_messages(self, thread_id: Optional[str] = None) -> list[dict[str, Any]]:
        return await self.adapter.list_messages(thread_id=thread_id)

    async def create_proposal_draft(self, payload: dict[str, Any]) -> dict[str, Any]:
        inp = CreateProposalDraftInput(**payload)
        return await self.adapter.create_proposal_draft(inp)

    async def submit_proposal(self, payload: dict[str, Any], idempotency_key: str) -> dict[str, Any]:
        data = {**payload, "idempotency_key": idempotency_key}
        inp = SubmitProposalInput(**data)
        return await self.adapter.submit_proposal(inp)

    async def send_message(self, client_id: str, body: str, idempotency_key: str, proposed_slots: list[str] = None, thread_id: str = None) -> dict[str, Any]:
        inp = SendMessageInput(
            client_id=client_id,
            body=body,
            idempotency_key=idempotency_key,
            proposed_slots=proposed_slots or [],
            thread_id=thread_id
        )
        return await self.adapter.send_message(inp)

def get_marketplace_port(mode: Optional[str] = None) -> ConfiguredMarketplacePort:
    """Factory method to get the active marketplace port instance."""
    return ConfiguredMarketplacePort(mode=mode)
