#!/usr/bin/env python3
"""Print total LLM spend and avg cost per coaching report from the cost log.

Usage:
    python scripts/cost_summary.py [path/to/coaching_costs.jsonl]
"""

import json
import sys
from collections import defaultdict

DEFAULT_LOG = "coaching_costs.jsonl"


def main() -> None:
    log_file = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_LOG

    try:
        with open(log_file) as f:
            entries = [json.loads(line) for line in f if line.strip()]
    except FileNotFoundError:
        print(f"No cost log found at: {log_file}")
        sys.exit(0)

    if not entries:
        print("Cost log is empty.")
        return

    total_cost   = sum(e["cost_usd"]      for e in entries)
    total_input  = sum(e["input_tokens"]  for e in entries)
    total_output = sum(e["output_tokens"] for e in entries)
    avg_cost     = total_cost / len(entries)

    by_model: dict[str, dict] = defaultdict(lambda: {"count": 0, "cost": 0.0})
    for e in entries:
        m = e.get("model", "unknown")
        by_model[m]["count"] += 1
        by_model[m]["cost"]  += e["cost_usd"]

    print(f"{'─' * 46}")
    print(f"  Reports:           {len(entries):>10,}")
    print(f"  Total spend:       ${total_cost:>13.4f}")
    print(f"  Avg cost/report:   ${avg_cost:>13.4f}")
    print(f"  Total tokens in:   {total_input:>13,}")
    print(f"  Total tokens out:  {total_output:>13,}")
    print(f"{'─' * 46}")
    for model, stats in sorted(by_model.items()):
        print(f"  {model:<28} {stats['count']:>4} calls  ${stats['cost']:.4f}")
    print(f"{'─' * 46}")


if __name__ == "__main__":
    main()
