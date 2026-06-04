"""Simple IoU-based multi-object tracker."""

import numpy as np
from scipy.optimize import linear_sum_assignment

import config


def _iou(boxA: tuple, boxB: tuple) -> float:
    ax1, ay1, ax2, ay2 = boxA
    bx1, by1, bx2, by2 = boxB
    ix1 = max(ax1, bx1)
    iy1 = max(ay1, by1)
    ix2 = min(ax2, bx2)
    iy2 = min(ay2, by2)
    inter = max(0, ix2 - ix1) * max(0, iy2 - iy1)
    if inter == 0:
        return 0.0
    aA = (ax2 - ax1) * (ay2 - ay1)
    aB = (bx2 - bx1) * (by2 - by1)
    return inter / (aA + aB - inter)


class Track:
    _next_id = 0

    def __init__(self, detection: dict):
        self.id        = Track._next_id
        Track._next_id += 1
        self.label     = detection["label"]
        self.bbox      = detection["bbox"]
        self.center    = detection["center"]
        self.conf      = detection["conf"]
        self.age       = 1
        self.hits      = 1
        self.no_match  = 0
        self.history   : list[tuple[float, float]] = [detection["center"]]

    def update(self, detection: dict):
        self.bbox    = detection["bbox"]
        self.center  = detection["center"]
        self.conf    = detection["conf"]
        self.age    += 1
        self.hits   += 1
        self.no_match = 0
        self.history.append(detection["center"])

    def miss(self):
        self.no_match += 1
        self.age      += 1

    @property
    def confirmed(self) -> bool:
        return self.hits >= config.TRACKER_MIN_HITS


class Tracker:
    def __init__(self):
        self.tracks: list[Track] = []

    def update(self, detections: list[dict]) -> list[Track]:
        if not self.tracks:
            for d in detections:
                self.tracks.append(Track(d))
            return [t for t in self.tracks if t.confirmed]

        # Build cost matrix (1 - IoU)
        cost = np.ones((len(self.tracks), len(detections)))
        for ti, track in enumerate(self.tracks):
            for di, det in enumerate(detections):
                iou_val = _iou(track.bbox, det["bbox"])
                if track.label == det["label"]:
                    cost[ti, di] = 1 - iou_val

        row_ind, col_ind = linear_sum_assignment(cost)

        matched_tracks = set()
        matched_dets   = set()

        for ti, di in zip(row_ind, col_ind):
            if cost[ti, di] < (1 - config.IOU_MIN_TRACK):
                self.tracks[ti].update(detections[di])
                matched_tracks.add(ti)
                matched_dets.add(di)

        for ti, track in enumerate(self.tracks):
            if ti not in matched_tracks:
                track.miss()

        for di, det in enumerate(detections):
            if di not in matched_dets:
                self.tracks.append(Track(det))

        # Prune dead tracks
        self.tracks = [t for t in self.tracks if t.no_match <= config.TRACKER_MAX_AGE]

        return [t for t in self.tracks if t.confirmed]
