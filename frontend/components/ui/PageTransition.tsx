'use client'

import { motion } from 'framer-motion'
import { type ReactNode } from 'react'
import { easeOut } from './motion'

/** Wraps page content with a fade + rise on mount. */
export function PageTransition({
  children,
  className,
}: {
  children: ReactNode
  className?: string
}) {
  return (
    <motion.div
      className={className}
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: easeOut }}
    >
      {children}
    </motion.div>
  )
}
