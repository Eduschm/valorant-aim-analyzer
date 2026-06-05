"""
Shared contracts between services.
All inter-service communication uses these typed dataclasses.
Never import from one service's internals into another — import from here.
"""

from __future__ import annotations
from dataclasses import dataclass, field


# ---------- CV service output ----------

@dataclass
class MistakeEvent:
    mistake_type: str       # overshoot | undershoot | body_not_head | wrong_target |
                            # moving_while_shooting | spray_control
    frame_idx:    int
    time_s:       float
    track_id:     int | None
    severity:     float     # 0-1
    description:  str


@dataclass
class CVReport:
    video_name:            str
    duration_s:            float
    total_engagements:     int
    total_mistakes:        int
    mistakes_per_minute:   float
    mistake_counts:        dict[str, int]
    avg_severity:          dict[str, float]
    impact_scores:         dict[str, float]
    most_impactful:        str | None
    ranked_mistakes:       list[dict]
    events:                list[MistakeEvent]


# ---------- Riot service output ----------

@dataclass
class MatchStat:
    match_id:     str
    agent:        str
    weapon:       str
    kills:        int
    deaths:       int
    assists:      int
    headshot_pct: float     # 0-100
    adr:          float     # avg damage per round
    won:          bool


@dataclass
class RiotReport:
    puuid:            str
    game_name:        str
    tag_line:         str
    current_rank:     str
    rank_delta:       int       # rank change over last N matches (+ = up, - = down)
    matches:          list[MatchStat]
    avg_headshot_pct: float
    avg_adr:          float
    top_agent:        str
    top_weapon:       str
    win_rate:         float
    region:           str = "na"  # resolved region (auto-detected if not passed explicitly)


# ---------- LLM service output ----------

@dataclass
class CoachingReport:
    summary:          str           # 2-3 sentence overview
    top_weakness:     str           # single biggest issue
    tips:             list[str]     # 3-5 actionable tips
    encouragement:    str           # motivational closing line
    raw_response:     str           # full LLM output for debugging


# ---------- Combined analysis request/response ----------

@dataclass
class AnalysisRequest:
    user_id:      str
    riot_id:      str       # e.g. "PlayerName#NA1"
    video_path:   str | None = None


@dataclass
class AnalysisResult:
    request:        AnalysisRequest
    cv_report:      CVReport | None
    riot_report:    RiotReport | None
    coaching:       CoachingReport | None
