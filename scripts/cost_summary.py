#!/usr/bin/env python3
"""
Print a summary of LLM coaching report costs from the cost log.

Usage:
    python scripts/cost_summary.py [--log PATH]

Default log path: llm_costs.jsonl (or LLM_COST_LOG env var).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarise LLM cost log")
    parser.add_argument(
        "--log",
        default=os.getenv("LLM_COST_LOG", "llm_costs.jsonl"),
        help="Path to the JSONL cost log (default: llm_costs.jsonl)",
    )
    args = parser.parse_args()

    if not os.path.exists(args.log):
        print(f"No cost log found at {args.log!r}. No reports generated yet.")
        sys.exit(0)

    entries: list[dict] = []
    bad_lines = 0
    with open(args.log) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                bad_lines += 1

    if not entries:
        print("Log file is empty.")
        sys.exit(0)

    total_cost   = sum(e.get("cost_usd", 0.0)        for e in entries)
    total_input  = sum(e.get("input_tokens", 0)       for e in entries)
    total_output = sum(e.get("output_tokens", 0)      for e in entries)
    avg_cost     = total_cost / len(entries)

    # Per-model breakdown
    by_model: dict[str, dict] = defaultdict(lambda: {"count": 0, "cost": 0.0, "input": 0, "output": 0})
    for e in entries:
        m = e.get("model", "unknown")
        by_model[m]["count"]  += 1
        by_model[m]["cost"]   += e.get("cost_usd", 0.0)
        by_model[m]["input"]  += e.get("input_tokens", 0)
        by_model[m]["output"] += e.get("output_tokens", 0)

    # Time range
    timestamps = [e.get("ts") for e in entries if e.get("ts")]
    first = datetime.fromtimestamp(min(timestamps), tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC") if timestamps else "unknown"
    last  = datetime.fromtimestamp(max(timestamps), tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC") if timestamps else "unknown"

    print("=" * 60)
    print("LLM Cost Summary")
    print("=" * 60)
    print(f"  Log file:       {args.log}")
    print(f"  Reports logged: {len(entries)}")
    print(f"  Period:         {first}  →  {last}")
    print(f"  Total input:    {total_input:,} tokens")
    print(f"  Total output:   {total_output:,} tokens")
    print(f"  Total cost:     ${total_cost:.4f}")
    print(f"  Avg cost/report: ${avg_cost:.6f}")
    if bad_lines:
        print(f"  (skipped {bad_lines} malformed lines)")

    if len(by_model) > 1:
        print("\nPer-model breakdown:")
        for model, stats in sorted(by_model.items()):
            print(
                f"  {model}: {stats['count']} reports, "
                f"${stats['cost']:.4f} total, "
                f"${stats['cost']/stats['count']:.6f} avg"
            )

    print("=" * 60)


if __name__ == "__main__":
    main()
