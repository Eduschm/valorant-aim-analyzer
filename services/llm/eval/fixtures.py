"""
Five fixture RiotReports covering Iron → Immortal rank brackets.
Each fixture has at least one stat measurably below the rank median so the eval
can assert that top_weakness targets a weak stat.

Rank medians used (approximate, from community data):
  Iron/Bronze  — HS% ~12%, ADR ~100, win_rate ~45%
  Silver/Gold  — HS% ~17%, ADR ~130, win_rate ~50%
  Plat/Diamond — HS% ~22%, ADR ~155, win_rate ~52%
  Immortal     — HS% ~27%, ADR ~175, win_rate ~54%
"""

from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from contracts.schemas import RiotReport, MatchStat


def _ms(match_id: str, agent: str, kills: int, deaths: int, hs_pct: float, adr: float, won: bool) -> MatchStat:
    return MatchStat(
        match_id=match_id, agent=agent, weapon="Vandal",
        kills=kills, deaths=deaths, assists=2,
        headshot_pct=hs_pct, adr=adr, won=won, competitive_tier=0,
    )


# Iron 2 — HS% 8% (well below median 12%), ADR 90
IRON_REPORT = RiotReport(
    puuid="iron-puuid", game_name="IronPlayer", tag_line="NA1",
    current_rank="Iron 2", rank_delta=-1,
    matches=[
        _ms("m1", "Reyna",  8,  14, 8.0,  90.0, False),
        _ms("m2", "Reyna",  6,  15, 7.5,  88.0, False),
        _ms("m3", "Reyna",  9,  13, 9.0,  92.0, True),
    ],
    avg_headshot_pct=8.2, avg_adr=90.0, top_agent="Reyna",
    top_weapon="Vandal", win_rate=0.33,
)

# Gold 1 — ADR 105 (below median 130), HS% close to median
GOLD_REPORT = RiotReport(
    puuid="gold-puuid", game_name="GoldPlayer", tag_line="EU1",
    current_rank="Gold 1", rank_delta=2,
    matches=[
        _ms("m1", "Jett",  14, 12, 17.0, 105.0, True),
        _ms("m2", "Jett",  10, 13, 16.5, 100.0, False),
        _ms("m3", "Jett",  12, 11, 18.0, 110.0, True),
        _ms("m4", "Jett",  11, 14, 15.0, 102.0, False),
    ],
    avg_headshot_pct=16.6, avg_adr=104.2, top_agent="Jett",
    top_weapon="Vandal", win_rate=0.5,
)

# Platinum 2 — win rate 36% (below median 52%), other stats near median
PLAT_REPORT = RiotReport(
    puuid="plat-puuid", game_name="PlatPlayer", tag_line="KR1",
    current_rank="Platinum 2", rank_delta=-3,
    matches=[
        _ms("m1", "Sage",   11, 10, 21.0, 150.0, False),
        _ms("m2", "Sage",   13, 11, 22.0, 158.0, True),
        _ms("m3", "Sage",    9, 12, 20.0, 145.0, False),
        _ms("m4", "Sage",   10, 13, 19.0, 140.0, False),
        _ms("m5", "Sage",   12, 10, 23.0, 155.0, False),
    ],
    avg_headshot_pct=21.0, avg_adr=149.6, top_agent="Sage",
    top_weapon="Vandal", win_rate=0.2,
)

# Diamond 1 — HS% 19% (below median 22%), ADR slightly below
DIAMOND_REPORT = RiotReport(
    puuid="dia-puuid", game_name="DiamondPlayer", tag_line="AP1",
    current_rank="Diamond 1", rank_delta=1,
    matches=[
        _ms("m1", "Neon",   18, 10, 19.0, 148.0, True),
        _ms("m2", "Neon",   16, 11, 18.5, 145.0, True),
        _ms("m3", "Neon",   20,  9, 20.0, 152.0, True),
        _ms("m4", "Neon",   15, 12, 18.0, 143.0, False),
    ],
    avg_headshot_pct=18.9, avg_adr=147.0, top_agent="Neon",
    top_weapon="Vandal", win_rate=0.75,
)

# Immortal 1 — ADR 160 (below median 175), HS% slightly low
IMMORTAL_REPORT = RiotReport(
    puuid="imm-puuid", game_name="ImmortalPlayer", tag_line="NA2",
    current_rank="Immortal 1", rank_delta=0,
    matches=[
        _ms("m1", "Chamber", 22, 8, 24.0, 162.0, True),
        _ms("m2", "Chamber", 19, 9, 25.0, 158.0, True),
        _ms("m3", "Chamber", 20, 8, 23.0, 160.0, False),
        _ms("m4", "Chamber", 18, 10, 22.0, 155.0, True),
        _ms("m5", "Chamber", 21, 9, 26.0, 165.0, True),
    ],
    avg_headshot_pct=24.0, avg_adr=160.0, top_agent="Chamber",
    top_weapon="Vandal", win_rate=0.8,
)

ALL_FIXTURES = [IRON_REPORT, GOLD_REPORT, PLAT_REPORT, DIAMOND_REPORT, IMMORTAL_REPORT]

# Rank medians for the eval assertions
RANK_MEDIANS: dict[str, dict[str, float]] = {
    "Iron/Bronze":      {"hs_pct": 12.0, "adr": 100.0, "win_rate": 0.45},
    "Silver/Gold":      {"hs_pct": 17.0, "adr": 130.0, "win_rate": 0.50},
    "Platinum/Diamond": {"hs_pct": 22.0, "adr": 155.0, "win_rate": 0.52},
    "Immortal/Radiant": {"hs_pct": 27.0, "adr": 175.0, "win_rate": 0.54},
}
