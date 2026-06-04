"""Tests for AimAnalyzer geometry helpers and engagement logic — no YOLO."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import math
import pytest
from unittest.mock import MagicMock

from services.cv.src.aim_analyzer import (
    AimAnalyzer,
    _dist, _scale, _point_in_box, _crosshair_path_velocity,
    FrameSnapshot,
)
import config


# ------------------------------------------------------------------ #
# Geometry helpers
# ------------------------------------------------------------------ #

def test_dist_known():
    assert _dist((0, 0), (3, 4)) == pytest.approx(5.0)


def test_dist_same_point():
    assert _dist((5, 5), (5, 5)) == pytest.approx(0.0)


def test_scale_reference_unchanged():
    assert _scale(100, config.REFERENCE_HEIGHT) == pytest.approx(100.0)


def test_scale_half_resolution():
    assert _scale(100, config.REFERENCE_HEIGHT // 2) == pytest.approx(50.0)


def test_point_in_box_inside():
    assert _point_in_box((50, 50), (10, 10, 100, 100)) is True


def test_point_in_box_outside():
    assert _point_in_box((200, 200), (10, 10, 100, 100)) is False


def test_point_in_box_on_edge():
    assert _point_in_box((10, 10), (10, 10, 100, 100)) is True


def test_crosshair_path_velocity_empty():
    snaps = []
    assert _crosshair_path_velocity(snaps) == []


def test_crosshair_path_velocity_known():
    s1 = MagicMock(); s1.crosshair = (0, 0)
    s2 = MagicMock(); s2.crosshair = (3, 4)
    s3 = MagicMock(); s3.crosshair = (3, 4)
    speeds = _crosshair_path_velocity([s1, s2, s3])
    assert speeds[0] == pytest.approx(5.0)
    assert speeds[1] == pytest.approx(0.0)


# ------------------------------------------------------------------ #
# Fake track helper
# ------------------------------------------------------------------ #

def fake_track(label, bbox, track_id=0):
    t = MagicMock()
    t.id     = track_id
    t.label  = label
    t.bbox   = bbox
    t.center = ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)
    t.conf   = 0.8
    return t


ENEMY_BBOX = (300, 200, 380, 400)   # enemy body box, center at (340, 300)
HEAD_BBOX  = (315, 200, 365, 240)   # head box at top of body


# ------------------------------------------------------------------ #
# Engagement windows
# ------------------------------------------------------------------ #

def test_push_opens_engagement_window():
    az = AimAnalyzer(frame_height=1080)
    enemy = fake_track("enemy", ENEMY_BBOX)
    az.push(0, (320, 300), [enemy])
    assert len(az._engagements) == 1


def test_push_closes_window_when_enemy_disappears():
    az = AimAnalyzer(frame_height=1080)
    enemy = fake_track("enemy", ENEMY_BBOX)
    # Frame 0–4: enemy visible
    for i in range(5):
        az.push(i, (320, 300), [enemy])
    # Frame 5: enemy gone
    az.push(5, (320, 300), [])
    assert len(az._engagements) == 0
    assert len(az._closed) == 1


def test_finalize_returns_closed_windows():
    az = AimAnalyzer(frame_height=1080)
    enemy = fake_track("enemy", ENEMY_BBOX)
    for i in range(6):
        az.push(i, (320, 300), [enemy])
    windows = az.finalize()
    assert len(windows) == 1


def test_min_engagement_frames_filters_flickers():
    az = AimAnalyzer(frame_height=1080)
    enemy = fake_track("enemy", ENEMY_BBOX)
    # Only 2 frames — below MIN_ENGAGEMENT_FRAMES (4)
    az.push(0, (320, 300), [enemy])
    az.push(1, (320, 300), [enemy])
    windows = az.finalize()
    assert len(windows) == 0


# ------------------------------------------------------------------ #
# Mistake detection
# ------------------------------------------------------------------ #

def test_overshoot_detected():
    az = AimAnalyzer(frame_height=1080)
    enemy = fake_track("enemy", ENEMY_BBOX, track_id=1)
    ecx, ecy = enemy.center

    # Approach: crosshair moves toward enemy over 10 frames
    for i in range(10):
        x = ecx - 200 + i * 20   # approaches from left
        az.push(i, (x, ecy), [enemy])

    # Overshoot: crosshair goes past and moves away
    for i in range(10, 20):
        x = ecx + (i - 10) * 20  # recedes to the right
        az.push(i, (x, ecy), [enemy])

    windows = az.finalize()
    assert len(windows) == 1
    mistake_types = [m.mistake_type for m in windows[0].mistakes]
    assert "overshoot" in mistake_types


def test_spray_control_detected():
    az = AimAnalyzer(frame_height=1080)
    enemy = fake_track("enemy", ENEMY_BBOX, track_id=2)
    ecx, ecy = enemy.center

    import random
    random.seed(42)
    for i in range(15):
        # Wild random crosshair movement — high std-dev
        x = ecx + random.randint(-150, 150)
        y = ecy + random.randint(-150, 150)
        az.push(i, (x, y), [enemy])

    windows = az.finalize()
    assert len(windows) == 1
    mistake_types = [m.mistake_type for m in windows[0].mistakes]
    assert "spray_control" in mistake_types


def test_moving_while_shooting_detected():
    """Crosshair stays inside enemy bbox but oscillates fast → moving_while_shooting."""
    threshold = _scale(config.MOVEMENT_BLUR_THRESHOLD, 1080)
    enemy = fake_track("enemy", ENEMY_BBOX, track_id=3)
    ecx, ecy = enemy.center

    # Oscillate quickly WITHIN the enemy bbox — high speed, always on target
    half_w = (ENEMY_BBOX[2] - ENEMY_BBOX[0]) // 2 - 5
    mistakes_all = []
    az = AimAnalyzer(frame_height=1080)
    for i in range(10):
        # Bounce left-right inside the box with speed > threshold
        x = ecx + (half_w if i % 2 == 0 else -half_w)
        events = az.push(i, (x, ecy), [enemy])
        mistakes_all.extend(events)

    types = [m.mistake_type for m in mistakes_all]
    assert "moving_while_shooting" in types


def test_body_not_head_detected():
    """Crosshair on body, just below head bbox — head is within threshold → body_not_head."""
    az = AimAnalyzer(frame_height=1080)
    enemy = fake_track("enemy", ENEMY_BBOX, track_id=4)
    head  = fake_track("enemy_head", HEAD_BBOX, track_id=5)

    # Place crosshair just below the head bbox (inside body box, close to head)
    # HEAD_BBOX bottom = 240; place crosshair at y=255 → 15px below head
    body_cx = (ENEMY_BBOX[0] + ENEMY_BBOX[2]) / 2
    body_cy = HEAD_BBOX[3] + 15   # just below head box, still inside body box

    mistakes = []
    for i in range(4):
        events = az.push(i, (body_cx, body_cy), [enemy, head])
        mistakes.extend(events)

    types = [m.mistake_type for m in mistakes]
    assert "body_not_head" in types
