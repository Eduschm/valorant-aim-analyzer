export const mockAnalysis = {
  id: 'analysis_123',
  riotId: 'Edu#1234',
  createdAt: new Date().toISOString(),
  status: 'completed',
  stats: {
    headshotPercent: 42.5,
    adr: 156.8,
    rankDelta: '+12 RR',
    matchesAnalyzed: 20,
  },
  weaponStats: [
    { weapon: 'Vandal', kills: 145, accuracy: 22.4 },
    { weapon: 'Phantom', kills: 89, accuracy: 19.8 },
    { weapon: 'Classic', kills: 23, accuracy: 15.2 },
    { weapon: 'Operator', kills: 34, accuracy: 28.6 },
    { weapon: 'Judge', kills: 18, accuracy: 45.3 },
  ],
  agentStats: [
    { agent: 'Jett', matches: 8, winRate: 62.5 },
    { agent: 'Reyna', matches: 6, winRate: 58.3 },
    { agent: 'Sage', matches: 4, winRate: 50.0 },
    { agent: 'Killjoy', matches: 2, winRate: 100.0 },
  ],
  coachingReport: `# Your Aim Analysis

## Strengths
- Strong crosshair placement on entry frags
- Consistent first-shot accuracy with Vandal (22.4%)
- Good pre-aim discipline on common angles

## Weaknesses
- Slow target acquisition on wide swings
- Over-aiming on close-range fights (Judge accuracy 45.3%)
- Inconsistent crosshair placement with spray weapons

## Recommendations
1. Practice wide-swing tracking in The Range for 10 min daily
2. Reduce sensitivity by 5-10% to improve spray control
3. Focus on pre-aiming common angles to improve engagement consistency
4. Record and review your close-range fights to identify positioning issues

## Next Steps
- Your ADR of 156.8 is solid, aim for 160+ next week
- Focus on headshot accuracy - get to 45%+
- Play more duelist agents to leverage your aim advantage`,
}

export const mockAnalysisHistory = [
  {
    id: 'analysis_123',
    riotId: 'Edu#1234',
    createdAt: new Date(Date.now() - 1000 * 60 * 5).toISOString(), // 5 mins ago
    status: 'completed',
    stats: {
      headshotPercent: 42.5,
      adr: 156.8,
    },
  },
  {
    id: 'analysis_122',
    riotId: 'Edu#1234',
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(), // 2 hours ago
    status: 'completed',
    stats: {
      headshotPercent: 40.2,
      adr: 152.3,
    },
  },
  {
    id: 'analysis_121',
    riotId: 'Edu#1234',
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(), // 1 day ago
    status: 'completed',
    stats: {
      headshotPercent: 38.9,
      adr: 148.5,
    },
  },
  {
    id: 'analysis_120',
    riotId: 'Edu#1234',
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 48).toISOString(), // 2 days ago
    status: 'completed',
    stats: {
      headshotPercent: 41.2,
      adr: 154.1,
    },
  },
]
