"""
Train a custom YOLOv8 model on Valorant footage.

Dataset format: YOLOv8 (images + .txt labels, data.yaml)
Classes: 0=enemy, 1=ally, 2=enemy_head, 3=ally_head

Quick start:
    1. Collect ~500+ labeled frames from your VODs
    2. Export in YOLOv8 format (Roboflow does this automatically)
    3. Put images in data/images/{train,val}/
       and labels  in data/labels/{train,val}/
    4. Run: python train.py

Roboflow dataset option:
    If you have a Roboflow API key, set ROBOFLOW_KEY and ROBOFLOW_WORKSPACE
    in a .env file and uncomment the download block below.
"""

import os
from ultralytics import YOLO
import yaml


import pathlib
ROOT = pathlib.Path(__file__).parent.parent  # repo root

EPOCHS      = 40
BATCH_SIZE  = 32
IMAGE_SIZE  = 640
BASE_MODEL  = "yolov8m.pt"
OUTPUT_DIR  = str(ROOT / "services" / "cv" / "models")
DATA_YAML   = str(ROOT / "data" / "data.yaml")

# Fine-tune mode: freeze backbone, only train the detection head.
# Use this when you have <200 labeled frames. Much faster, less data needed.
FINETUNE_MODE  = False
FREEZE_LAYERS  = 10    # freeze first N layers (backbone); 10 is good for yolov8m


def train():
    if not os.path.exists(DATA_YAML):
        print(f"[Train] ERROR: data.yaml not found at {DATA_YAML}")
        return

    # Verify dataset exists
    train_img_dir = r"data\train\images"
    if not os.path.exists(train_img_dir) or not os.listdir(train_img_dir):
        print(f"[Train] ERROR: No training images found at {train_img_dir}")
        return

    model = YOLO(BASE_MODEL)

    freeze = FREEZE_LAYERS if FINETUNE_MODE else 0
    if FINETUNE_MODE:
        print(f"[Train] Fine-tune mode — freezing first {freeze} layers, {EPOCHS} epochs")
    else:
        print(f"[Train] Full training — {EPOCHS} epochs, batch={BATCH_SIZE}, imgsz={IMAGE_SIZE}")

    results = model.train(
        data=DATA_YAML,
        epochs=EPOCHS,
        batch=BATCH_SIZE,
        imgsz=IMAGE_SIZE,
        project=OUTPUT_DIR,
        name="valorant_v1",
        freeze=freeze,
        patience=20,
        save=True,
        plots=True,
        augment=True,
        mixup=0.1,
        copy_paste=0.1,
        device="cpu",
    )

    best_weights = os.path.join(OUTPUT_DIR, "valorant_v1", "weights", "best.pt")
    dest = str(ROOT / "services" / "cv" / "models" / "valorant.pt")
    if os.path.exists(best_weights):
        import shutil
        shutil.copy(best_weights, dest)
        print(f"[Train] Best weights saved → {dest}")
    else:
        print(f"[Train] Training complete. Copy best weights to {dest} manually.")

    return results


if __name__ == "__main__":
    train()
