"""
Core aiming-mistake analysis.

For every frame where at least one enemy is visible, we compare the
crosshair position to each enemy's bounding-box to decide:
  - whether the player was on target
  - what kind of mistake was made if they were not / missed

Results are collected per *engagement window* — a continuous run of frames
in which a specific enemy track is visible.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from collections import defaultdict

import numpy as np

import config
from src.tracker import Track


# --------------------------------------------------------------------------- #
#  Data structures                                                             #
# --------------------------------------------------------------------------- #

@dataclass
class FrameSnapshot:
    frame_idx:      int
    crosshair:      tuple[float, float]
    enemy_tracks:   list[Track]
    head_tracks:    list[Track]


@dataclass
class MistakeEvent:
    mistake_type:  str
    frame_idx:     int
    track_id:      int | None
    severity:      float          # 0-1 normalised
    description:   str


@dataclass
class EngagementWindow:
    track_id:   int
    start:      int
    end:        int
    snapshots:  list[FrameSnapshot] = field(default_factory=list)
    mistakes:   list[MistakeEvent]  = field(default_factory=list)
    on_target_frames:  int = 0
    total_frames:      int = 0


# --------------------------------------------------------------------------- #
#  Helpers                                                                     #
# --------------------------------------------------------------------------- #

def _dist(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _scale(px: float, frame_h: int) -> float:
    """Scale a pixel threshold from reference resolution to actual resolution."""
    return px * (frame_h / config.REFERENCE_HEIGHT)


def _point_in_box(pt: tuple[float, float], box: tuple) -> bool:
    x1, y1, x2, y2 = box
    return x1 <= pt[0] <= x2 and y1 <= pt[1] <= y2


def _crosshair_path_velocity(snapshots: list[FrameSnapshot]) -> list[float]:
    """Per-frame crosshair speed (pixels/frame)."""
    speeds = []
    for i in range(1, len(snapshots)):
        speeds.append(_dist(snapshots[i].crosshair, snapshots[i - 1].crosshair))
    return speeds


# --------------------------------------------------------------------------- #
#  Main analyser                                                               #
# --------------------------------------------------------------------------- #

class AimAnalyzer:
    def __init__(self, frame_height: int = 1080):
        self.frame_h = frame_height
        self._snapshots:  list[FrameSnapshot]    = []
        self._engagements: dict[int, EngagementWindow] = {}   # track_id → window
        self._closed:      list[EngagementWindow] = []

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def push(self, frame_idx: int, crosshair: tuple[float, float],
             tracks: list[Track]) -> list[MistakeEvent]:
        """Feed one frame; returns any mistakes detected in this frame."""
        # Exclude _death detections — they're corpses, not active threats
        enemy_tracks = [t for t in tracks if t.label == "enemy"]
        head_tracks  = [t for t in tracks if t.label == "enemy_head"]

        snap = FrameSnapshot(frame_idx, crosshair, enemy_tracks, head_tracks)
        self._snapshots.append(snap)

        self._update_engagement_windows(snap)
        return self._analyze_frame(snap)

    def finalize(self) -> list[EngagementWindow]:
        """Close all open windows and run per-engagement analysis. Call at end of video."""
        for ew in list(self._engagements.values()):
            self._close_window(ew)
        return self._closed

    # ------------------------------------------------------------------ #
    #  Engagement window tracking                                          #
    # ------------------------------------------------------------------ #

    def _update_engagement_windows(self, snap: FrameSnapshot):
        visible_ids = {t.id for t in snap.enemy_tracks}  # only live enemies

        # Close windows whose enemy disappeared
        for tid in list(self._engagements.keys()):
            if tid not in visible_ids:
                self._close_window(self._engagements.pop(tid))

        # Open or extend windows
        for track in snap.enemy_tracks:
            if track.id not in self._engagements:
                self._engagements[track.id] = EngagementWindow(
                    track_id=track.id,
                    start=snap.frame_idx,
                    end=snap.frame_idx,
                )
            ew = self._engagements[track.id]
            ew.end = snap.frame_idx
            ew.total_frames += 1
            ew.snapshots.append(snap)
            if _point_in_box(snap.crosshair, track.bbox):
                ew.on_target_frames += 1

    def _close_window(self, ew: EngagementWindow):
        if ew.total_frames < config.MIN_ENGAGEMENT_FRAMES:
            return
        ew.mistakes.extend(self._analyze_engagement(ew))
        self._closed.append(ew)

    # ------------------------------------------------------------------ #
    #  Per-frame mistakes (real-time feedback)                            #
    # ------------------------------------------------------------------ #

    def _analyze_frame(self, snap: FrameSnapshot) -> list[MistakeEvent]:
        mistakes = []
        if not snap.enemy_tracks:
            return mistakes

        s = _scale(1, self.frame_h)    # scaling factor

        for enemy in snap.enemy_tracks:
            cx, cy = snap.crosshair
            ex1, ey1, ex2, ey2 = enemy.bbox
            ecx, ecy = enemy.center

            # Movement-while-shooting: check last 3 frames for crosshair speed
            recent = self._snapshots[-3:]
            if len(recent) >= 2:
                speeds = _crosshair_path_velocity(recent)
                avg_speed = sum(speeds) / len(speeds)
                threshold = _scale(config.MOVEMENT_BLUR_THRESHOLD, self.frame_h)
                if avg_speed > threshold and _point_in_box(snap.crosshair, enemy.bbox):
                    sev = min(1.0, avg_speed / (threshold * 3))
                    mistakes.append(MistakeEvent(
                        mistake_type="moving_while_shooting",
                        frame_idx=snap.frame_idx,
                        track_id=enemy.id,
                        severity=sev,
                        description=f"Fired while moving at {avg_speed:.1f}px/frame speed",
                    ))

            # Body-not-head: crosshair on body but a head bbox is available nearby
            for head in snap.head_tracks:
                head_dist = _dist(snap.crosshair, head.center)
                body_dist = _dist(snap.crosshair, enemy.center)
                threshold_head = _scale(config.HEAD_PROXIMITY_PX, self.frame_h)
                threshold_body = _scale(config.BODY_NOT_HEAD_THRESHOLD_PX, self.frame_h)
                if (
                    _point_in_box(snap.crosshair, enemy.bbox)
                    and not _point_in_box(snap.crosshair, head.bbox)
                    and head_dist < _scale(config.BODY_NOT_HEAD_THRESHOLD_PX * 2, self.frame_h)
                ):
                    sev = 1 - (head_dist / (threshold_body * 2 + 1e-9))
                    sev = max(0.1, min(1.0, sev))
                    mistakes.append(MistakeEvent(
                        mistake_type="body_not_head",
                        frame_idx=snap.frame_idx,
                        track_id=enemy.id,
                        severity=sev,
                        description=f"Head was {head_dist:.0f}px away but crosshair on body",
                    ))

        return mistakes

    # ------------------------------------------------------------------ #
    #  Per-engagement mistakes (post-hoc analysis)                        #
    # ------------------------------------------------------------------ #

    def _analyze_engagement(self, ew: EngagementWindow) -> list[MistakeEvent]:
        mistakes = []
        crosshairs = [s.crosshair for s in ew.snapshots]
        if len(crosshairs) < 2:
            return mistakes

        # Find the matching enemy track across snapshots
        enemy_centers = []
        for s in ew.snapshots:
            match = next((t for t in s.enemy_tracks if t.id == ew.track_id), None)
            enemy_centers.append(match.center if match else None)

        valid_pairs = [
            (ch, ec)
            for ch, ec in zip(crosshairs, enemy_centers)
            if ec is not None
        ]
        if not valid_pairs:
            return mistakes

        crosshairs_v, enemy_centers_v = zip(*valid_pairs)

        # ---- Overshoot / Undershoot analysis -------------------------
        # Compute signed distance along the aim direction across frames
        dists = [_dist(ch, ec) for ch, ec in valid_pairs]
        min_dist = min(dists)
        min_idx  = dists.index(min_dist)

        # Overshoot: crosshair approaches then recedes past the target
        if min_idx > 0 and min_idx < len(dists) - 1:
            before = dists[:min_idx]
            after  = dists[min_idx + 1:]
            if before and after:
                approach_delta = before[0] - min_dist
                recoil_delta   = dists[-1] - min_dist
                overshoot_thresh = _scale(config.OVERSHOOT_THRESHOLD_PX, self.frame_h)
                undershoot_thresh = _scale(config.UNDERSHOOT_THRESHOLD_PX, self.frame_h)

                if recoil_delta > overshoot_thresh and approach_delta > overshoot_thresh:
                    sev = min(1.0, recoil_delta / (overshoot_thresh * 4))
                    mistakes.append(MistakeEvent(
                        mistake_type="overshoot",
                        frame_idx=ew.snapshots[min_idx].frame_idx,
                        track_id=ew.track_id,
                        severity=sev,
                        description=f"Crosshair passed target by ~{recoil_delta:.0f}px",
                    ))
                elif min_dist > undershoot_thresh and approach_delta < undershoot_thresh / 2:
                    sev = min(1.0, min_dist / (undershoot_thresh * 4))
                    mistakes.append(MistakeEvent(
                        mistake_type="undershoot",
                        frame_idx=ew.snapshots[min_idx].frame_idx,
                        track_id=ew.track_id,
                        severity=sev,
                        description=f"Never closed within {min_dist:.0f}px of target",
                    ))

        # ---- Spray control ------------------------------------------
        if len(crosshairs_v) >= 6:
            xs = [c[0] for c in crosshairs_v]
            ys = [c[1] for c in crosshairs_v]
            std_dev = math.sqrt(np.std(xs) ** 2 + np.std(ys) ** 2)
            threshold = _scale(config.SPRAY_DEVIATION_THRESHOLD, self.frame_h)
            if std_dev > threshold:
                sev = min(1.0, std_dev / (threshold * 3))
                mistakes.append(MistakeEvent(
                    mistake_type="spray_control",
                    frame_idx=ew.start,
                    track_id=ew.track_id,
                    severity=sev,
                    description=f"High crosshair spread during engagement (σ={std_dev:.0f}px)",
                ))

        # ---- Wrong target priority ----------------------------------
        # If multiple enemies visible and the player aimed at one with a
        # farther head when a closer-to-crosshair enemy existed
        for s in ew.snapshots:
            if len(s.enemy_tracks) >= 2:
                sorted_by_dist = sorted(
                    s.enemy_tracks,
                    key=lambda t: _dist(s.crosshair, t.center),
                )
                aimed_at   = sorted_by_dist[0]
                other      = sorted_by_dist[1]
                aimed_dist = _dist(s.crosshair, aimed_at.center)
                other_dist = _dist(s.crosshair, other.center)
                # Heuristic: other enemy is significantly closer and we're not even near aimed
                if other_dist < aimed_dist * 0.6 and aimed_dist > _scale(80, self.frame_h):
                    sev = 1 - (other_dist / (aimed_dist + 1e-9))
                    sev = max(0.1, min(0.9, sev))
                    mistakes.append(MistakeEvent(
                        mistake_type="wrong_target",
                        frame_idx=s.frame_idx,
                        track_id=aimed_at.id,
                        severity=sev,
                        description=(
                            f"Aimed at enemy {aimed_dist:.0f}px away "
                            f"while closer enemy was {other_dist:.0f}px away"
                        ),
                    ))
                    break  # one per engagement is enough

        return mistakes
