"""
Valorant Aim Analyzer
---------------------
Usage:
    python main.py <video_path> [--no-video] [--device cpu]

Arguments:
    video_path      Path to your Valorant gameplay recording
    --no-video      Skip writing annotated output video (faster)
    --device        Force inference device: 'cpu', '0' (GPU 0), etc.
"""

import argparse
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import cv2
from tqdm import tqdm
from services.logging import configure_logging, get_logger

configure_logging()
logger = get_logger("services.cv.main")

import config
from src.detector       import Detector, CrosshairDetector
from src.tracker        import Tracker
from src.aim_analyzer   import AimAnalyzer
from src.reporter       import VideoAnnotator, Reporter


def parse_args():
    p = argparse.ArgumentParser(description="Valorant Aim Analyzer")
    p.add_argument("video",       help="Path to gameplay video")
    p.add_argument("--no-video",  action="store_true", help="Skip annotated video output")
    p.add_argument("--device",    default="",          help="Inference device ('' = auto)")
    return p.parse_args()


def main():
    args = parse_args()

    if not os.path.exists(args.video):
        logger.error("Video not found: %s", args.video)
        sys.exit(1)

    if args.device:
        config.DEVICE = args.device

    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        logger.error("Cannot open video: %s", args.video)
        sys.exit(1)

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps          = cap.get(cv2.CAP_PROP_FPS) or 30.0
    width        = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height       = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    video_name   = os.path.basename(args.video)

    logger.info("Video %s %dx%d @ %.1f fps (%d frames)", video_name, width, height, fps, total_frames)

    # Initialise pipeline
    detector          = Detector()
    crosshair_detector = CrosshairDetector()
    tracker           = Tracker()
    analyzer          = AimAnalyzer(frame_height=height)
    reporter          = Reporter(output_dir="output")

    annotator = None
    if config.ANNOTATE_VIDEO and not args.no_video:
        out_path  = os.path.join("output", os.path.splitext(video_name)[0] + "_analyzed.mp4")
        annotator = VideoAnnotator(args.video, out_path, fps, (width, height))
        print(f"[Main] Annotated video → {out_path}")

    realtime_events = []

    # Detection counters for the full report
    from collections import defaultdict, Counter
    detection_counts   = Counter()          # label → total detections across all frames
    detection_conf     = defaultdict(list)  # label → list of confidence scores
    frames_with_enemy  = 0
    frames_with_friend = 0
    max_enemies_frame  = 0
    max_friends_frame  = 0
    unique_track_ids   = defaultdict(set)   # label → set of track IDs seen

    with tqdm(total=total_frames, unit="frame", desc="Analyzing") as pbar:
        frame_idx = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            # Detect & track
            detections = detector.detect(frame)
            tracks     = tracker.update(detections)
            crosshair  = crosshair_detector.detect(frame)

            # Accumulate detection stats
            frame_enemies  = 0
            frame_friends  = 0
            for d in detections:
                detection_counts[d["label"]] += 1
                detection_conf[d["label"]].append(d["conf"])
            for t in tracks:
                unique_track_ids[t.label].add(t.id)
                if t.label == "enemy":
                    frame_enemies += 1
                elif t.label == "friend":
                    frame_friends += 1
            if frame_enemies > 0:
                frames_with_enemy += 1
            if frame_friends > 0:
                frames_with_friend += 1
            max_enemies_frame = max(max_enemies_frame, frame_enemies)
            max_friends_frame = max(max_friends_frame, frame_friends)

            # Analyze
            frame_mistakes = analyzer.push(frame_idx, crosshair, tracks)
            realtime_events.extend(frame_mistakes)

            # Annotate
            if annotator:
                annotator.annotate_frame(frame, frame_idx, crosshair, frame_mistakes, tracks)

            frame_idx += 1
            pbar.update(1)

    cap.release()
    if annotator:
        annotator.release()

    detection_stats = {
        "counts":             dict(detection_counts),
        "avg_confidence":     {k: round(sum(v)/len(v), 3) for k, v in detection_conf.items()},
        "unique_tracks":      {k: len(v) for k, v in unique_track_ids.items()},
        "frames_with_enemy":  frames_with_enemy,
        "frames_with_friend": frames_with_friend,
        "max_enemies_frame":  max_enemies_frame,
        "max_friends_frame":  max_friends_frame,
        "total_frames":       frame_idx,
    }

    # Finalize engagement analysis and report
    engagements = analyzer.finalize()
    summary = reporter.generate(
        engagements=engagements,
        realtime_events=realtime_events,
        total_frames=frame_idx,
        fps=fps,
        video_name=video_name,
    )
    logger.info("CV analysis complete for %s", video_name)
    reporter.print_summary(summary, detection_stats)


if __name__ == "__main__":
    main()
