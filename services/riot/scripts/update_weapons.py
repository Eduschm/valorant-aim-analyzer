"""
Refresh services/riot/data/weapons.json from the public Valorant API.

Usage:
    python services/riot/scripts/update_weapons.py

Override the source URL via MODEL_URL env var (useful for testing with a stub).
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request

SOURCE_URL = os.getenv("WEAPONS_URL", "https://valorant-api.com/v1/weapons")
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "weapons.json")


def fetch_weapons(url: str) -> dict[str, str]:
    with urllib.request.urlopen(url, timeout=15) as resp:
        data = json.loads(resp.read())
    weapons: dict[str, str] = {}
    for w in data.get("data", []):
        uuid = (w.get("uuid") or "").lower()
        name = w.get("displayName") or ""
        if uuid and name:
            weapons[uuid] = name
    return weapons


def main() -> None:
    print(f"Fetching weapons from {SOURCE_URL} …")
    try:
        weapons = fetch_weapons(SOURCE_URL)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    out = os.path.abspath(OUT_PATH)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        json.dump(weapons, f, indent=2)
    print(f"Wrote {len(weapons)} weapons → {out}")


if __name__ == "__main__":
    main()
