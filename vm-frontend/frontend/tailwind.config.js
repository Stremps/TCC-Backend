/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        gunmetal: '#18242c',
        surface: '#22303a',
        primary: '#40cf9f',
        primaryHover: '#34b086',
        textMain: '#ffffff',
        textSec: '#94a3b8',
        danger: '#ef4444',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      // Aqui criamos a grade "Blueprint" usando gradientes CSS
      backgroundImage: {
        'blueprint': `linear-gradient(to right, #2a3b47 1px, transparent 1px),
                      linear-gradient(to bottom, #2a3b47 1px, transparent 1px)`,
      },
      backgroundSize: {
        'blueprint-size': '40px 40px', // Tamanho dos quadrados da grade
      },
      // Sombra Neon Suave (menos estourada que a padrão)
      boxShadow: {
        'neon-soft': '0 0 20px -5px rgba(64, 207, 159, 0.15)',
        'neon-card': '0 0 40px -10px rgba(0, 0, 0, 0.5)',
      },
      animation: {
        'shake': 'shake 0.5s cubic-bezier(.36,.07,.19,.97) both',
        'float-slow': 'float 8s ease-in-out infinite',
      },
      keyframes: {
        shake: {
          '0%, 100%': { transform: 'translateX(0)' },
          '10%, 30%, 50%, 70%, 90%': { transform: 'translateX(-4px)' },
          '20%, 40%, 60%, 80%': { transform: 'translateX(4px)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-15px)' },
        }
      }
    },
  },
  plugins: [],
}