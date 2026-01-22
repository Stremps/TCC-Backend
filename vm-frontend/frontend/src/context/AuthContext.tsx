import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import { api } from '../services/api';
import type { User, LoginResponse } from '../types/auth';

interface AuthContextType {
    user: User | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    signIn: (username: string, password: string) => Promise<void>;
    signOut: () => void;
}

const AuthContext = createContext<AuthContextType>({} as AuthContextType);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    // 1. Ao iniciar, tenta recuperar a sessão
    useEffect(() => {
        const storedKey = localStorage.getItem('labcg_api_key');

        if (storedKey) {
            // Se tem chave, validamos com o backend
            api.get<User>('/users/me')
                .then(response => {
                    setUser(response.data);
                })
                .catch(() => {
                    // Se a chave for inválida (ex: revogada), limpamos tudo
                    signOut();
                })
                .finally(() => {
                    setIsLoading(false);
                });
        } else {
            setIsLoading(false);
        }
    }, []);

    // 2. Função de Login
    async function signIn(username: string, password: string) {
        try {
            // Chama a rota que criamos no backend
            const response = await api.post<LoginResponse>('/auth/login', {
                username,
                password
            });

            const { api_key, username: responseUser } = response.data;

            // Salva a chave para o Axios Interceptor usar nas próximas chamadas
            localStorage.setItem('labcg_api_key', api_key);

            // Atualiza o estado local (simulamos o objeto User inicial)
            setUser({ 
                id: 'session-init', // O ID real virá no próximo F5 ou chamada, não é crítico agora
                username: responseUser, 
                is_active: true,
                api_key: api_key 
            });

        } catch (error) {
            console.error("Erro ao logar:", error);
            throw error; // Repassa o erro para a tela de Login exibir o alerta
        }
    }

    // 3. Função de Logout
    function signOut() {
        localStorage.removeItem('labcg_api_key');
        setUser(null);
    }

    return (
        <AuthContext.Provider value={{ 
            user, 
            isAuthenticated: !!user, 
            isLoading, 
            signIn, 
            signOut 
        }}>
            {children}
        </AuthContext.Provider>
    );
}

// Hook personalizado para facilitar o uso: const { signIn } = useAuth();
export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth deve ser usado dentro de um AuthProvider');
    }
    return context;
}