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

    // Função única que o Dashboard vai chamar ao clicar em "Gerar"
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
                    model_id: 'dreamfusion-sd', // ID que está no ai_models.json
                    input_params: {
                        prompt: prompt,
                        max_steps: steps,
                        guidance_scale: guidance,
                        seed: seed,
                        random_bg: true 
                    }
                };

            } else {
                // --- FLUXO 2: IMAGEM (Stable Fast 3D) ---
                if (!file) throw new Error("Selecione uma imagem de referência (PNG/JPG).");

                // Passo A: Pedir permissão ao Backend (Ticket)
                // O backend retorna uma URL assinada e o caminho onde o arquivo ficará (object_name)
                const ticket = await jobsService.getUploadTicket(file.name, file.type);

                // Passo B: Enviar o arquivo binário para o MinIO (Storage)
                await jobsService.uploadFileToStorage(ticket.upload_url, file);

                // Passo C: Criar o Job apontando para o arquivo no Storage
                payload = {
                    model_id: 'sf3d-v1', // ID que está no ai_models.json
                    input_params: {
                        input_path: ticket.object_name, // Caminho interno (uploads/...)
                        texture_resolution: textureRes,
                        remesh_option: remesh,
                        foreground_ratio: 0.85 
                    }
                };
            }

            // Passo Final: Dispara o processamento
            await jobsService.createJob(payload);
            return true; // Sucesso

        } catch (err: any) {
            console.error("Erro ao submeter job:", err);
            // Tenta extrair a mensagem de erro da API ou usa uma genérica
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