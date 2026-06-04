# CV Service

Computer vision pipeline for analyzing Valorant gameplay footage (Phase 2).

## Status

⚠️ **MVP Only** — Basic YOLO detection works. Integration with coaching pipeline pending.

## Quick Start

```bash
cd services/cv
python main.py path/to/video.mp4 --device 0
```

Output files:
- `output/video_report.json` — Detection stats
- `output/video_events.csv` — Frame-by-frame events

## Architecture

- **Entry point**: `main.py` — CLI for video processing
- **Detector**: `src/detector.py` — YOLO-based enemy/crosshair detection
- **Analyzer**: `src/aim_analyzer.py` — Engagement window analysis
- **Reporter**: `src/reporter.py` — JSON and CSV output
- **Config**: `config.py` — Model paths, confidence thresholds

## Data Flow

```
main.py (video.mp4)
  ↓
VideoCapture + frame loop
  ↓
Detector.detect_frame()  # YOLO inference
  ↓
Analyzer.process_detections()  # Engagement windows
  ↓
Reporter.save()  # JSON + CSV
```

## Models

### Primary: `models/valorant.pt`
- Custom-trained YOLOv8 on Valorant screenshot dataset
- Detects: enemy players, crosshairs
- ~1-2ms per frame on GPU

### Fallback: `models/yolov8n.pt`
- YOLOv8 Nano (COCO-pretrained)
- Maps COCO "person" class → "enemy"
- Used if custom model not found
- ~5ms per frame on CPU

## Configuration

Via `config.py`:
- `MODEL_PATH` — Path to custom model (default: `models/valorant.pt`)
- `FALLBACK_MODEL` — Fallback model (default: `yolov8n`)
- `CONFIDENCE_THRESHOLD` — Detection confidence (default: 0.5)
- `DEVICE` — GPU ID or "cpu" (default: "0")
- `OUTPUT_DIR` — Output directory (default: "output/")

## Dependencies

- ultralytics — YOLOv8 framework
- opencv-python — Video I/O
- numpy — Array processing
- tqdm — Progress bars

## Testing

```bash
python -m pytest services/cv/tests/ -v --ignore=services/cv/tests/test_detector.py
```

Note: `test_detector.py` requires ultralytics to be installed.

## Output Format

### JSON (`video_report.json`)
```json
{
  "video_name": "clip.mp4",
  "total_frames": 1500,
  "fps": 60,
  "detections": {
    "enemy": 450,
    "crosshair": 1500
  },
  "engagement_windows": [
    {"start_frame": 10, "end_frame": 50, "enemies": 2}
  ]
}
```

### CSV (`video_events.csv`)
Frame-by-frame event log for analysis.

## Phase 2 Integration

When integrated with the API:
1. User uploads 3-min clip
2. Server extracts frames at 5fps
3. CV service processes frames (async)
4. CV report merged with Riot report
5. LLM generates coaching report

## Notes

- Custom model needs training (Roboflow dataset available)
- Screen center = crosshair (no detection needed)
- Max 3-min clips for Phase 1
- GPU recommended for real-time (CPU ~10fps)
