"""Tests for IoU, Track, and Tracker — no YOLO required."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import pytest
from services.cv.src.tracker import _iou, Track, Tracker
import config


def _det(label="enemy", bbox=(10, 10, 60, 60)):
    cx = (bbox[0] + bbox[2]) / 2
    cy = (bbox[1] + bbox[3]) / 2
    return {"label": label, "class_id": 0, "conf": 0.8, "bbox": bbox, "center": (cx, cy)}


# ------------------------------------------------------------------ #
# IoU
# ------------------------------------------------------------------ #

def test_iou_perfect_overlap():
    box = (0, 0, 100, 100)
    assert _iou(box, box) == pytest.approx(1.0)


def test_iou_no_overlap():
    assert _iou((0, 0, 10, 10), (20, 20, 30, 30)) == pytest.approx(0.0)


def test_iou_partial_overlap():
    # box A: (0,0,10,10) area=100; box B: (5,5,15,15) area=100
    # intersection: (5,5,10,10) = 25; union = 175
    result = _iou((0, 0, 10, 10), (5, 5, 15, 15))
    assert result == pytest.approx(25 / 175, rel=1e-3)


# ------------------------------------------------------------------ #
# Track
# ------------------------------------------------------------------ #

def test_track_created_unconfirmed():
    t = Track(_det())
    assert t.hits == 1
    assert t.confirmed is False


def test_track_confirmed_after_min_hits():
    t = Track(_det())
    t.update(_det())   # hits = 2 ≥ TRACKER_MIN_HITS (2)
    assert t.confirmed is True


def test_track_miss_increments_no_match():
    t = Track(_det())
    t.miss()
    assert t.no_match == 1
    assert t.age == 2


def test_track_update_resets_no_match():
    t = Track(_det())
    t.miss()
    t.update(_det())
    assert t.no_match == 0


def test_track_history_accumulates():
    t = Track(_det(bbox=(10, 10, 60, 60)))
    t.update(_det(bbox=(20, 20, 70, 70)))
    assert len(t.history) == 2


# ------------------------------------------------------------------ #
# Tracker
# ------------------------------------------------------------------ #

def test_tracker_empty_on_init():
    tr = Tracker()
    assert tr.tracks == []


def test_tracker_creates_track_on_first_detection():
    tr = Tracker()
    tr.update([_det()])
    # First frame: 1 detection, hits=1 (unconfirmed) — confirmed requires 2 hits
    assert len(tr.tracks) == 1


def test_tracker_confirms_after_two_frames():
    tr = Tracker()
    tr.update([_det()])
    confirmed = tr.update([_det()])
    assert len(confirmed) == 1
    assert confirmed[0].confirmed is True


def test_tracker_matches_same_box_next_frame():
    tr = Tracker()
    tr.update([_det(bbox=(10, 10, 60, 60))])
    confirmed = tr.update([_det(bbox=(12, 12, 62, 62))])  # slight movement
    assert len(tr.tracks) == 1   # not a new track


def test_tracker_creates_new_track_for_new_detection():
    tr = Tracker()
    tr.update([_det(bbox=(10, 10, 60, 60))])
    tr.update([_det(bbox=(10, 10, 60, 60)), _det(bbox=(200, 200, 250, 250))])
    assert len(tr.tracks) == 2


def test_tracker_prunes_dead_tracks(monkeypatch):
    monkeypatch.setattr(config, "TRACKER_MAX_AGE", 2)
    tr = Tracker()
    tr.update([_det()])
    tr.update([_det()])
    # Now miss 3 times — track should be pruned
    tr.update([])
    tr.update([])
    tr.update([])
    assert len(tr.tracks) == 0


def test_tracker_returns_only_confirmed():
    tr = Tracker()
    # After 1 frame, track is unconfirmed — returned list should be empty
    result = tr.update([_det()])
    assert result == []
