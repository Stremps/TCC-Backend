import { useState } from 'react';
import { jobsService, type JobCreate } from '../services/jobs';

interface SubmitProps {
    mode: 'TEXT' | 'IMAGE';
    // Dados Text (DreamFusion)
    prompt: string;
    steps: number;
    guidance: number;
    seed: number;
    // Dados Image (SF3D)
    file: File | null;
    textureRes: number;
    remesh: string;
}

export function useJobSubmit() {
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    async function submit({ 
        mode, prompt, steps, guidance, seed, 
        file, textureRes, remesh 
    }: SubmitProps): Promise<boolean> {
        
        setIsSubmitting(true);
        setError(null);

        try {
            let payload: JobCreate;

            if (mode === 'TEXT') {
                // --- FLUXO 1: TEXTO (DreamFusion) ---
                if (!prompt.trim()) throw new Error("Por favor, descreva o objeto no prompt.");

                payload = {
                    model_id: 'dreamfusion-sd',
                    // CORREÇÃO: Prompt enviado no nível raiz (Coluna dedicada no Banco)
                    prompt: prompt, 
                    
                    // CORREÇÃO: Apenas parâmetros técnicos ficam no JSONB
                    input_params: {
                        max_steps: steps,
                        guidance_scale: guidance,
                        seed: seed,
                        random_bg: true 
                    }
                };

            } else {
                // --- FLUXO 2: IMAGEM (Stable Fast 3D) ---
                if (!file) throw new Error("Selecione uma imagem de referência (PNG/JPG).");

                // Passo A: Ticket de Upload
                const ticket = await jobsService.getUploadTicket(file.name, file.type);

                // Passo B: Upload Binário Direto (MinIO)
                await jobsService.uploadFileToStorage(ticket.upload_url, file);

                // Passo C: Criação do Job
                payload = {
                    model_id: 'sf3d-v1',
                    // Prompt omitido (ou null) pois é Image-to-3D
                    input_params: {
                        input_path: ticket.object_name, // Caminho no Storage
                        texture_resolution: textureRes,
                        remesh_option: remesh,
                        foreground_ratio: 0.85 
                    }
                };
            }

            // Envio final para API
            await jobsService.createJob(payload);
            return true;

        } catch (err: any) {
            console.error("Erro ao submeter job:", err);
            const msg = err.response?.data?.detail || err.message || "Falha ao iniciar a geração.";
            setError(msg);
            return false;
        } finally {
            setIsSubmitting(false);
        }
    }

    return {
        submit,
        isSubmitting,
        error
    };
}