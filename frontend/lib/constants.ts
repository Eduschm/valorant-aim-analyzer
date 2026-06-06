// Design system colors and constants
export const COLORS = {
  primary: '#4361EE',
  primaryDark: '#3046C0',
  secondary: '#0F1923',
  accent: '#69C9D0',
  textPrimary: '#ECE8E1',
  textSecondary: '#8B9BB4',
  surface: '#1F2731',
  surfaceHover: '#2A3542',
}

// API endpoints
export const API_ENDPOINTS = {
  AUTH: {
    SIGNIN: '/api/auth/signin',
    CALLBACK: '/api/auth/callback',
    LINK_RIOT_ID: '/api/auth/link-riot-id',
    SESSION: '/api/auth/session',
  },
  ANALYSIS: {
    TRACKER: '/api/analysis/tracker',
    GET: '/api/analysis/:id',
    HISTORY: '/api/analysis/history',
    CLIP: '/api/analysis/clip',
    VIDEO_URL: '/api/analysis/:id/video-url',
    FRAMES: '/api/analysis/:id/frames',
    ENGAGEMENTS: '/api/analysis/:id/engagements',
  },
  USER: {
    PROFILE: '/api/user/profile',
    UPDATE: '/api/user/profile',
  },
  UPLOAD: {
    PRESIGNED_URL: '/api/upload/presigned-url',
  },
}

// Polling configuration
export const POLLING = {
  INTERVAL: 2000, // 2 seconds
  MAX_ATTEMPTS: 120, // 4 minutes max
}

// Analysis status
export const ANALYSIS_STATUS = {
  PENDING: 'pending',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  FAILED: 'failed',
}

// Weapoon names (from Valorant)
export const WEAPONS = {
  VANDAL: 'Vandal',
  PHANTOM: 'Phantom',
  OPERATOR: 'Operator',
  JUDGE: 'Judge',
  CLASSIC: 'Classic',
  SHORTY: 'Shorty',
  FRENZY: 'Frenzy',
  GHOST: 'Ghost',
  SHERIFF: 'Sheriff',
}

// Agent names
export const AGENTS = {
  JETT: 'Jett',
  PHOENIX: 'Phoenix',
  SAGE: 'Sage',
  SOVA: 'Sova',
  VIPER: 'Viper',
  CYPHER: 'Cypher',
  REYNA: 'Reyna',
  KILLJOY: 'Killjoy',
  BREACH: 'Breach',
  RAZE: 'Raze',
  SKYE: 'Skye',
  YORU: 'Yoru',
  ASTRA: 'Astra',
  KAY_O: 'KAY/O',
  CHAMBER: 'Chamber',
  NEON: 'Neon',
  FADE: 'Fade',
  HARBOR: 'Harbor',
  GEKKO: 'Gekko',
  ISO: 'Iso',
}

// Maps
export const MAPS = {
  ASCENT: 'Ascent',
  BIND: 'Bind',
  HAVEN: 'Haven',
  SPLIT: 'Split',
  ICEBOX: 'Icebox',
  LOTUS: 'Lotus',
  PEARL: 'Pearl',
}

// Ranks
export const RANKS = [
  'Unranked',
  'Iron',
  'Bronze',
  'Silver',
  'Gold',
  'Platinum',
  'Diamond',
  'Ascendant',
  'Immortal',
  'Radiant',
]

// Error messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your connection.',
  VALIDATION_ERROR: 'Please fill in all required fields correctly.',
  UNAUTHORIZED: 'Please sign in to continue.',
  NOT_FOUND: 'Resource not found.',
  SERVER_ERROR: 'Server error. Please try again later.',
  INVALID_RIOT_ID: 'Invalid Riot ID format. Use PlayerName#1234',
}

// Success messages
export const SUCCESS_MESSAGES = {
  ANALYSIS_STARTED: 'Analysis started. Analyzing your matches...',
  RIOT_ID_LINKED: 'Riot ID linked successfully!',
  PROFILE_UPDATED: 'Profile updated successfully!',
}

// Free tier limits
export const FREE_TIER = {
  CLIPS_PER_MONTH: 10,
  MAX_CLIP_DURATION_SECONDS: 180, // 3 minutes
  MAX_CLIP_SIZE_MB: 500,
}

// Paid tier limits
export const PAID_TIER = {
  CLIPS_PER_MONTH: 40,
  MAX_CLIP_DURATION_SECONDS: 600, // 10 minutes (unlimited in UI)
  MAX_CLIP_SIZE_MB: 2000,
}

// Video formats
export const SUPPORTED_VIDEO_FORMATS = [
  'video/mp4',
  'video/webm',
  'video/quicktime',
  'video/x-msvideo',
]

// Local storage keys
export const STORAGE_KEYS = {
  AUTH_TOKEN: 'auth_token',
  USER: 'user',
  RECENT_ANALYSIS: 'recent_analysis',
  UI_PREFERENCES: 'ui_preferences',
}

// Timeouts (ms)
export const TIMEOUTS = {
  API_REQUEST: 30000,
  POLLING: 120000,
}

// Page titles and descriptions
export const PAGE_META = {
  HOME: {
    title: 'Valorant Aim Analyzer',
    description: 'AI-powered aim analysis for Valorant players',
  },
  DASHBOARD: {
    title: 'Dashboard - Valorant Aim Analyzer',
    description: 'Track your aim improvement over time',
  },
  ANALYSIS: {
    title: 'Analysis Report - Valorant Aim Analyzer',
    description: 'Your detailed aim analysis and coaching insights',
  },
}
