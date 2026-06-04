"""Tests for CrosshairDetector — no YOLO model required."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import numpy as np
import pytest
from unittest.mock import patch, MagicMock

import config
from services.cv.src.detector import CrosshairDetector


def _black_frame(h=480, w=640):
    return np.zeros((h, w, 3), dtype=np.uint8)


def _frame_with_cyan_at(x: int, y: int, h=480, w=640) -> np.ndarray:
    """Place a 5×5 cyan pixel block at (x, y) in BGR."""
    frame = _black_frame(h, w)
    frame[y-2:y+3, x-2:x+3] = [255, 255, 0]   # BGR cyan
    return frame


# ------------------------------------------------------------------ #
# CrosshairDetector
# ------------------------------------------------------------------ #

def test_fallback_to_center_on_black_frame():
    det = CrosshairDetector()
    frame = _black_frame()
    h, w = frame.shape[:2]
    cx, cy = det.detect(frame)
    assert cx == w // 2
    assert cy == h // 2


def test_detects_cyan_blob_near_center():
    """Cyan blob within the search region should be returned, not center."""
    det = CrosshairDetector()
    h, w = 480, 640
    # Place blob at exact center
    frame = _frame_with_cyan_at(w // 2, h // 2, h, w)
    cx, cy = det.detect(frame)
    assert abs(cx - w // 2) < 20
    assert abs(cy - h // 2) < 20


def test_blob_outside_search_region_falls_back_to_center():
    """Cyan blob in corner (outside CROSSHAIR_SEARCH_REGION) → fall back to center."""
    det = CrosshairDetector()
    h, w = 480, 640
    # Place blob far from center (top-left corner)
    frame = _frame_with_cyan_at(10, 10, h, w)
    cx, cy = det.detect(frame)
    # Should fall back to frame center since blob is outside search region
    assert cx == w // 2
    assert cy == h // 2


def test_returns_floats():
    det = CrosshairDetector()
    cx, cy = det.detect(_black_frame())
    assert isinstance(cx, float)
    assert isinstance(cy, float)


# ------------------------------------------------------------------ #
# Detector fallback flag (no model download)
# ------------------------------------------------------------------ #

def test_detector_uses_fallback_when_model_missing(tmp_path, monkeypatch):
    """When MODEL_PATH doesn't exist, _fallback=True is set."""
    monkeypatch.setattr(config, "MODEL_PATH", str(tmp_path / "nonexistent.pt"))
    monkeypatch.setattr(config, "FALLBACK_MODEL", "yolov8n.pt")

    with patch("services.cv.src.detector.YOLO") as MockYOLO:
        MockYOLO.return_value = MagicMock()
        from importlib import reload
        import services.cv.src.detector as det_mod
        reload(det_mod)
        d = det_mod.Detector()
        assert d._fallback is True
