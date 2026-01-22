import { defineConfig, loadEnv } from 'vite' // <--- Adicione loadEnv
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Carrega variáveis de ambiente (necessário para ler o que o Docker manda)
  const env = loadEnv(mode, process.cwd(), '');
  
  // Define o alvo: Se o Docker mandar um alvo, usa ele. Se não, usa localhost.
  const apiTarget = env.VITE_API_TARGET || 'http://192.168.1.180:8000';

  return {
    plugins: [react()],
    server: {
      port: 3000,
      host: true, // Necessário para Docker
      proxy: {
        '/api': {
          target: apiTarget, // <--- Usa a variável dinâmica
          changeOrigin: true,
          secure: false,
        }
      }
    }
  }
})