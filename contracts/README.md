# Contracts

Shared type definitions and schemas for inter-service communication.

## Location

`contracts/schemas.py` — All service contracts live here.

## Import Pattern

```python
from contracts.schemas import RiotReport, CoachingReport, AnalysisResult
```

Never import from service internals. Always use the contract types.

## Core Types

### RiotReport
Valorant player statistics from Riot API.

```python
@dataclass
class RiotReport:
    puuid: str
    game_name: str
    tag_line: str
    current_rank: str | None
    rank_delta: int | None
    matches: list[MatchStat]
    avg_headshot_pct: float
    avg_adr: float
    top_agent: str
    win_rate: float
```

**Source**: `services/riot.service.get_riot_report()`

### CVReport
Video analysis results (Phase 2).

```python
@dataclass
class CVReport:
    video_name: str
    total_frames: int
    fps: float
    detections: dict[str, int]
    engagement_windows: list[dict]
```

**Source**: `services/cv.main.analyze_video()`

### CoachingReport
Personalized coaching insights from Claude.

```python
@dataclass
class CoachingReport:
    summary: str
    top_weakness: str
    tips: list[str]
    encouragement: str
    raw_response: str
```

**Source**: `services/llm.coach.generate_coaching_report()`

### AnalysisResult
Final API response combining all reports.

```python
@dataclass
class AnalysisResult:
    report_id: str
    status: str  # "queued" | "processing" | "done" | "error"
    riot_report: RiotReport | None
    cv_report: CVReport | None
    coaching: CoachingReport | None
    error: str | None
```

**Source**: `services/api.store` (composed by API)

## Versioning

When adding fields to a contract:
1. Add new field with default value to maintain backward compatibility
2. Bump schema version in docstring: `# v1.1`
3. Document in CHANGELOG
4. Update all consumers simultaneously (or gate on version check)

## Notes

- All types are frozen dataclasses for immutability
- Use `None` for optional fields, not `Optional[T]`
- No circular imports — services import contracts, not vice versa
- Update this file when changing contracts
