/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          dark: "#0b132b",
          navy: "#1c2541",
          steel: "#3a506b",
          cyan: "#5bc0be",
          mint: "#6fffe9",
        },
        risk: {
          low: "#10b981",       // Healthy green
          medium: "#f59e0b",    // Warning yellow/amber
          high: "#ef4444",      // High-risk blight red
          extreme: "#7f1d1d",   // Severe disease dark red
        },
      },
    },
  },
  plugins: [],
};
