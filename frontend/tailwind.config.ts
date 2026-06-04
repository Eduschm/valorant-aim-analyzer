import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#fff5f5',
          100: '#fed7d7',
          200: '#fc8c8c',
          300: '#f6747d',
          400: '#ff4655', // Valorant red
          500: '#ff4655',
          600: '#e64149',
          700: '#c4323e',
          800: '#a22c35',
          900: '#7a1f26',
        },
        secondary: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          500: '#8b9bb4',
          700: '#475569',
          900: '#0f1923', // Dark background
        },
        accent: {
          50: '#f0fdfd',
          100: '#d4faf8',
          400: '#69c9d0', // Cyan
          500: '#00b8c4',
          600: '#00a0ad',
        },
        surface: {
          50: '#f8fafc',
          100: '#f1f5f9',
          500: '#1f2731',
          600: '#1a1f27',
          700: '#0f1923',
        },
      },
      fontFamily: {
        heading: ['Inter', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      boxShadow: {
        glow: '0 0 20px rgba(255, 70, 85, 0.1)',
        'glow-accent': '0 0 20px rgba(105, 201, 208, 0.1)',
      },
    },
  },
  plugins: [require('@tailwindcss/forms')],
}
export default config
