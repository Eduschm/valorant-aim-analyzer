"""
Quick frame extraction utility.
Extracts frames from a VOD at regular intervals so you can label them.

Usage:
    python label_tool.py <video_path> [--interval 30] [--output data/images/train]

After extraction, label with:
    - Roboflow (roboflow.com) — recommended, exports YOLOv8 format directly
    - LabelImg  (pip install labelImg)
    - CVAT      (app.cvat.ai)

Label these 4 classes:
    0 = enemy       (full body bounding box of enemy player)
    1 = ally        (full body bounding box of ally player)
    2 = enemy_head  (tight box around enemy head/helmet)
    3 = ally_head   (tight box around ally head/helmet)
"""

import argparse
import os
import cv2
from tqdm import tqdm


def extract_frames(video_path: str, output_dir: str, interval: int):
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps   = cap.get(cv2.CAP_PROP_FPS) or 30

    base = os.path.splitext(os.path.basename(video_path))[0]
    saved = 0
    frame_idx = 0

    with tqdm(total=total // interval, desc="Extracting") as pbar:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if frame_idx % interval == 0:
                ts = frame_idx / fps
                fname = f"{base}_f{frame_idx:06d}_t{ts:.1f}s.jpg"
                cv2.imwrite(os.path.join(output_dir, fname), frame,
                            [cv2.IMWRITE_JPEG_QUALITY, 95])
                saved += 1
                pbar.update(1)
            frame_idx += 1

    cap.release()
    print(f"\n[Extractor] Saved {saved} frames to {output_dir}")
    print(f"  Tip: use Roboflow or LabelImg to annotate these frames.")
    print(f"  Classes: 0=enemy, 1=ally, 2=enemy_head, 3=ally_head")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("video",           help="Path to VOD file")
    p.add_argument("--interval",  type=int, default=30,
                   help="Extract 1 frame every N frames (default: 30)")
    p.add_argument("--output",    default="data/images/train",
                   help="Output directory for extracted frames")
    args = p.parse_args()
    extract_frames(args.video, args.output, args.interval)
