#!/usr/bin/env python3
"""Print a summary of LLM call costs from the cost log (llm_costs.jsonl)."""

import json
import os
import sys
from collections import defaultdict


def main() -> None:
    log_path = os.getenv("LLM_COST_LOG", "llm_costs.jsonl")
    if not os.path.exists(log_path):
        print(f"No cost log found at: {log_path}")
        sys.exit(0)

    totals: dict[str, dict] = defaultdict(
        lambda: {"calls": 0, "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0}
    )

    with open(log_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                m = entry.get("model", "unknown")
                totals[m]["calls"]         += 1
                totals[m]["input_tokens"]  += entry.get("input_tokens", 0)
                totals[m]["output_tokens"] += entry.get("output_tokens", 0)
                totals[m]["cost_usd"]      += entry.get("cost_usd", 0.0)
            except (json.JSONDecodeError, KeyError):
                continue

    if not totals:
        print("No valid entries in cost log.")
        return

    col = "{:<32} {:>6} {:>10} {:>10} {:>10} {:>12}"
    print(col.format("Model", "Calls", "In-tok", "Out-tok", "Total $", "Avg $/call"))
    print("-" * 82)

    grand_cost  = 0.0
    grand_calls = 0
    for model, data in sorted(totals.items()):
        avg = data["cost_usd"] / data["calls"] if data["calls"] else 0.0
        print(col.format(
            model[:32],
            data["calls"],
            data["input_tokens"],
            data["output_tokens"],
            f"${data['cost_usd']:.4f}",
            f"${avg:.6f}",
        ))
        grand_cost  += data["cost_usd"]
        grand_calls += data["calls"]

    print("-" * 82)
    print(col.format("TOTAL", grand_calls, "", "", f"${grand_cost:.4f}", ""))


if __name__ == "__main__":
    main()
