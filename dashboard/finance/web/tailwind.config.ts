import type { Config } from 'tailwindcss'

export default {
  content: [
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        bg: '#0f172a',
        surface: '#1e293b',
        'surface-hover': '#334155',
        border: '#334155',
        accent: '#3b82f6',
        'accent-light': '#60a5fa',
        positive: '#22c55e',
        negative: '#ef4444',
        muted: '#94a3b8',
        ink: '#f1f5f9',
      },
    },
  },
  plugins: [],
} satisfies Config
