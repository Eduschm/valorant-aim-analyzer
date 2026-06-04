"""YOLO-based enemy and crosshair detection."""

import os
import sys
import cv2
import numpy as np
from ultralytics import YOLO

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
import config
from services.logging import configure_logging, get_logger

configure_logging()
logger = get_logger("services.cv.detector")


class Detector:
    def __init__(self):
        if os.path.exists(config.MODEL_PATH):
            self.model = YOLO(config.MODEL_PATH)
            self._fallback = False
            logger.info("Loaded custom weights: %s", config.MODEL_PATH)
        else:
            self.model = YOLO(config.FALLBACK_MODEL)
            self._fallback = True
            logger.warning(
                "Custom weights not found at '%s'. Falling back to %s — COCO 'person' class mapped to 'enemy'.",
                config.MODEL_PATH,
                config.FALLBACK_MODEL,
            )

        self.conf = config.CONFIDENCE_THRESHOLD
        self.iou  = config.IOU_THRESHOLD
        self.device = config.DEVICE or None

    def detect(self, frame: np.ndarray) -> list[dict]:
        """Run YOLO on a frame, return list of detection dicts."""
        results = self.model(
            frame,
            conf=self.conf,
            iou=self.iou,
            device=self.device,
            verbose=False,
        )[0]

        # COCO class IDs for person (0) and relevant objects when using fallback model
        _FALLBACK_PERSON_IDS = {0}   # COCO: 0 = person

        detections = []
        for box in results.boxes:
            cls_id = int(box.cls[0])
            conf   = float(box.conf[0])
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2

            label = self.model.names[cls_id]

            # Fallback COCO model: map "person" → "enemy" so the pipeline works
            # without custom weights. All persons treated as enemies.
            if self._fallback:
                if cls_id not in _FALLBACK_PERSON_IDS:
                    continue
                label = "enemy"
                cls_id = 0

            detections.append({
                "class_id": cls_id,
                "label":    label,
                "conf":     conf,
                "bbox":     (x1, y1, x2, y2),
                "center":   (cx, cy),
            })

        return detections


class CrosshairDetector:
    """
    Finds the crosshair via HSV color masking in the center of the frame.
    Works best with the default Valorant crosshair (cyan/white).
    For custom crosshair colors, update CROSSHAIR_HSV_* in config.py.
    """

    def __init__(self):
        self.lower = np.array(config.CROSSHAIR_HSV_LOWER)
        self.upper = np.array(config.CROSSHAIR_HSV_UPPER)
        self.region = config.CROSSHAIR_SEARCH_REGION

    def detect(self, frame: np.ndarray) -> tuple[float, float] | None:
        h, w = frame.shape[:2]
        margin_x = int(w * self.region)
        margin_y = int(h * self.region)
        cx_frame = w // 2
        cy_frame = h // 2

        x1 = cx_frame - margin_x
        y1 = cy_frame - margin_y
        x2 = cx_frame + margin_x
        y2 = cy_frame + margin_y

        roi = frame[y1:y2, x1:x2]
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower, self.upper)

        # Morphological cleanup
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN,  kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            # Fall back to frame center — crosshair is always roughly centered
            return (float(cx_frame), float(cy_frame))

        # Pick largest blob near frame center
        best = max(contours, key=cv2.contourArea)
        M = cv2.moments(best)
        if M["m00"] == 0:
            return (float(cx_frame), float(cy_frame))

        bx = int(M["m10"] / M["m00"]) + x1
        by = int(M["m01"] / M["m00"]) + y1
        return (float(bx), float(by))
