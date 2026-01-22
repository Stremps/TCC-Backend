import { useState, type FormEvent, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  
  const { signIn, isLoading, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) navigate('/dashboard');
  }, [isAuthenticated, navigate]);

  async function handleLogin(e: FormEvent) {
    e.preventDefault();
    // Limpa erros anteriores ao tentar novamente
    setError(false);
    setErrorMessage('');

    if (!username || !password) {
      setErrorMessage('Preencha todos os campos.');
      setError(true);
      // Aqui removemos o 'shake' depois de 500ms, mas a mensagem fica
      setTimeout(() => setError(false), 500);
      return;
    }

    try {
      await signIn(username, password);
      // Não precisa redirecionar aqui, o useEffect já faz isso
    } catch (err) {
      // Define a mensagem para o usuário ler
      setErrorMessage('Usuário ou senha inválidos.');
      // Ativa a animação
      setError(true);
      // Desativa APENAS a animação (o shake) depois de 500ms
      // A mensagem de erro continua visível até ele tentar de novo
      setTimeout(() => setError(false), 500);
    }
  }

  return (
    <div className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden bg-gunmetal">
      
      {/* --- BACKGROUND EFEITOS --- */}
      
      {/* 1. Grade Blueprint (Via Tailwind config) */}
      <div className="absolute inset-0 z-0 bg-blueprint bg-blueprint-size opacity-20 pointer-events-none"></div>
      
      {/* 2. Orbs (Bolas Coloridas) - Mais coladas nas bordas */}
      <div className="absolute top-[-10%] left-[-10%] w-96 h-96 bg-primary/10 rounded-full blur-[100px]"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-96 h-96 bg-blue-500/10 rounded-full blur-[100px]"></div>


      {/* --- CONTEÚDO PRINCIPAL (z-10) --- */}
      <div className="z-10 flex w-full max-w-md flex-col gap-8 p-8 animate-float-slow">
        
        {/* HEADER (Fora do Cartão) */}
        <div className="text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl border border-primary/20 bg-surface/50 shadow-neon-soft backdrop-blur-sm">
            <i className="fa-solid fa-cube text-3xl text-primary"></i>
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-white">
            Lab<span className="text-primary">CGera</span>
          </h1>
          <p className="mt-2 text-sm text-textSec">
            Plataforma de IA Generativa 3D
          </p>
        </div>

        {/* CARTÃO (Somente Login/Senha) */}
        <div className="bg-surface/50 backdrop-blur-md border border-white/10 rounded-2xl py-5 px-8 shadow-2xl">
          <form onSubmit={handleLogin} className="space-y-6">
            
            {/* Usuário */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold uppercase tracking-wider text-textSec ml-1">
                Usuário
              </label>
              {/* Ajuste 2: Adicionado 'group' aqui para controlar o ícone via foco do input */}
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                  {/* Ícone muda de cor quando o grupo recebe foco */}
                  <i className="fa-regular fa-user text-textSec/50 transition-colors duration-300 group-focus-within:text-primary"></i>
                </div>
                <input 
                  type="text" 
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full rounded-lg bg-gunmetal border border-white/10 py-3 pl-10 pr-4 text-sm text-white placeholder-textSec/20 focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary transition-all"
                  placeholder="Usuário acadêmico"
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold uppercase tracking-wider text-textSec ml-1">
                Senha
              </label>
              {/* Ajuste 2: Adicionado 'group' aqui também */}
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                  {/* Ajuste 3: Lógica corrigida para o ícone não sumir no erro */}
                  {/* Se erro: Vermelho. Se normal: Cinza -> Verde no Foco */}
                  <i className={`fa-solid fa-lock transition-colors duration-300 ${
                    error 
                      ? 'text-danger' 
                      : 'text-textSec/50 group-focus-within:text-primary'
                  }`}></i>
                </div>
                <input 
                  type="password" 
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className={`w-full rounded-lg bg-gunmetal border py-3 pl-10 pr-4 text-sm text-white placeholder-textSec/20 focus:outline-none transition-all ${
                    error 
                      ? 'border-danger ring-1 ring-danger animate-shake placeholder-danger/50' 
                      : 'border-white/10 focus:border-primary focus:ring-1 focus:ring-primary'
                  }`}
                  placeholder="••••••••"
                />
              </div>
            </div>

            {/* Erro */}
            {errorMessage && (
              <div className="flex items-center justify-center gap-2 rounded-lg bg-danger/10 py-2 text-xs font-medium text-danger">
                <i className="fa-solid fa-circle-exclamation"></i>
                {errorMessage}
              </div>
            )}

            {/* Botão */}
            <button 
              type="submit" 
              disabled={isLoading}
              className={`w-full rounded-lg py-2.5 text-sm font-semibold transition-all duration-300 ${
                isLoading 
                  ? 'cursor-not-allowed bg-surface border border-white/5 text-textSec' 
                  : 'bg-primary text-gunmetal shadow-neon-soft hover:bg-primaryHover hover:shadow-lg'
              }`}
            >
              {isLoading ? (
                <span><i className="fa-solid fa-circle-notch fa-spin mr-2"></i></span>
              ) : (
                "Acessar Sistema"
              )}
            </button>
          </form>
        </div>

        {/* FOOTER (Fora do Cartão) */}
        <div className="text-center">
          <p className="text-center text-xs text-textSec opacity-60">
            &copy; 2026 Laboratório de Computação Gráfica.<br/>Acesso restrito a pesquisadores autorizados.
        </p>
        </div>

      </div>
    </div>
  );
}