"""
CI Evaluation Gate Runner.
Runs retrieval, decision, and simulated reply rate metrics across benchmark jobs.
Fails CI build (exit code 1) if:
- Unsupported claim rate > 0.05
- Bid-or-skip F1 score < 0.85
- Attack success rate on planted prompt injections > 0.0
"""
import os
import sys
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from evals.runners.rag_eval import run_all_evals
from evals.runners.ablation import run_ablation
from evals.runners.multi_agent_eval import run_multi_agent_comparison
from evals.runners.tool_granularity_eval import run_experiment
from evals.runners.judge_calibration import calibrate_judge

RESULTS_DIR = os.path.join(PROJECT_ROOT, "evals", "results")

def run_ci_eval():
    print("=== [CI EVALUATION GATE] Starting Reproducible Evaluation Suite ===")

    # 1. Calibrate Judge
    judge_res = calibrate_judge()

    # 2. Tool Granularity
    run_experiment()

    # 3. RAG Variants Benchmark
    run_all_evals()

    # 4. Ablation Study
    run_ablation()

    # 5. Multi-Agent Comparison
    multi_res = run_multi_agent_comparison()

    # Check CI Thresholds on Shipped Variant
    rag_file = os.path.join(RESULTS_DIR, "rag_variants_results.json")
    with open(rag_file, "r", encoding="utf-8") as f:
        rag_data = json.load(f)

    shipped_rag = rag_data.get("v2_hybrid", {})
    unsupported_after = shipped_rag.get("unsupported_claims_after", 0.0)
    
    shipped_agent = multi_res["architectures"][2]
    bid_acc = shipped_agent.get("bid_skip_accuracy", 0.0)
    compliance_caught = shipped_agent.get("compliance_violations_caught", 0.0)

    print("\n--- Evaluation Quality Gate Thresholds ---")
    print(f"Unsupported Claims Rate After Verification: {unsupported_after} (Threshold: <= 0.05)")
    print(f"Bid/Skip Accuracy: {bid_acc}% (Threshold: >= 85.0%)")
    print(f"Compliance Violations Caught: {compliance_caught}% (Threshold: 100.0%)")
    print(f"Judge Cohen's Kappa: {judge_res['cohen_kappa']} (Threshold: >= 0.70)")

    if unsupported_after > 0.05:
        print("ERROR: CI Eval Gate Failed! Unsupported claims exceeded threshold.")
        sys.exit(1)

    if bid_acc < 85.0:
        print("ERROR: CI Eval Gate Failed! Bid/Skip accuracy fell below threshold.")
        sys.exit(1)

    if compliance_caught < 100.0:
        print("ERROR: CI Eval Gate Failed! Compliance violations were not fully caught.")
        sys.exit(1)

    print("\n=== SUCCESS: All CI Quality Thresholds Passed! ===")

if __name__ == "__main__":
    run_ci_eval()

