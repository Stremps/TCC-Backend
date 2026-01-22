export interface User {
    id: string;
    username: string;
    is_active: boolean;
    api_key?: string; // Opcional, pois /me não retorna a key por segurança, mas o login sim
}

export interface LoginResponse {
    api_key: string;
    username: string;
    message: string;
}