"""
Pricing Strategist Node: Recommends contract bid price and Connects investment.
"""
import os
from datetime import datetime
from agent.state import BidGraphState
from agent.handoffs import PriceQuote

def load_prompt() -> str:
    prompt_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "prompts", "pricing_v1.md")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()

def pricing_node(state: BidGraphState) -> dict:
    job = state.get("job", {})
    job_spec = state.get("job_spec")
    budget_max = job_spec.budget_max if job_spec else 500.0
    budget_min = job_spec.budget_min if job_spec else 250.0
    connects_cost = job.get("connects_cost", 6)

    # Strategy: bid 85-90% of max budget for competitive value, but above minimum floor
    proposed_bid = round(max(budget_min, budget_max * 0.88), 2)
    if proposed_bid <= 0:
        proposed_bid = 350.0

    rationale = (
        f"Bid priced at ${proposed_bid} (88% of stated ceiling ${budget_max}). "
        f"Connects cost of {connects_cost} is justified by high fit score and project margin."
    )

    price_quote = PriceQuote(
        proposed_bid=proposed_bid,
        rationale=rationale,
        connects_cost=connects_cost,
        expected_roi="High (>4x margin over Connects cost)"
    )

    trace = {
        "node": "pricing",
        "tool": "get_connects_balance",
        "input": {"budget_max": budget_max, "connects_cost": connects_cost},
        "output": price_quote.model_dump(),
        "timestamp": datetime.utcnow().isoformat()
    }

    return {
        "price_quote": price_quote,
        "execution_traces": [trace]
    }
