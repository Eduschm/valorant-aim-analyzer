export interface FaqItem {
  q: string
  a: string
}

/** Shared FAQ content. Plain module (no 'use client') so server components
 * like /pricing can import and filter it without crossing the RSC boundary. */
export const FAQ_ITEMS: FaqItem[] = [
  {
    q: 'Is this allowed by Riot? Will I get banned?',
    a: 'Yes, it is allowed. We only read public match data through the official Riot API and the community HenrikDev API. We never touch the game client, inject anything, or automate gameplay, so there is nothing for anti-cheat to flag.',
  },
  {
    q: 'How accurate is the analysis?',
    a: 'Every stat comes straight from your real match history: headshot %, ADR, win rate, rank, agent and weapon usage. The AI coaching is generated from those exact numbers, so the feedback is grounded in what actually happened in your games, not guesswork.',
  },
  {
    q: 'Is my data safe?',
    a: 'We only request public competitive data tied to your Riot ID. We do not ask for your Riot password, and we never sell your data. Your saved analyses live in your browser unless you create an account.',
  },
  {
    q: 'Do I need to upload clips?',
    a: 'Not for the core report. Phase 1 works entirely from your match stats. Clip analysis (detecting overshoot, undershoot, body-not-head and spray errors frame by frame) is Phase 2 and is included with Pro when it ships.',
  },
  {
    q: 'What does it cost?',
    a: 'The first reports are free, every month. Pro is $9/month for unlimited analyses and comes with a 7-day free trial, so you can cancel before you are charged if it is not for you.',
  },
  {
    q: 'Which regions and modes are supported?',
    a: 'All major regions (NA, EU, AP, KR, BR, LATAM) and ranked competitive matches. We pull your most recent 20 games to build the report.',
  },
]
