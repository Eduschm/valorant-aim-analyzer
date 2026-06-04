import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        val: {
          bg:           '#0A0B0F',
          surface:      '#111318',
          'surface-2':  '#181A22',
          border:       '#1F2130',
          'border-2':   '#2A2D40',
          red:          '#FF4655',
          'red-dark':   '#CC3542',
          'red-glow':   'rgba(255,70,85,0.12)',
          text:         '#F0F1F5',
          subtle:       '#7A8496',
          muted:        '#42495A',
          green:        '#22C55E',
          'green-dim':  'rgba(34,197,94,0.12)',
          orange:       '#F97316',
          'orange-dim': 'rgba(249,115,22,0.12)',
        },
      },
      fontFamily: {
        sans:    ['Inter', 'sans-serif'],
        display: ['Rajdhani', 'sans-serif'],
      },
      boxShadow: {
        'red-glow':    '0 0 24px rgba(255, 70, 85, 0.25)',
        'red-glow-sm': '0 0 12px rgba(255, 70, 85, 0.15)',
      },
      animation: {
        'spin-slow': 'spin 2s linear infinite',
      },
    },
  },
  plugins: [require('@tailwindcss/forms')],
}
export default config
