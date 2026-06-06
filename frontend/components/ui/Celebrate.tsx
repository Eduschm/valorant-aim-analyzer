'use client'

import { useEffect, useRef } from 'react'
import confetti from 'canvas-confetti'

const VALORANT_COLORS = ['#4361EE', '#8E9DF5', '#F0F1F5', '#FFD166']

/** Fire a one-shot confetti burst. `intense` adds extra cannons for rank-ups. */
export function fireConfetti(intense = false) {
  if (typeof window === 'undefined' || typeof document === 'undefined') return
  const prefersReduced = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
  if (prefersReduced) return
  // Skip in environments without a real 2D canvas (e.g. jsdom in tests),
  // where canvas-confetti's animation loop would throw on a null context.
  try {
    if (!document.createElement('canvas').getContext('2d')) return
  } catch {
    return
  }

  const base = { colors: VALORANT_COLORS, disableForReducedMotion: true }

  confetti({ ...base, particleCount: 90, spread: 70, origin: { y: 0.6 }, startVelocity: 45 })
  setTimeout(() => confetti({ ...base, particleCount: 50, angle: 60, spread: 55, origin: { x: 0 } }), 120)
  setTimeout(() => confetti({ ...base, particleCount: 50, angle: 120, spread: 55, origin: { x: 1 } }), 120)

  if (intense) {
    setTimeout(
      () => confetti({ ...base, particleCount: 120, spread: 100, origin: { y: 0.5 }, scalar: 1.1, startVelocity: 55 }),
      450,
    )
  }
}

/**
 * Mount-once celebration. Fires confetti a single time when `trigger`
 * first becomes true (guards against React re-renders / poll loops).
 */
export function Celebrate({ trigger, intense = false }: { trigger: boolean; intense?: boolean }) {
  const fired = useRef(false)
  useEffect(() => {
    if (trigger && !fired.current) {
      fired.current = true
      fireConfetti(intense)
    }
  }, [trigger, intense])
  return null
}
