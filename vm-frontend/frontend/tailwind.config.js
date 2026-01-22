/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Paleta LabCG (Extraída do login.html)
        gunmetal: '#18242c', // Background principal
        surface: '#22303a',  // Cartões e Sidebar
        primary: '#40cf9f',  // Verde Destaque (Ações)
        primaryHover: '#34b086',
        textMain: '#ffffff',
        textSec: '#94a3b8',   // Slate-400
        danger: '#ef4444',
        success: '#22c55e',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        }
      }
    },
  },
  plugins: [],
}