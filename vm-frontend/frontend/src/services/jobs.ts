import axios from 'axios';
import { api } from './api';

// --- Interfaces (Contratos de Dados) ---

// Payload para criar um novo Job
export interface JobCreate {
    model_id: string;
    input_params: Record<string, any>;
    prompt?: string; // Opcional no envio, dependendo do modelo
}

// Resposta do Backend ao criar Job
export interface JobRead {
    id: string;
    model_id: string;
    status: 'QUEUED' | 'PROCESSING' | 'SUCCEEDED' | 'FAILED';
    progress_percent: number;
    created_at: string; // ISO String
    started_at?: string | null;
    completed_at?: string | null;
    prompt: string | null; // Pode ser null no SF3D
    input_params: Record<string, any>; // Dicionário flexível
}

// Resposta do Endpoint de Ticket de Upload
export interface ArtifactUploadResponse {
    upload_url: string; // URL Assinada do MinIO (PUT)
    object_name: string; // Caminho interno (uploads/inputs/...) para salvar no banco
}

interface ArtifactDownload {
    download_url: string;
    expires_in: number;
}

// --- Service Layer ---

export const jobsService = {
    /**
     * Passo 1 do Upload: Pede permissão ao Backend.
     * Retorna uma URL assinada temporária para fazer o PUT direto no Storage.
     */
    getUploadTicket: async (filename: string, contentType: string) => {
        const response = await api.post<ArtifactUploadResponse>('/jobs/upload-ticket', {
            filename,
            content_type: contentType
        });
        return response.data;
    },

    /**
     * Passo 2 do Upload: Envia o arquivo binário para o MinIO.
     * NOTA: Usamos axios puro para NÃO enviar o header 'x-api-key', 
     * pois o MinIO rejeitaria a requisição assinada.
     */
    uploadFileToStorage: async (presignedUrl: string, file: File) => {
        await axios.put(presignedUrl, file, {
            headers: {
                'Content-Type': file.type
            },
            // Monitoramento de progresso de upload (útil para barras de progresso futuras)
            onUploadProgress: (progressEvent) => {
                const percentCompleted = Math.round((progressEvent.loaded * 100) / (progressEvent.total || 1));
                console.log(`Upload MinIO: ${percentCompleted}%`);
            }
        });
    },

    /**
     * Passo 3 (Final): Cria o Job de fato no banco de dados.
     */
    createJob: async (data: JobCreate) => {
        const response = await api.post<JobRead>('/jobs', data);
        return response.data;
    },

    /**
     * Lista os jobs do usuário (paginado).
     */
    listJobs: async () => {
        // Por enquanto pegamos os 50 últimos. Futuramente podemos passar params.
        const response = await api.get<JobRead[]>('/jobs?limit=50');
        return response.data;
    },

    /**
     * Obtém a URL assinada para baixar o GLB final.
     */
    getDownloadUrl: async (jobId: string) => {
        const response = await api.get<ArtifactDownload>(`/jobs/${jobId}/download`);
        return response.data.download_url;
    }
};