"""Fixture RiotReports for LLM coaching quality evals.

Each fixture has at least one stat below the rank median so the LLM
can identify a meaningful weakness in top_weakness.
"""

from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from contracts.schemas import RiotReport, MatchStat

# Approximate rank medians used in eval assertions
RANK_MEDIANS: dict[str, dict[str, float]] = {
    "Iron":     {"hs_pct": 12.0, "adr": 100.0, "kd": 0.80},
    "Bronze":   {"hs_pct": 15.0, "adr": 110.0, "kd": 0.85},
    "Silver":   {"hs_pct": 17.0, "adr": 120.0, "kd": 0.90},
    "Gold":     {"hs_pct": 20.0, "adr": 130.0, "kd": 1.00},
    "Platinum": {"hs_pct": 22.0, "adr": 135.0, "kd": 1.05},
    "Diamond":  {"hs_pct": 25.0, "adr": 140.0, "kd": 1.10},
    "Immortal": {"hs_pct": 28.0, "adr": 150.0, "kd": 1.20},
    "Radiant":  {"hs_pct": 30.0, "adr": 155.0, "kd": 1.30},
}


def _kd(report: RiotReport) -> float:
    total_kills  = sum(m.kills  for m in report.matches)
    total_deaths = sum(m.deaths for m in report.matches) or 1
    return round(total_kills / total_deaths, 2)


def get_below_median_stats(report: RiotReport) -> list[str]:
    """Return stat names that are below median for the report's rank tier."""
    rank_tier = next(
        (k for k in RANK_MEDIANS if report.current_rank.lower().startswith(k.lower())),
        None,
    )
    if rank_tier is None:
        return []
    medians = RANK_MEDIANS[rank_tier]
    below = []
    if report.avg_headshot_pct < medians["hs_pct"]:
        below.append("hs_pct")
    if report.avg_adr < medians["adr"]:
        below.append("adr")
    if _kd(report) < medians["kd"]:
        below.append("kd")
    return below


# Five fixtures covering Iron → Diamond ranks

IRON_REPORT = RiotReport(
    puuid="iron-puuid",
    game_name="IronPlayer",
    tag_line="EU1",
    current_rank="Iron 2",
    rank_delta=-10,
    matches=[
        MatchStat("m1", "Sage",    "Classic", 5,  18, 2, 8.0,  85.0, False),
        MatchStat("m2", "Sage",    "Classic", 6,  15, 3, 7.5,  80.0, False),
        MatchStat("m3", "Sage",    "Classic", 4,  17, 1, 9.0,  75.0, False),
        MatchStat("m4", "Sage",    "Classic", 7,  16, 0, 8.0,  90.0, False),
        MatchStat("m5", "Phoenix", "Classic", 8,  14, 2, 10.0, 95.0, True),
    ],
    avg_headshot_pct=8.5,   # below Iron median (12)
    avg_adr=85.0,           # below Iron median (100)
    top_agent="Sage",
    top_weapon="Classic",
    win_rate=0.20,
    region="eu",
)

GOLD_REPORT = RiotReport(
    puuid="gold-puuid",
    game_name="GoldPlayer",
    tag_line="NA1",
    current_rank="Gold 3",
    rank_delta=+5,
    matches=[
        MatchStat("m1", "Jett",   "Vandal",  14, 12, 4, 17.0, 125.0, True),
        MatchStat("m2", "Jett",   "Vandal",  12, 13, 6, 16.5, 118.0, False),
        MatchStat("m3", "Jett",   "Phantom", 16, 11, 3, 18.0, 130.0, True),
        MatchStat("m4", "Reyna",  "Vandal",  10, 14, 2, 15.0, 110.0, False),
        MatchStat("m5", "Jett",   "Vandal",  13, 12, 5, 17.5, 122.0, True),
    ],
    avg_headshot_pct=16.8,  # below Gold median (20)
    avg_adr=121.0,
    top_agent="Jett",
    top_weapon="Vandal",
    win_rate=0.60,
    region="na",
)

PLATINUM_REPORT = RiotReport(
    puuid="plat-puuid",
    game_name="PlatPlayer",
    tag_line="NA1",
    current_rank="Platinum 1",
    rank_delta=+12,
    matches=[
        MatchStat("m1", "Chamber", "Operator", 18, 9,  3, 24.0, 145.0, True),
        MatchStat("m2", "Chamber", "Operator", 15, 11, 4, 23.0, 138.0, True),
        MatchStat("m3", "Chamber", "Vandal",   12, 13, 5, 20.0, 128.0, False),
        MatchStat("m4", "Chamber", "Operator", 17, 10, 2, 22.0, 140.0, True),
        MatchStat("m5", "Killjoy", "Phantom",  10, 12, 7, 19.0, 122.0, False),
    ],
    avg_headshot_pct=21.6,  # below Platinum median (22)
    avg_adr=134.6,          # below Platinum median (135)
    top_agent="Chamber",
    top_weapon="Operator",
    win_rate=0.60,
    region="na",
)

DIAMOND_REPORT = RiotReport(
    puuid="diamond-puuid",
    game_name="DiamondPlayer",
    tag_line="KR1",
    current_rank="Diamond 2",
    rank_delta=-8,
    matches=[
        MatchStat("m1", "Neon",     "Vandal",  20, 10, 5, 23.0, 148.0, True),
        MatchStat("m2", "Neon",     "Vandal",  18, 12, 4, 22.0, 142.0, False),
        MatchStat("m3", "Neon",     "Phantom", 15, 13, 6, 21.0, 135.0, False),
        MatchStat("m4", "Raze",     "Vandal",  19, 11, 3, 24.0, 150.0, True),
        MatchStat("m5", "Neon",     "Vandal",  17, 12, 5, 22.0, 143.0, False),
    ],
    avg_headshot_pct=22.4,  # below Diamond median (25)
    avg_adr=143.6,
    top_agent="Neon",
    top_weapon="Vandal",
    win_rate=0.40,
    region="kr",
)

IMMORTAL_REPORT = RiotReport(
    puuid="immo-puuid",
    game_name="ImmoPlayer",
    tag_line="AP1",
    current_rank="Immortal 1",
    rank_delta=+20,
    matches=[
        MatchStat("m1", "Omen",    "Vandal",  22, 9,  6, 30.0, 162.0, True),
        MatchStat("m2", "Omen",    "Phantom", 20, 10, 5, 29.0, 158.0, True),
        MatchStat("m3", "Skye",    "Vandal",  18, 11, 8, 27.0, 152.0, True),
        MatchStat("m4", "Omen",    "Vandal",  21, 9,  4, 31.0, 165.0, True),
        MatchStat("m5", "Viper",   "Phantom", 15, 13, 7, 25.0, 140.0, False),
    ],
    avg_headshot_pct=28.4,
    avg_adr=155.4,
    top_agent="Omen",
    top_weapon="Vandal",
    win_rate=0.80,
    region="ap",
)

ALL_FIXTURES = [
    IRON_REPORT,
    GOLD_REPORT,
    PLATINUM_REPORT,
    DIAMOND_REPORT,
    IMMORTAL_REPORT,
]
