"""
Long-Term Memory Store for GigBid.
Maintains two persistent, tenant-scoped memory namespaces:
1. Style Memory: User-specific writing preferences and banned vocabulary learned from edits.
2. Outcome Memory: Proven proposal strategies and evidence pairings learned from client replies.
"""
import os
import json
from typing import Any, Optional
from agent.memory.promotion_rules import evaluate_style_promotion, evaluate_outcome_promotion

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR))
MEMORY_FILE = os.path.join(PROJECT_ROOT, "data", "processed", "long_term_memory.json")

class LongTermMemoryStore:
    def __init__(self, filepath: Optional[str] = None):
        self.filepath = filepath or MEMORY_FILE
        self.state = self._load()

    def _load(self) -> dict[str, Any]:
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "style_rules": [
                {"id": "style-01", "rule": "Never use the word 'passionate'; open directly with solution evidence.", "learned_from": "initial_preference"},
                {"id": "style-02", "rule": "Always lead with quantified benchmark numbers (e.g. latency, throughput).", "learned_from": "initial_preference"}
            ],
            "outcome_patterns": []
        }

    def _save(self):
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2)

    def get_style_guidelines(self) -> list[str]:
        return [item["rule"] for item in self.state.get("style_rules", [])]

    def get_outcome_insights(self, category: Optional[str] = None) -> list[dict[str, Any]]:
        patterns = self.state.get("outcome_patterns", [])
        if category:
            return [p for p in patterns if p.get("category") == category]
        return patterns

    def record_user_edit(self, original: str, edited: str) -> list[dict[str, Any]]:
        new_rules = evaluate_style_promotion(original, edited)
        for r in new_rules:
            # Prevent duplicate rules
            if not any(existing["rule"] == r["rule"] for existing in self.state["style_rules"]):
                r["id"] = f"style-{len(self.state['style_rules']) + 1:02d}"
                self.state["style_rules"].append(r)
        if new_rules:
            self._save()
        return new_rules

    def record_outcome(self, category: str, bid: float, outcome: str, evidence_ids: list[str]) -> Optional[dict[str, Any]]:
        insight = evaluate_outcome_promotion(category, bid, outcome, evidence_ids)
        if insight:
            insight["id"] = f"outcome-{len(self.state['outcome_patterns']) + 1:02d}"
            self.state["outcome_patterns"].append(insight)
            self._save()
        return insight

    def delete_rule(self, rule_id: str) -> bool:
        """Allows user to inspect and remove learned memories from the settings UI."""
        before = len(self.state.get("style_rules", []))
        self.state["style_rules"] = [r for r in self.state.get("style_rules", []) if r.get("id") != rule_id]
        if len(self.state["style_rules"]) < before:
            self._save()
            return True
        return False

# Global singleton
_memory_store = None

def get_memory_store() -> LongTermMemoryStore:
    global _memory_store
    if _memory_store is None:
        _memory_store = LongTermMemoryStore()
    return _memory_store

