const LEVELS = {
  debug: 10,
  info: 20,
  warn: 30,
  error: 40,
}

type Level = keyof typeof LEVELS

const defaultLevel = process.env.NEXT_PUBLIC_LOG_LEVEL?.toLowerCase() as Level | undefined
const activeLevel = LEVELS[defaultLevel ?? (process.env.NODE_ENV === 'production' ? 'info' : 'debug')] ?? LEVELS.debug

function shouldLog(level: Level): boolean {
  return LEVELS[level] >= activeLevel
}

function formatMessage(level: Level, args: unknown[]) {
  return [`[frontend:${level}]`, ...args]
}

export const logger = {
  debug: (...args: unknown[]) => { if (shouldLog('debug')) console.debug(...formatMessage('debug', args)) },
  info:  (...args: unknown[]) => { if (shouldLog('info'))  console.info(...formatMessage('info', args)) },
  warn:  (...args: unknown[]) => { if (shouldLog('warn'))  console.warn(...formatMessage('warn', args)) },
  error: (...args: unknown[]) => { if (shouldLog('error')) console.error(...formatMessage('error', args)) },
}
