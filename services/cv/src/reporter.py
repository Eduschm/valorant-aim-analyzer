"""
Generates:
  - an annotated output video with mistake overlays
  - a JSON report and/or CSV breakdown
"""

from __future__ import annotations

import json
import os
import csv
from collections import Counter, defaultdict
from dataclasses import asdict

import cv2
import numpy as np

import config
from src.aim_analyzer import MistakeEvent, EngagementWindow


MISTAKE_LABELS = {
    "overshoot":             "Overshoot",
    "undershoot":            "Undershoot",
    "body_not_head":         "Body (not head)",
    "wrong_target":          "Wrong target",
    "moving_while_shooting": "Moving while shooting",
    "spray_control":         "Spray control",
}

PERFORMANCE_WEIGHT = {
    "body_not_head":         1.0,
    "overshoot":             0.9,
    "wrong_target":          0.85,
    "spray_control":         0.75,
    "undershoot":            0.7,
    "moving_while_shooting": 0.6,
}


# --------------------------------------------------------------------------- #
#  Video annotator                                                             #
# --------------------------------------------------------------------------- #

class VideoAnnotator:
    def __init__(self, source_path: str, output_path: str, fps: float, size: tuple[int, int]):
        fourcc = cv2.VideoWriter_fourcc(*config.OUTPUT_VIDEO_CODEC)
        out_fps = fps if config.ANNOTATE_FPS_LIMIT == 0 else config.ANNOTATE_FPS_LIMIT
        self.writer = cv2.VideoWriter(output_path, fourcc, out_fps, size)
        self._active_mistakes: list[tuple[int, MistakeEvent]] = []  # (expire_frame, event)
        self._frame_events: dict[int, list[MistakeEvent]] = defaultdict(list)

    def register_events(self, events: list[MistakeEvent]):
        for e in events:
            self._frame_events[e.frame_idx].append(e)

    # Colour per label
    _BOX_COLORS = {
        "enemy":        (0,   60,  255),   # red
        "enemy_head":   (0,   0,   255),   # bright red
        "enemy_death":  (80,  80,  160),   # muted purple
        "friend":       (0,   200, 60),    # green
        "friend_head":  (0,   255, 80),    # bright green
        "friend_death": (60,  120, 60),    # muted green
    }

    def annotate_frame(
        self,
        frame: np.ndarray,
        frame_idx: int,
        crosshair: tuple[float, float] | None,
        real_time_mistakes: list[MistakeEvent],
        tracks: list | None = None,
    ) -> np.ndarray:
        out = frame.copy()

        # --- Draw bounding boxes for all tracked objects ---
        if tracks:
            for t in tracks:
                x1, y1, x2, y2 = [int(v) for v in t.bbox]
                color = self._BOX_COLORS.get(t.label, (200, 200, 200))
                cv2.rectangle(out, (x1, y1), (x2, y2), color, 2)

                # Label chip above the box
                chip = f"{t.label} #{t.id} {t.conf:.2f}"
                (tw, th), _ = cv2.getTextSize(chip, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
                chip_y = max(y1 - 4, th + 4)
                cv2.rectangle(out, (x1, chip_y - th - 4), (x1 + tw + 4, chip_y + 2), color, -1)
                cv2.putText(out, chip, (x1 + 2, chip_y - 2),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

        # --- Draw screen-centre crosshair ---
        h, w = out.shape[:2]
        cx, cy = w // 2, h // 2
        cv2.drawMarker(out, (cx, cy), (0, 255, 0), cv2.MARKER_CROSS, 24, 2)

        # --- Activate new mistake events ---
        for e in real_time_mistakes:
            self._active_mistakes.append((frame_idx + 45, e))

        # --- Draw active mistake overlays ---
        self._active_mistakes = [(exp, e) for exp, e in self._active_mistakes if exp > frame_idx]

        y_offset = 40
        for _, event in self._active_mistakes:
            color = config.MISTAKE_COLORS.get(event.mistake_type, (255, 255, 255))
            label = MISTAKE_LABELS.get(event.mistake_type, event.mistake_type)
            text  = f"[{label}] {event.description}"
            (tw, _), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.52, 1)
            cv2.rectangle(out, (10, y_offset - 18), (14 + tw, y_offset + 6), (0, 0, 0), -1)
            cv2.putText(out, text, (12, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.52, color, 1, cv2.LINE_AA)
            y_offset += 28

        # --- Frame counter (top-right) ---
        fc = f"frame {frame_idx}"
        (fw, _), _ = cv2.getTextSize(fc, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
        cv2.putText(out, fc, (w - fw - 8, 18),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1, cv2.LINE_AA)

        self.writer.write(out)
        return out

    def release(self):
        self.writer.release()


# --------------------------------------------------------------------------- #
#  Stats reporter                                                              #
# --------------------------------------------------------------------------- #

class Reporter:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate(
        self,
        engagements: list[EngagementWindow],
        realtime_events: list[MistakeEvent],
        total_frames: int,
        fps: float,
        video_name: str,
    ) -> dict:
        all_mistakes: list[MistakeEvent] = list(realtime_events)
        for ew in engagements:
            all_mistakes.extend(ew.mistakes)

        counts     = Counter(e.mistake_type for e in all_mistakes)
        severities = defaultdict(list)
        for e in all_mistakes:
            severities[e.mistake_type].append(e.severity)

        avg_sev = {k: sum(v) / len(v) for k, v in severities.items()}

        # Performance impact = frequency × avg_severity × weight
        impact_scores = {
            k: counts[k] * avg_sev[k] * PERFORMANCE_WEIGHT.get(k, 0.5)
            for k in counts
        }
        ranked = sorted(impact_scores.items(), key=lambda x: x[1], reverse=True)

        duration_s = total_frames / fps if fps else 0

        summary = {
            "video":              video_name,
            "duration_seconds":   round(duration_s, 2),
            "total_engagements":  len(engagements),
            "total_mistakes":     len(all_mistakes),
            "mistakes_per_minute": round(len(all_mistakes) / max(duration_s / 60, 1e-9), 2),
            "mistake_counts":     dict(counts),
            "average_severity":   {k: round(v, 3) for k, v in avg_sev.items()},
            "performance_impact_scores": {k: round(v, 3) for k, v in impact_scores.items()},
            "most_impactful_mistake":    ranked[0][0] if ranked else None,
            "ranked_by_impact": [
                {
                    "rank":           i + 1,
                    "mistake":        k,
                    "label":          MISTAKE_LABELS.get(k, k),
                    "count":          counts[k],
                    "avg_severity":   round(avg_sev[k], 3),
                    "impact_score":   round(v, 3),
                    "share_of_total": f"{100 * v / max(sum(impact_scores.values()), 1e-9):.1f}%",
                }
                for i, (k, v) in enumerate(ranked)
            ],
            "all_events": [
                {
                    "frame":        e.frame_idx,
                    "time_s":       round(e.frame_idx / fps, 2) if fps else 0,
                    "type":         e.mistake_type,
                    "label":        MISTAKE_LABELS.get(e.mistake_type, e.mistake_type),
                    "severity":     round(e.severity, 3),
                    "description":  e.description,
                    "track_id":     e.track_id,
                }
                for e in sorted(all_mistakes, key=lambda e: e.frame_idx)
            ],
        }

        base = os.path.join(self.output_dir, os.path.splitext(video_name)[0])
        fmt  = config.REPORT_FORMAT

        if fmt in ("json", "both"):
            json_path = base + "_report.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2)
            print(f"[Reporter] JSON report → {json_path}")

        if fmt in ("csv", "both"):
            csv_path = base + "_events.csv"
            if summary["all_events"]:
                keys = summary["all_events"][0].keys()
                with open(csv_path, "w", newline="", encoding="utf-8") as f:
                    w = csv.DictWriter(f, fieldnames=keys)
                    w.writeheader()
                    w.writerows(summary["all_events"])
            print(f"[Reporter] CSV events  → {csv_path}")

        return summary

    def print_summary(self, summary: dict, detection_stats: dict | None = None):
        W = 64
        div = "=" * W

        print("\n" + div)
        print(f"  VALORANT AIM ANALYSIS — {summary['video']}")
        print(div)
        print(f"  Duration          : {summary['duration_seconds']:.1f}s")
        total_frames = detection_stats["total_frames"] if detection_stats else "?"
        print(f"  Frames processed  : {total_frames}")
        print()

        # --- Detection breakdown ---
        if detection_stats:
            counts   = detection_stats["counts"]
            conf     = detection_stats["avg_confidence"]
            tracks   = detection_stats["unique_tracks"]
            tf       = detection_stats["total_frames"] or 1

            print("  DETECTIONS")
            print("  " + "-" * (W - 2))

            label_map = {
                "enemy":        "Enemies (alive)",
                "enemy_head":   "Enemy heads",
                "enemy_death":  "Enemy deaths",
                "friend":       "Allies (alive)",
                "friend_head":  "Ally heads",
                "friend_death": "Ally deaths",
            }
            for key, display in label_map.items():
                n = counts.get(key, 0)
                if n == 0:
                    continue
                avg_c  = conf.get(key, 0)
                n_trk  = tracks.get(key, 0)
                print(f"  {display:<22} {n:>6} detections   avg conf {avg_c:.2f}   {n_trk} unique tracks")

            print()
            enemy_pct  = 100 * detection_stats["frames_with_enemy"]  / tf
            friend_pct = 100 * detection_stats["frames_with_friend"] / tf
            print(f"  Frames with enemy visible : {detection_stats['frames_with_enemy']:>5}  ({enemy_pct:.1f}%)")
            print(f"  Frames with ally  visible : {detection_stats['frames_with_friend']:>5}  ({friend_pct:.1f}%)")
            print(f"  Max enemies on screen     : {detection_stats['max_enemies_frame']}")
            print(f"  Max allies  on screen     : {detection_stats['max_friends_frame']}")
            print()

        # --- Engagement & mistake summary ---
        print("  ENGAGEMENTS & MISTAKES")
        print("  " + "-" * (W - 2))
        print(f"  Engagements detected  : {summary['total_engagements']}")
        print(f"  Total mistakes        : {summary['total_mistakes']}")
        print(f"  Mistakes / minute     : {summary['mistakes_per_minute']}")
        print()

        if summary["ranked_by_impact"]:
            print("  RANKED BY PERFORMANCE IMPACT")
            print("  " + "-" * (W - 2))
            for r in summary["ranked_by_impact"]:
                bar_len = int(float(r["share_of_total"].rstrip("%")) / 4)
                bar = "█" * bar_len
                print(
                    f"  {r['rank']}. {r['label']:<26} "
                    f"x{r['count']:>3}  sev={r['avg_severity']:.2f}  "
                    f"impact={r['impact_score']:.2f}  {bar} {r['share_of_total']}"
                )
            print()
            label = MISTAKE_LABELS.get(summary["most_impactful_mistake"], summary["most_impactful_mistake"])
            print(f"  ► Most impactful mistake: {label}")
        else:
            print("  No mistakes detected.")

        print(div + "\n")
