/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'weather-dark': '#0a0f1b',
        'weather-panel': '#1a2332',
        'weather-accent': '#4facfe',
        'weather-accent-2': '#00f2fe',
      }
    },
  },
  plugins: [require("daisyui")],
  daisyui: {
    themes: [
      {
        weather: {
          "primary": "#4facfe",
          "secondary": "#00f2fe",
          "accent": "#37cdbe",
          "neutral": "#1a2332",
          "base-100": "#0a0f1b",
          "base-200": "#1a2332",
          "base-300": "#2a3f5f",
          "info": "#3abff8",
          "success": "#2ecc71",
          "warning": "#f1c40f",
          "error": "#e74c3c",
        },
      },
    ],
  },
}
