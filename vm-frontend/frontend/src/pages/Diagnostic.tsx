import { useEffect, useState } from 'react';
import { api } from '../services/api';

interface HealthResponse {
  status: string;
  env: string;
}

export function Diagnostic() {
  const [status, setStatus] = useState<'loading' | 'online' | 'offline'>('loading');
  const [data, setData] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    checkConnection();
  }, []);

  async function checkConnection() {
    setStatus('loading');
    try {
      // Tenta bater no endpoint /health do Backend
      const response = await api.get<HealthResponse>('/health');
      setData(response.data);
      setStatus('online');
    } catch (err: any) {
      console.error(err);
      setStatus('offline');
      setError(err.message || 'Erro desconhecido');
    }
  }

  return (
    <div className="min-h-screen bg-gunmetal flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-md bg-surface p-8 rounded-xl shadow-2xl border border-white/5">
        <h1 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
          <i className="fa-solid fa-stethoscope text-primary"></i> Diagnóstico de Rede
        </h1>

        {/* Status Indicator */}
        <div className={`p-4 rounded-lg mb-6 border ${
          status === 'online' ? 'bg-green-500/10 border-green-500/30' : 
          status === 'offline' ? 'bg-danger/10 border-danger/30' : 
          'bg-white/5 border-white/10'
        }`}>
          <div className="flex items-center justify-between">
            <span className="text-textSec font-medium">Status da API</span>
            {status === 'loading' && <span className="text-primary animate-pulse">Conectando...</span>}
            {status === 'online' && <span className="text-green-500 font-bold flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-green-500"></div> ONLINE</span>}
            {status === 'offline' && <span className="text-danger font-bold flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-danger"></div> OFFLINE</span>}
          </div>
        </div>

        {/* Detalhes Técnicos */}
        {status === 'online' && data && (
          <div className="space-y-3 text-sm">
            <div className="flex justify-between border-b border-white/5 pb-2">
              <span className="text-textSec">Projeto Backend:</span>
              <span className="text-white font-mono">{data.env}</span>
            </div>
            <div className="flex justify-between border-b border-white/5 pb-2">
              <span className="text-textSec">Health Check:</span>
              <span className="text-white font-mono">{data.status}</span>
            </div>
            <div className="flex justify-between pt-2">
              <span className="text-textSec">Base URL (Frontend):</span>
              <span className="text-white font-mono text-xs truncate max-w-[150px]">
                {import.meta.env.VITE_API_BASE_URL}
              </span>
            </div>
          </div>
        )}

        {/* Erro */}
        {status === 'offline' && (
          <div className="text-center">
            <p className="text-danger text-sm mb-4">{error}</p>
            <p className="text-textSec text-xs">
              Verifique se o backend está rodando na porta 8000.
            </p>
          </div>
        )}

        {/* Botão Retry */}
        <button 
          onClick={checkConnection}
          className="w-full mt-6 bg-surface hover:bg-white/5 border border-white/10 text-white py-2 rounded-lg transition-colors"
        >
          Testar Novamente
        </button>
        
        <div className="mt-4 text-center">
           <a href="/" className="text-primary text-sm hover:underline">Voltar para Login</a>
        </div>
      </div>
    </div>
  );
}