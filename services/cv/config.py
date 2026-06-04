"""Central configuration for the Valorant aim analyzer."""

# --- Model ---
import os
_HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH    = os.path.join(_HERE, "models", "valorant.pt")
FALLBACK_MODEL = os.path.join(_HERE, "models", "yolov8n.pt")
CONFIDENCE_THRESHOLD = 0.45
IOU_THRESHOLD = 0.45
DEVICE = ""                                # "" = auto (GPU if available)

# YOLO class IDs — matches valo-qs4up/valorant-0h6ni dataset
CLASS_IDS = {
    "enemy":        0,
    "enemy_death":  1,
    "enemy_head":   2,
    "friend":       3,
    "friend_head":  4,
    "friend_death": 5,
}

# --- Crosshair detection ---
# HSV range for the default Valorant crosshair (white/cyan)
# Tune these if you use a custom crosshair color
CROSSHAIR_HSV_LOWER = (85, 80, 180)
CROSSHAIR_HSV_UPPER = (105, 255, 255)
CROSSHAIR_FALLBACK_COLOR_BGR = (0, 255, 255)  # cyan fallback

# Screen region to search for crosshair (fraction of frame width/height)
# Center crop reduces false positives from UI elements
CROSSHAIR_SEARCH_REGION = 0.25   # ±25% around frame center

# --- Tracking ---
TRACKER_MAX_AGE = 30         # frames before a track is dropped
TRACKER_MIN_HITS = 2         # detections before a track is confirmed
IOU_MIN_TRACK = 0.2

# --- Aim analysis ---
# Thresholds for classifying aiming mistakes (in pixels, relative to 1080p)
# Scaled automatically to actual resolution at runtime
REFERENCE_HEIGHT = 1080

OVERSHOOT_THRESHOLD_PX = 40        # crosshair passed target by this many px
UNDERSHOOT_THRESHOLD_PX = 30       # stopped this far short of target
HEAD_PROXIMITY_PX = 25             # head considered "available" if crosshair this close
BODY_NOT_HEAD_THRESHOLD_PX = 60    # aimed at body when head was within reach
MOVEMENT_BLUR_THRESHOLD = 18.0     # px/frame crosshair movement = "moving while shooting"
SPRAY_DEVIATION_THRESHOLD = 55     # std-dev of crosshair path during burst

MIN_ENGAGEMENT_FRAMES = 4          # ignore flickers shorter than this

# --- Reporting ---
ANNOTATE_VIDEO = True
ANNOTATE_FPS_LIMIT = 0             # 0 = match source fps
OUTPUT_VIDEO_CODEC = "mp4v"
REPORT_FORMAT = "both"             # "json" | "csv" | "both"

MISTAKE_COLORS = {
    "overshoot":            (0, 60, 255),    # red-orange
    "undershoot":           (0, 165, 255),   # orange
    "body_not_head":        (0, 255, 255),   # yellow
    "wrong_target":         (255, 0, 200),   # magenta
    "moving_while_shooting":(255, 200, 0),   # sky-blue
    "spray_control":        (128, 0, 255),   # purple
}
