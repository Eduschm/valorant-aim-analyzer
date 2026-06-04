import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Valorant palette
        val: {
          red:    '#FF4655',
          'red-dark': '#CC3542',
          'red-glow': 'rgba(255,70,85,0.15)',
          blue:   '#00D4FF',
          'blue-dark': '#0099BB',
          bg:     '#0D0E14',
          surface:'#13141C',
          'surface-2': '#1A1B26',
          border: '#1E2030',
          'border-2': '#2A2D40',
          text:   '#E8EAF0',
          muted:  '#5A6070',
          subtle: '#8892A4',
        },
      },
      fontFamily: {
        sans:    ['Inter', 'sans-serif'],
        display: ['Rajdhani', 'sans-serif'],
      },
      boxShadow: {
        'red-glow':  '0 0 24px rgba(255, 70, 85, 0.3)',
        'red-glow-sm': '0 0 12px rgba(255, 70, 85, 0.2)',
        'blue-glow': '0 0 24px rgba(0, 212, 255, 0.2)',
      },
      backgroundImage: {
        'grid-pattern': 'linear-gradient(rgba(30,32,48,0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(30,32,48,0.5) 1px, transparent 1px)',
      },
      backgroundSize: {
        'grid': '32px 32px',
      },
    },
  },
  plugins: [require('@tailwindcss/forms')],
}
export default config
