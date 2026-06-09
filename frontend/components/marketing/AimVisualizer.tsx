'use client'

import { useEffect, useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Target, Zap, RotateCcw, AlertTriangle, Eye, Crosshair } from 'lucide-react'

type Weapon = 'Vandal' | 'Phantom' | 'Operator' | 'Sheriff'
type AnalysisType = 'perfect' | 'overshoot' | 'undershoot' | 'spray'

interface TargetItem {
  id: number
  x: number // percentage 10-90
  y: number // percentage 20-80
  size: number
  status: 'active' | 'hit' | 'missed'
}

export function AimVisualizer() {
  const [weapon, setWeapon] = useState<Weapon>('Vandal')
  const [mode, setMode] = useState<AnalysisType>('perfect')
  const [isPlaying, setIsPlaying] = useState(true)
  const [targets, setTargets] = useState<TargetItem[]>([])
  const [crosshairPos, setCrosshairPos] = useState({ x: 50, y: 50 })
  const [laserLine, setLaserLine] = useState<{ x1: number; y1: number; x2: number; y2: number } | null>(null)
  const [diagnosticText, setDiagnosticText] = useState('SYSTEM INIT: Ready to simulate.')
  const [diagnosticCode, setDiagnosticCode] = useState('OK_AIM_STEADY')
  const [stats, setStats] = useState({ shots: 0, headshots: 0, score: 0 })
  const [floatingTexts, setFloatingTexts] = useState<{ id: number; text: string; x: number; y: number; color: string }[]>([])
  const [manualMode, setManualMode] = useState(false)

  const containerRef = useRef<HTMLDivElement>(null)
  const targetIdRef = useRef(0)
  const textIdRef = useRef(0)

  // Trigger sound-like click or feedback visually
  const spawnTarget = () => {
    targetIdRef.current += 1
    const newTarget: TargetItem = {
      id: targetIdRef.current,
      x: 20 + Math.random() * 60,
      y: 20 + Math.random() * 50,
      size: weapon === 'Operator' ? 32 : 24,
      status: 'active',
    }
    setTargets([newTarget])
    return newTarget
  }

  // Handle manual user clicks
  const handleCanvasClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!containerRef.current) return
    const rect = containerRef.current.getBoundingClientRect()
    const clickX = ((e.clientX - rect.left) / rect.width) * 100
    const clickY = ((e.clientY - rect.top) / rect.height) * 100

    setStats(s => ({ ...s, shots: s.shots + 1 }))

    // Laser fire line from crosshair (or center) to click position
    setLaserLine({ x1: crosshairPos.x, y1: crosshairPos.y, x2: clickX, y2: clickY })
    setTimeout(() => setLaserLine(null), 180)

    // Check hit on current active targets
    const activeTarget = targets.find(t => t.status === 'active')
    if (activeTarget) {
      const dist = Math.hypot(clickX - activeTarget.x, clickY - activeTarget.y)
      const isHit = dist <= (activeTarget.size / rect.width) * 100 * 2.5 // generous hit radius

      // Classify the aim relative to target head center
      let classification = 'perfect'
      let text = 'Perfect Headshot!'
      let color = 'text-emerald-400'
      const dx = clickX - activeTarget.x
      const dy = clickY - activeTarget.y

      if (isHit) {
        if (Math.abs(dx) < 1.5 && Math.abs(dy) < 1.5) {
          classification = 'perfect'
          text = 'Perfect Headshot! [100%]'
          color = 'text-emerald-400 font-bold'
          setStats(s => ({ ...s, headshots: s.headshots + 1, score: s.score + 100 }))
          setDiagnosticCode('AIM_PERFECT')
          setDiagnosticText('ANALYSIS: Zero deviation. Centered click.')
        } else {
          // slight dev
          text = 'Body Hit (Aim Low)'
          color = 'text-yellow-400'
          setStats(s => ({ ...s, score: s.score + 50 }))
          setDiagnosticCode('AIM_BODY_LOW')
          setDiagnosticText('ANALYSIS: Crosshair sits 8px below head level.')
        }
        setTargets(targets.map(t => t.id === activeTarget.id ? { ...t, status: 'hit' } : t))
      } else {
        // missed
        if (dy < -2) {
          text = 'Overshoot (Aim High)'
          color = 'text-red-400'
          setDiagnosticCode('AIM_OVERSHOOT')
          setDiagnosticText('ANALYSIS: Overshot target head by 14px.')
        } else if (dy > 2) {
          text = 'Undershoot (Aim Low)'
          color = 'text-orange-400'
          setDiagnosticCode('AIM_UNDERSHOOT')
          setDiagnosticText('ANALYSIS: Stopped short by 18px (undershoot).')
        } else {
          text = 'Spray Deviation'
          color = 'text-purple-400'
          setDiagnosticCode('AIM_SPRAY_DEV')
          setDiagnosticText('ANALYSIS: Heavy horizontal recoil (spray dispersion).')
        }
      }

      textIdRef.current += 1
      setFloatingTexts(ft => [...ft, {
        id: textIdRef.current,
        text,
        x: clickX,
        y: clickY - 5,
        color,
      }])

      // Clear text after animation
      const currentTextId = textIdRef.current
      setTimeout(() => {
        setFloatingTexts(ft => ft.filter(f => f.id !== currentTextId))
        if (!manualMode) spawnTarget()
      }, 1500)
    }

    setCrosshairPos({ x: clickX, y: clickY })
  }

  // Automatic simulation engine
  useEffect(() => {
    if (!isPlaying || manualMode) return

    let timeoutId: NodeJS.Timeout
    let active = true

    const runLoop = async () => {
      if (!active) return
      const t = spawnTarget()

      // 1. Wait a bit at target spawn
      await new Promise(r => { timeoutId = setTimeout(r, 400) })
      if (!active) return

      // 2. Aim logic based on selected mode
      let targetAimX = t.x
      let targetAimY = t.y

      if (mode === 'overshoot') {
        targetAimX = t.x + (Math.random() > 0.5 ? 4 : -4)
        targetAimY = t.y - (3 + Math.random() * 3) // aiming too high
      } else if (mode === 'undershoot') {
        targetAimX = t.x + (Math.random() > 0.5 ? 3 : -3)
        targetAimY = t.y + (3 + Math.random() * 3) // aiming too low
      } else if (mode === 'spray') {
        targetAimX = t.x + (5 + Math.random() * 6)
        targetAimY = t.y + (2 + Math.random() * 4)
      }

      // Smooth move crosshair
      setCrosshairPos({ x: targetAimX, y: targetAimY })
      setStats(s => ({ ...s, shots: s.shots + 1 }))

      // 3. Shoot laser
      setLaserLine({ x1: 50, y1: 50, x2: targetAimX, y2: targetAimY })
      await new Promise(r => { timeoutId = setTimeout(r, 150) })
      if (!active) return
      setLaserLine(null)

      // 4. Classify outcome
      let label = ''
      let colorClass = ''
      if (mode === 'perfect') {
        label = 'Perfect Headshot! [100%]'
        colorClass = 'text-emerald-400 font-bold'
        setStats(s => ({ ...s, headshots: s.headshots + 1, score: s.score + 100 }))
        setTargets(curr => curr.map(item => item.id === t.id ? { ...item, status: 'hit' } : item))
        setDiagnosticCode('AIM_PERFECT')
        setDiagnosticText('COACH: Center hit. Crosshair perfectly placed on target head.')
      } else if (mode === 'overshoot') {
        label = 'Overshoot (+14px)'
        colorClass = 'text-red-400 font-semibold'
        setTargets(curr => curr.map(item => item.id === t.id ? { ...item, status: 'missed' } : item))
        setDiagnosticCode('AIM_ERR_OVERSHOOT')
        setDiagnosticText('COACH: Target overshot. Reduce mouse sensitivity by 5-10% or practice stop-flicks.')
      } else if (mode === 'undershoot') {
        label = 'Undershoot (-18px)'
        colorClass = 'text-orange-400 font-semibold'
        setTargets(curr => curr.map(item => item.id === t.id ? { ...item, status: 'missed' } : item))
        setDiagnosticCode('AIM_ERR_UNDERSHOOT')
        setDiagnosticText('COACH: Target undershot. Make sure to full-swipe or verify desk space constraints.')
      } else {
        label = 'Recoil Deviation'
        colorClass = 'text-purple-400 font-semibold'
        setTargets(curr => curr.map(item => item.id === t.id ? { ...item, status: 'missed' } : item))
        setDiagnosticCode('AIM_ERR_SPRAY')
        setDiagnosticText('COACH: Spray control error. Limit sprays to 3-5 bullets. Reset weapon bloom before refiring.')
      }

      textIdRef.current += 1
      const textId = textIdRef.current
      setFloatingTexts(curr => [...curr, { id: textId, text: label, x: targetAimX, y: targetAimY - 6, color: colorClass }])

      // Clean floating text
      setTimeout(() => {
        setFloatingTexts(curr => curr.filter(item => item.id !== textId))
      }, 1500)

      // Reset crosshair to center
      await new Promise(r => { timeoutId = setTimeout(r, 800) })
      if (!active) return
      setCrosshairPos({ x: 50, y: 50 })

      // Next spawn cycle
      await new Promise(r => { timeoutId = setTimeout(r, 600) })
      if (active) runLoop()
    }

    runLoop()

    return () => {
      active = false
      clearTimeout(timeoutId)
    }
  }, [isPlaying, mode, weapon, manualMode])

  const resetStats = () => {
    setStats({ shots: 0, headshots: 0, score: 0 })
    setTargets([])
    setFloatingTexts([])
    setCrosshairPos({ x: 50, y: 50 })
    setDiagnosticText('SYSTEM: Stats reset. Ready for next simulation.')
    setDiagnosticCode('OK_AIM_STEADY')
    if (manualMode) spawnTarget()
  }

  return (
    <div className="flex flex-col h-full rounded-2xl border border-[#1F2130] bg-[#0A0D1A] overflow-hidden">
      {/* Simulation title bar */}
      <div className="flex items-center justify-between border-b border-[#1F2130] bg-[#0E1225] px-5 py-3.5">
        <div className="flex items-center gap-2">
          <span className="flex h-2 w-2 rounded-full bg-val-accent animate-pulse" />
          <span className="font-display text-sm font-semibold tracking-wider uppercase text-[#F0F1F5]">
            Interactive YOLO Aim Classifier Simulator
          </span>
        </div>
        <div className="flex items-center gap-2 text-xs text-[#7A8496]">
          <span className="border border-[#1F2130] px-2 py-0.5 rounded uppercase font-mono">
            {manualMode ? 'Manual Testing' : 'Auto Simulation'}
          </span>
        </div>
      </div>

      {/* Simulator canvas */}
      <div
        ref={containerRef}
        onClick={manualMode ? handleCanvasClick : undefined}
        className={`relative h-64 md:h-72 w-full border-b border-[#1F2130] bg-radial-glow overflow-hidden ${
          manualMode ? 'cursor-crosshair' : 'cursor-default'
        }`}
        style={{
          backgroundImage:
            'radial-gradient(circle, rgba(67, 97, 238, 0.05) 1px, transparent 1px)',
          backgroundSize: '20px 20px',
        }}
      >
        {/* Radar grids */}
        <div className="absolute inset-0 flex items-center justify-center opacity-10 pointer-events-none">
          <div className="border border-white rounded-full w-24 h-24" />
          <div className="border border-white rounded-full w-48 h-48" />
          <div className="border border-white rounded-full w-72 h-72" />
          <div className="absolute h-full w-[1px] bg-white" />
          <div className="absolute w-full h-[1px] bg-white" />
        </div>

        {/* Target Dummies */}
        <AnimatePresence>
          {targets.map(t => (
            t.status === 'active' ? (
              <div
                key={t.id}
                style={{ left: `${t.x}%`, top: `${t.y}%` }}
                className="absolute -translate-x-1/2 -translate-y-1/2 select-none z-10 animate-target-pop"
              >
                {/* Target dummy Head */}
                <div
                  className="rounded-full bg-red-600/35 border-2 border-red-500 flex items-center justify-center relative shadow-[0_0_15px_rgba(239,68,68,0.4)]"
                  style={{ width: `${t.size}px`, height: `${t.size}px` }}
                >
                  <div className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />
                </div>
                {/* Target dummy Body */}
                <div
                  className="w-12 h-16 border border-[#2A2D40] bg-[#11131E]/80 rounded-t-xl mx-auto mt-0.5 opacity-60 flex justify-center pt-1"
                  style={{ width: `${t.size * 1.6}px` }}
                />
              </div>
            ) : t.status === 'hit' ? (
              // Hit glow animation
              <div
                key={t.id}
                style={{ left: `${t.x}%`, top: `${t.y}%` }}
                className="absolute -translate-x-1/2 -translate-y-1/2 pointer-events-none z-10"
              >
                <div className="w-8 h-8 rounded-full border-2 border-emerald-400 bg-emerald-500/10 animate-hit-glow" />
              </div>
            ) : null
          ))}
        </AnimatePresence>

        {/* Laser shooting line */}
        {laserLine && (
          <svg className="absolute inset-0 w-full h-full pointer-events-none z-20">
            <line
              x1={`${laserLine.x1}%`}
              y1={`${laserLine.y1}%`}
              x2={`${laserLine.x2}%`}
              y2={`${laserLine.y2}%`}
              stroke={weapon === 'Operator' ? '#ff4655' : weapon === 'Phantom' ? '#8854d0' : '#4361EE'}
              className="animate-laser-fade"
              strokeLinecap="round"
            />
          </svg>
        )}

        {/* Crosshair indicator */}
        <motion.div
          animate={{ left: `${crosshairPos.x}%`, top: `${crosshairPos.y}%` }}
          transition={{ type: 'spring', stiffness: manualMode ? 500 : 250, damping: 28 }}
          className="absolute -translate-x-1/2 -translate-y-1/2 pointer-events-none z-20 flex items-center justify-center"
        >
          {/* Valorant crosshair lines */}
          <div className="relative w-6 h-6 flex items-center justify-center">
            <div className="absolute w-[2px] h-[8px] bg-emerald-400 top-0" style={{ transform: 'translateY(-2px)' }} />
            <div className="absolute w-[2px] h-[8px] bg-emerald-400 bottom-0" style={{ transform: 'translateY(2px)' }} />
            <div className="absolute h-[2px] w-[8px] bg-emerald-400 left-0" style={{ transform: 'translateX(-2px)' }} />
            <div className="absolute h-[2px] w-[8px] bg-emerald-400 right-0" style={{ transform: 'translateX(2px)' }} />
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 opacity-90" />
          </div>
        </motion.div>

        {/* Floating feedback texts */}
        {floatingTexts.map(f => (
          <motion.div
            key={f.id}
            initial={{ opacity: 0, y: 0 }}
            animate={{ opacity: 1, y: -20 }}
            exit={{ opacity: 0 }}
            style={{ left: `${f.x}%`, top: `${f.y}%` }}
            className={`absolute -translate-x-1/2 text-xs font-mono px-2 py-0.5 rounded bg-[#070B18]/90 border border-white/10 shadow-lg z-30 ${f.color}`}
          >
            {f.text}
          </motion.div>
        ))}

        {/* Diagnostic HUD Overlay */}
        <div className="absolute bottom-3 left-4 right-4 pointer-events-none flex justify-between items-end font-mono text-[10px] text-[#7A8496] z-10 bg-gradient-to-t from-[#0A0D1A]/90 to-transparent p-1.5 rounded">
          <div className="flex flex-col gap-0.5">
            <span className="text-[#42495A] uppercase font-bold text-[9px] tracking-wider">Diagnostic Code</span>
            <span className={diagnosticCode.includes('ERR') ? 'text-val-danger' : 'text-emerald-400'}>
              {diagnosticCode}
            </span>
          </div>
          <div className="text-right max-w-[60%]">
            <span className="text-[#F0F1F5] truncate block">{diagnosticText}</span>
          </div>
        </div>
      </div>

      {/* Control panel and HUD stats */}
      <div className="p-5 bg-[#0A0D1A] space-y-4">
        {/* Performance metrics display */}
        <div className="grid grid-cols-3 gap-3 border border-[#1F2130] bg-[#0C1024] p-3 rounded-lg text-center font-mono">
          <div>
            <span className="block text-[10px] uppercase text-[#42495A] tracking-wider">Score</span>
            <span className="text-lg font-bold text-[#F0F1F5]">{stats.score}</span>
          </div>
          <div>
            <span className="block text-[10px] uppercase text-[#42495A] tracking-wider">HS%</span>
            <span className="text-lg font-bold text-emerald-400">
              {stats.shots > 0 ? ((stats.headshots / stats.shots) * 100).toFixed(0) : '0'}%
            </span>
          </div>
          <div>
            <span className="block text-[10px] uppercase text-[#42495A] tracking-wider">Shots Fired</span>
            <span className="text-lg font-bold text-[#7A8496]">{stats.shots}</span>
          </div>
        </div>

        {/* Simulation Selector controls */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <span className="block text-[10px] uppercase text-[#42495A] tracking-widest font-bold">
              Classification Filter
            </span>
            <div className="grid grid-cols-2 gap-1.5 text-xs">
              {(['perfect', 'overshoot', 'undershoot', 'spray'] as AnalysisType[]).map(t => (
                <button
                  key={t}
                  onClick={() => {
                    setMode(t)
                    setManualMode(false)
                  }}
                  className={`px-3 py-2 border rounded font-semibold uppercase text-[10px] transition ${
                    mode === t && !manualMode
                      ? 'bg-val-accent/15 border-val-accent text-val-accent'
                      : 'bg-[#111424] border-[#1F2130] text-[#7A8496] hover:border-[#2A3150] hover:text-[#C7CDDA]'
                  }`}
                >
                  {t === 'perfect' ? '🎯 Perfect' : t === 'overshoot' ? '↗️ Overshoot' : t === 'undershoot' ? '↘️ Undershoot' : '💨 Spray Control'}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-2">
            <span className="block text-[10px] uppercase text-[#42495A] tracking-widest font-bold">
              Simulator Mode
            </span>
            <div className="flex gap-2">
              <button
                onClick={() => {
                  setManualMode(true)
                  setTargets([])
                  spawnTarget()
                }}
                className={`flex-1 flex items-center justify-center gap-1.5 px-3 py-2 border rounded font-semibold text-xs transition uppercase text-[10px] ${
                  manualMode
                    ? 'bg-emerald-500/15 border-emerald-500 text-emerald-400'
                    : 'bg-[#111424] border-[#1F2130] text-[#7A8496] hover:border-[#2A3150]'
                }`}
              >
                <Crosshair className="w-3.5 h-3.5" /> Manual Click
              </button>

              <button
                onClick={resetStats}
                className="flex items-center justify-center p-2.5 border border-[#1F2130] bg-[#111424] rounded text-[#7A8496] hover:text-[#F0F1F5] hover:border-val-accent/50 transition"
                title="Reset Statistics"
              >
                <RotateCcw className="w-4 h-4" />
              </button>
            </div>
            <p className="text-[10px] text-[#42495A] leading-normal font-mono">
              {manualMode
                ? 'CLICK inside the simulator box above to shoot. We analyze your deviations instantly.'
                : 'AUTOMATIC loops trace aiming error bounds. Adjust classification filters to preview.'}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
