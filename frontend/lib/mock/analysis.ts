/** Mock report matching the ReportResponse shape from services/api/main.py */
export const MOCK_REPORT = {
  report_id: 'mock-001',
  status:    'done',
  riot_report: {
    puuid:            'mock-puuid',
    game_name:        'DemoPlayer',
    tag_line:         'NA1',
    current_rank:     'Gold 2',
    rank_delta:       15,
    avg_headshot_pct: 21.5,
    avg_adr:          142.3,
    win_rate:         0.55,
    top_agent:        'Jett',
    top_weapon:       'Vandal',
    matches: [
      { match_id:'m1', agent:'Jett',   weapon:'Vandal',  kills:18, deaths:12, assists:3,  headshot_pct:25.0, adr:160.0, won:true  },
      { match_id:'m2', agent:'Jett',   weapon:'Vandal',  kills:10, deaths:15, assists:5,  headshot_pct:18.0, adr:120.0, won:false },
      { match_id:'m3', agent:'Reyna',  weapon:'Phantom', kills:14, deaths:13, assists:8,  headshot_pct:22.0, adr:140.0, won:true  },
      { match_id:'m4', agent:'Jett',   weapon:'Vandal',  kills:20, deaths:10, assists:2,  headshot_pct:30.0, adr:180.0, won:true  },
      { match_id:'m5', agent:'Reyna',  weapon:'Vandal',  kills:8,  deaths:16, assists:4,  headshot_pct:15.0, adr:100.0, won:false },
    ],
  },
  cv_report: null,
  coaching: {
    summary:
      'DemoPlayer is sitting at Gold 2 with a 55% win rate and a 21.5% headshot percentage — solid fundamentals, but the HS% is 6-7 points below the Gold average. Jett with Vandal is your comfort pick and it shows.',
    top_weakness:
      'Headshot rate of 21.5% — Gold 2 average is ~28%. Crosshair placement is the bottleneck.',
    tips: [
      'Your 21.5% HS rate means your crosshair is consistently below head height. Spend 5 minutes in The Range each session practicing wall-bang angles at head level before queuing.',
      'On your 10/15 loss, ADR dropped to 120 — 40 below your average. You stop taking duels when you\'re down. Identify one angle to hold and commit to it even when losing.',
      'Your Vandal spray pattern is inconsistent on the m5 loss. Counter-strafe before every shot — full stop, then burst. Watch your movement icon before shooting.',
      'Agent pool is fine — Jett and Reyna both reward aggression. Make sure your first duel of the round is winnable, not just available.',
    ],
    encouragement:
      'The 180 ADR round shows the ceiling is there — just needs consistency.',
    raw_response: '{}',
  },
  error: null,
}

export const mockAnalysisHistory = [
  { id: 'mock-001', riotId: 'DemoPlayer#NA1', createdAt: new Date(Date.now() - 5 * 60000).toISOString(),           status: 'completed', stats: { headshotPercent: 21.5, adr: 142.3 } },
  { id: 'mock-002', riotId: 'DemoPlayer#NA1', createdAt: new Date(Date.now() - 2 * 3600000).toISOString(),         status: 'completed', stats: { headshotPercent: 19.8, adr: 138.1 } },
  { id: 'mock-003', riotId: 'DemoPlayer#NA1', createdAt: new Date(Date.now() - 24 * 3600000).toISOString(),        status: 'completed', stats: { headshotPercent: 23.1, adr: 151.4 } },
  { id: 'mock-004', riotId: 'DemoPlayer#NA1', createdAt: new Date(Date.now() - 2 * 24 * 3600000).toISOString(),    status: 'completed', stats: { headshotPercent: 18.7, adr: 129.8 } },
]

// Legacy shape kept for any components still using the old format
export const mockAnalysis = {
  id:        'mock-001',
  riotId:    'DemoPlayer#NA1',
  createdAt: new Date().toISOString(),
  status:    'completed',
  stats: {
    headshotPercent: 21.5,
    adr:             142.3,
    rankDelta:       '+15 RR',
    matchesAnalyzed: 5,
  },
  weaponStats: [
    { weapon: 'Vandal',  kills: 70,  accuracy: 21.5 },
    { weapon: 'Phantom', kills: 14,  accuracy: 22.0 },
    { weapon: 'Classic', kills: 8,   accuracy: 14.0 },
  ],
  agentStats: [
    { agent: 'Jett',  matches: 4, winRate: 75.0 },
    { agent: 'Reyna', matches: 2, winRate: 50.0 },
  ],
  coachingReport: MOCK_REPORT.coaching.summary,
}
