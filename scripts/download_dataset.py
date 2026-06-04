"""
Download the Valorant dataset from Roboflow using the REST API directly.
Dataset: https://universe.roboflow.com/valo-qs4up/valorant-0h6ni

Usage:
    python download_dataset.py --key YOUR_API_KEY
    python download_dataset.py --key YOUR_API_KEY --version 2   (if version 1 fails)

Get your API key: https://app.roboflow.com → top-right avatar → API Keys
"""

import argparse
import io
import os
import zipfile
import requests

WORKSPACE = "valo-qs4up"
PROJECT   = "valorant-0h6ni"
FORMAT    = "yolov8"
OUT_DIR   = "data"


def download(api_key: str, version: int):
    # Step 1: ask Roboflow for the export link
    meta_url = (
        f"https://api.roboflow.com/{WORKSPACE}/{PROJECT}/{version}/{FORMAT}"
        f"?api_key={api_key}"
    )
    print(f"[Download] Requesting export link...")
    r = requests.get(meta_url, timeout=30)

    if r.status_code != 200:
        print(f"[ERROR] API returned {r.status_code}: {r.text}")
        print("  → Check your API key and version number.")
        return

    data = r.json()
    export = data.get("export", {})
    link   = export.get("link")

    if not link:
        print(f"[ERROR] No download link in response: {data}")
        return

    # Step 2: download the zip
    print(f"[Download] Downloading dataset zip...")
    r2 = requests.get(link, timeout=120, stream=True)
    r2.raise_for_status()

    total = int(r2.headers.get("content-length", 0))
    downloaded = 0
    chunks = []
    for chunk in r2.iter_content(chunk_size=8192):
        chunks.append(chunk)
        downloaded += len(chunk)
        if total:
            pct = downloaded / total * 100
            print(f"\r  {pct:.1f}%  ({downloaded // 1024}KB / {total // 1024}KB)", end="", flush=True)
    print()

    # Step 3: extract into data/
    print(f"[Download] Extracting to {OUT_DIR}/...")
    os.makedirs(OUT_DIR, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(b"".join(chunks))) as z:
        z.extractall(OUT_DIR)

    # Step 4: find data.yaml and report class names
    yaml_path = None
    for root, dirs, files in os.walk(OUT_DIR):
        for fname in files:
            if fname == "data.yaml":
                yaml_path = os.path.join(root, fname)
                break

    if not yaml_path:
        print("[WARNING] data.yaml not found after extraction. Check the data/ folder manually.")
        return

    print(f"\n[Download] Done. data.yaml at: {yaml_path}")

    import yaml
    with open(yaml_path) as f:
        meta = yaml.safe_load(f)

    names = meta.get("names", [])
    print(f"\n  Class names ({len(names)} total):")
    for i, name in enumerate(names):
        print(f"    {i}: {name}")

    print(f"\n  Open train.py and set:")
    print(f'    DATA_YAML = r"{yaml_path}"')
    print()
    print("  Then check that config.py CLASS_IDS matches the class names above.")
    print("  If the dataset only has 1-2 classes (e.g. just 'player'), update CLASS_IDS accordingly.")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--key",     required=True, help="Roboflow API key")
    p.add_argument("--version", type=int, default=1, help="Dataset version (default: 1)")
    args = p.parse_args()
    download(args.key, args.version)
