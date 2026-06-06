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
          // Brand accent — driven by CSS vars in globals.css :root
          accent:        'rgb(var(--accent) / <alpha-value>)',
          'accent-dark': 'rgb(var(--accent-hover) / <alpha-value>)',
          'accent-mid':  'rgb(var(--accent-mid) / <alpha-value>)',
          // Semantic danger (losses / errors) — stays red
          danger:        'rgb(var(--danger) / <alpha-value>)',
          // Backward-compat aliases: any leftover val-red* class renders blue
          red:        'rgb(var(--accent) / <alpha-value>)',
          'red-dark': 'rgb(var(--accent-hover) / <alpha-value>)',
          'red-glow': 'rgb(var(--accent) / 0.12)',
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
        'accent-glow':    '0 0 24px rgb(var(--accent) / 0.25)',
        'accent-glow-sm': '0 0 12px rgb(var(--accent) / 0.15)',
        // Aliases so existing shadow-red-glow* classes stay valid (now blue)
        'red-glow':    '0 0 24px rgb(var(--accent) / 0.25)',
        'red-glow-sm': '0 0 12px rgb(var(--accent) / 0.15)',
      },
      animation: {
        'spin-slow': 'spin 2s linear infinite',
      },
    },
  },
  plugins: [require('@tailwindcss/forms')],
}
export default config
