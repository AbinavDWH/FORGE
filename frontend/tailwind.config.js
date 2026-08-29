/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        forge: {
          bg: '#FFFFFF',
          fg: '#0A0A0A',
          muted: '#737373',
          subtle: '#A3A3A3',
          border: '#E5E5E5',
          soft: '#FAFAFA',
          accent: '#E11D48',  // Swiss Red
          danger: '#E11D48',
        }
      },
      fontFamily: {
        sans: ['ui-sans-serif', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'Inter', 'sans-serif'],
        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
      },
      letterSpacing: {
        tightest: '-0.04em',
        tighter: '-0.02em',
        wide: '0.08em',
        wider: '0.12em',
      },
    },
  },
  plugins: [],
}