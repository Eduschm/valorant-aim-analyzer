"""
Root conftest — shared fixtures for all services.
"""

import sys
import os

# Ensure repo root is on path so all service imports work
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
import pytest

from contracts.schemas import RiotReport, CoachingReport, CVReport, MatchStat


@pytest.fixture
def mock_riot_report():
    return RiotReport(
        puuid="test-puuid-abc",
        game_name="TestPlayer",
        tag_line="NA1",
        current_rank="Gold 2",
        rank_delta=15,
        matches=[
            MatchStat("m1", "Jett",  "Vandal",  18, 12, 3, 25.0, 160.0, True),
            MatchStat("m2", "Jett",  "Vandal",  10, 15, 5, 18.0, 120.0, False),
            MatchStat("m3", "Reyna", "Phantom", 14, 13, 8, 22.0, 140.0, True),
        ],
        avg_headshot_pct=21.7,
        avg_adr=140.0,
        top_agent="Jett",
        top_weapon="Vandal",
        win_rate=0.67,
    )


@pytest.fixture
def mock_coaching():
    return CoachingReport(
        summary="TestPlayer has a 21.7% HS rate — below Gold average.",
        top_weakness="Headshot rate 21.7% vs 28% Gold average.",
        tips=["Keep crosshair at head height.", "Counter-strafe before shooting."],
        encouragement="The ceiling is there — consistency is next.",
        raw_response='{"summary":"..."}',
    )


@pytest.fixture
def sample_frame():
    """480×640 black BGR frame — safe for CV tests without model files."""
    return np.zeros((480, 640, 3), dtype=np.uint8)


@pytest.fixture
def fake_track_factory():
    """Factory for building fake Track-like objects without YOLO."""
    from unittest.mock import MagicMock

    def _make(label: str, bbox: tuple, center: tuple = None, track_id: int = 0):
        t = MagicMock()
        t.id     = track_id
        t.label  = label
        t.bbox   = bbox
        t.center = center or ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)
        t.conf   = 0.8
        t.hits   = 3
        t.history = [t.center]
        return t

    return _make
