'use client'

import Image from 'next/image'
import { motion } from 'framer-motion'
import { useState } from 'react'
import { rankIcon } from '@/lib/assets'

/**
 * Competitive tier badge. When `promoted` is true it gets a celebratory
 * glow + pop, used when the player's rank delta is positive.
 */
export function RankBadge({
  rank,
  size = 64,
  promoted = false,
  className = '',
}: {
  rank?: string | null
  size?: number
  promoted?: boolean
  className?: string
}) {
  const src = rankIcon(rank || 'Unranked')
  const [errored, setErrored] = useState(false)
  if (!src || errored) return null

  return (
    <motion.span
      className={`relative inline-flex items-center justify-center ${className}`}
      style={{ width: size, height: size }}
      initial={{ scale: 0.5, opacity: 0, rotate: -8 }}
      animate={{ scale: 1, opacity: 1, rotate: 0 }}
      transition={{ type: 'spring', stiffness: 260, damping: 16, delay: 0.15 }}
    >
      {promoted && (
        <motion.span
          className="pointer-events-none absolute inset-0 rounded-full bg-[#FF4655]/30 blur-xl"
          animate={{ scale: [1, 1.35, 1], opacity: [0.5, 0.9, 0.5] }}
          transition={{ duration: 2.2, repeat: Infinity, ease: 'easeInOut' }}
        />
      )}
      <Image
        src={src}
        alt={rank || 'Unranked'}
        width={size}
        height={size}
        className="relative object-contain drop-shadow-[0_2px_10px_rgba(0,0,0,0.5)]"
        onError={() => setErrored(true)}
      />
    </motion.span>
  )
}
