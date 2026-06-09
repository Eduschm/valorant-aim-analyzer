"""
Download the custom Valorant YOLO model to services/cv/models/valorant.pt.

Usage:
    python services/cv/scripts/download_model.py

Override the source URL via MODEL_URL env var (useful for testing with a stub).
Set MODEL_URL to a local file:// path or an HTTP URL.
"""

from __future__ import annotations

import os
import sys
import urllib.request
import shutil

_HERE = os.path.dirname(os.path.abspath(__file__))
_MODELS_DIR = os.path.join(_HERE, "..", "models")
_MODEL_PATH = os.path.join(_MODELS_DIR, "valorant.pt")

# The canonical download URL. Replace with the actual hosted location once
# the model is uploaded to a stable source (Hugging Face Hub recommended).
# Set MODEL_URL env var to override for testing.
DEFAULT_MODEL_URL = os.getenv(
    "MODEL_URL",
    "https://huggingface.co/valorant-aim-analyzer/models/resolve/main/valorant.pt",
)


def download_model(url: str, dest: str) -> None:
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    print(f"Downloading model from {url} …")

    # Support local file:// paths for testing
    if url.startswith("file://"):
        src = url[len("file://"):]
        shutil.copy2(src, dest)
        print(f"Copied {src} → {dest}")
        return

    def _progress(count, block_size, total):
        if total > 0:
            pct = min(count * block_size * 100 // total, 100)
            print(f"\r  {pct}%", end="", flush=True)

    try:
        urllib.request.urlretrieve(url, dest, reporthook=_progress)
        print(f"\nSaved → {dest}")
    except Exception as exc:
        # Clean up partial download
        if os.path.exists(dest):
            os.remove(dest)
        raise RuntimeError(f"Download failed: {exc}") from exc


def main() -> None:
    dest = os.path.abspath(_MODEL_PATH)

    if os.path.exists(dest):
        size_mb = os.path.getsize(dest) / 1_000_000
        print(f"Model already present at {dest} ({size_mb:.1f} MB). Delete it to re-download.")
        sys.exit(0)

    url = DEFAULT_MODEL_URL
    try:
        download_model(url, dest)
    except RuntimeError as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        print(
            "\nTo get the model:\n"
            "  1. Contact the project maintainer for the hosted URL.\n"
            "  2. Set MODEL_URL env var and re-run this script.\n"
            "  3. Or set MATCH_PROVIDER=henrik to skip CV and use Riot stats only.",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
