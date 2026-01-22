import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export function PrivateRoute() {
    const { isAuthenticated, isLoading } = useAuth();

    // Enquanto verifica o localStorage, mostra nada ou um spinner simples
    if (isLoading) {
        return <div className="min-h-screen bg-gunmetal flex items-center justify-center">
            <i className="fa-solid fa-circle-notch fa-spin text-primary text-2xl"></i>
        </div>;
    }

    // Se não estiver logado, manda para o Login
    return isAuthenticated ? <Outlet /> : <Navigate to="/" replace />;
}