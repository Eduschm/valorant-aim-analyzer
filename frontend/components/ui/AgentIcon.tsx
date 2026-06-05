'use client'

import Image from 'next/image'
import { useState } from 'react'
import { agentIcon } from '@/lib/assets'

/** Round agent portrait. Falls back to the agent initial when art is missing. */
export function AgentIcon({
  name,
  size = 36,
  className = '',
}: {
  name?: string | null
  size?: number
  className?: string
}) {
  const src = agentIcon(name)
  const [errored, setErrored] = useState(false)

  if (!src || errored) {
    return (
      <span
        className={`flex items-center justify-center rounded-full bg-[#1F2130] font-display text-xs font-bold text-[#7A8496] ${className}`}
        style={{ width: size, height: size }}
        aria-hidden
      >
        {(name || '?').charAt(0).toUpperCase()}
      </span>
    )
  }

  return (
    <span
      className={`relative inline-block overflow-hidden rounded-full bg-[#0A0B0F] ring-1 ring-white/10 ${className}`}
      style={{ width: size, height: size }}
    >
      <Image
        src={src}
        alt={name || 'agent'}
        width={size}
        height={size}
        className="object-cover"
        onError={() => setErrored(true)}
      />
    </span>
  )
}
