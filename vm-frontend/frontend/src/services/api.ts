import axios from 'axios';

// Lê a variável do .env. Se não existir, usa o fallback.
const baseURL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

// Cria instância do axios
export const api = axios.create({
  baseURL: baseURL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// --- INTERCEPTOR DE REQUISIÇÃO ---
// Antes de qualquer chamada sair, este código roda.
api.interceptors.request.use(
  (config) => {
    // Busca a chave salva no Login (faremos isso no FRONT-01)
    const apiKey = localStorage.getItem('labcg_api_key');
    
    // Se existir, injeta no header padrão que o Backend espera
    if (apiKey) {
      config.headers['x-api-key'] = apiKey;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// --- INTERCEPTOR DE RESPOSTA (Opcional, mas recomendado) ---
// Se o token expirar ou for inválido (401/403), podemos deslogar o usuário automaticamente.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && (error.response.status === 401 || error.response.status === 403)) {
      console.warn('Sessão expirada ou inválida via Interceptor.');
      
      //Limpar storage e redirecionar para login
      localStorage.clear();
      window.location.href = '/'; 
    }
    return Promise.reject(error);
  }
);