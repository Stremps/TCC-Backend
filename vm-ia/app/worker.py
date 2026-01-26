import sys
import os
import logging
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime
import trimesh # <--- Adicione esta linha

# Imports do Core
from app.core.database import SessionLocal
from app.core.storage import storage 
from app.core.config import settings

# Imports dos Modelos
from app.models.job_model import Job, JobStatus
from app.models.artifact_model import Artifact, ArtifactType

# Configuração de Logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [Worker] - %(message)s')
logger = logging.getLogger(__name__)

# Caminho absoluto para a pasta de wrappers
BASE_DIR = Path(__file__).resolve().parents[1]
WRAPPERS_DIR = BASE_DIR / "wrappers"

def convert_obj_to_glb(input_obj_path: str, output_glb_path: str):
    """
    Converte um arquivo .obj (texto) para .glb (binário) usando trimesh.
    Essencial para visualização Web (<model-viewer>) e Unity.
    """
    logger.info(f"Iniciando conversão de formato: OBJ -> GLB")
    try:
        # Carrega o OBJ. O trimesh detecta automaticamente se é uma Cena ou uma Malha única.
        scene_or_mesh = trimesh.load(input_obj_path)
        
        # Exporta para GLB
        scene_or_mesh.export(output_glb_path, file_type='glb')
        
        # Verificação básica
        if os.path.exists(output_glb_path) and os.path.getsize(output_glb_path) > 0:
            logger.info(f"Conversão concluída: {output_glb_path}")
            return True
        else:
            logger.error("Arquivo GLB não foi criado ou está vazio.")
            return False
            
    except Exception as e:
        logger.error(f"Falha crítica na conversão OBJ->GLB: {e}")
        return False

def update_job_start(job_id: str):
    """
    Abre uma sessão curta apenas para marcar o início do Job.
    Retorna o prompt (se houver) para uso na memória, desconectando do banco logo em seguida.
    """
    with SessionLocal() as session:
        job = session.query(Job).filter(Job.id == job_id).first()
        if not job:
            return None
        
        job.status = JobStatus.PROCESSING
        job.started_at = datetime.utcnow()
        
        # Captura dados necessários antes de fechar a sessão
        job_data = {
            "prompt": job.prompt,
            "id": str(job.id)
        }
        session.commit()
        return job_data

def update_job_finish(job_id: str, status: JobStatus, artifact_path: str = None, file_size: int = 0, error_msg: str = None):
    """
    Abre uma NOVA sessão apenas para marcar o fim do Job.
    Isso evita timeouts de conexão em jobs longos (DreamFusion).
    """
    with SessionLocal() as session:
        job = session.query(Job).filter(Job.id == job_id).first()
        if not job:
            logger.error(f"Job {job_id} não encontrado para finalização.")
            return

        job.status = status
        job.completed_at = datetime.utcnow()
        
        if status == JobStatus.SUCCEEDED:
            job.progress_percent = 100
            
            # Registra o artefato se houver
            if artifact_path:
                artifact = Artifact(
                    job_id=job_id,
                    type=ArtifactType.OUTPUT_MODEL,
                    storage_path=artifact_path,
                    file_size_bytes=file_size
                )
                session.add(artifact)
        
        elif status == JobStatus.FAILED:
            # Em caso de falha, reseta progresso ou marca erro?
            # Geralmente mantemos onde parou ou zeramos, aqui salvamos a msg de erro se tivéssemos coluna
            # Como não temos coluna error_message no model atual, apenas logamos
            logger.error(f"Finalizando Job {job_id} com erro: {error_msg}")

        session.commit()
        logger.info(f"Job {job_id} finalizado com status: {status}")

def process_job(job_id: str, model_id: str, input_params: dict):
    """
    Função principal executada pelo RQ Worker.
    Refatorada para não manter conexão aberta com o banco.
    """
    logger.info(f"Iniciando processamento do Job {job_id} (Model: {model_id})")
    
    # 1. Marca Início (Sessão Curta)
    job_data = update_job_start(job_id)
    if not job_data:
        logger.error(f"Job {job_id} não encontrado no banco.")
        return

    # Cria diretório temporário para isolar este job
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            output_file_path = None
            
            # ====================================================
            # LÓGICA DO STABLE FAST 3D (Image-to-3D)
            # ====================================================
            if model_id == "sf3d-v1":
                # CORREÇÃO 1: Busca priorizada por 'input_path' (Frontend novo)
                # Fallback para 'image_path' (Legado) e erro se não achar nada.
                image_filename = input_params.get("input_path") or input_params.get("image_path")
                
                if not image_filename:
                    raise ValueError("Parâmetro 'input_path' não encontrado nos parâmetros do Job.")

                bucket_name = input_params.get("bucket", settings.MINIO_BUCKET)
                
                local_input = os.path.join(temp_dir, "input_image.png")
                local_output = os.path.join(temp_dir, "output.glb")

                logger.info(f"Baixando input '{image_filename}' do bucket '{bucket_name}'...")
                storage.download_file(bucket_name, image_filename, local_input)

                wrapper_script = WRAPPERS_DIR / "sf3d" / "run.py"
                
                cmd = [
                    sys.executable, str(wrapper_script),
                    "--input_path", local_input,
                    "--output_path", local_output,
                    "--texture_resolution", str(input_params.get("texture_resolution", 1024)),
                    "--remesh_option", str(input_params.get("remesh_option", "triangle"))
                ]

                logger.info(f"Chamando Wrapper SF3D...")
                subprocess.run(cmd, check=True)
                
                output_file_path = local_output

            # ====================================================
            # LÓGICA DO DREAMFUSION (Text-to-3D)
            # ====================================================
            elif model_id == "dreamfusion-sd":
                # Recupera o prompt da coluna segura (via job_data) ou params
                prompt = job_data.get("prompt") or input_params.get("prompt")
                
                if not prompt:
                    raise ValueError("Parâmetro 'prompt' é obrigatório para DreamFusion.")
                
                # Definimos os caminhos: O Wrapper gera OBJ, nós queremos GLB
                local_obj = os.path.join(temp_dir, "output.obj")
                local_glb = os.path.join(temp_dir, "output.glb")
                
                wrapper_script = WRAPPERS_DIR / "dreamfusion" / "run.py"
                
                cmd = [
                    sys.executable, str(wrapper_script),
                    "--prompt", prompt,
                    "--output_path", local_output,
                    "--max_steps", str(input_params.get("max_steps", 1000))
                ]

                logger.info(f"Chamando Wrapper DreamFusion...")
                # Timeout implícito pelo RQ, mas aqui deixamos o subprocess rodar
                subprocess.run(cmd, check=True)
                
                # --- NOVO PASSO: PÓS-PROCESSAMENTO (Conversão) ---
                if os.path.exists(local_obj):
                    success = convert_obj_to_glb(local_obj, local_glb)
                    if success:
                        output_file_path = local_glb # Sucesso! O arquivo final é o GLB
                    else:
                        raise RuntimeError("O arquivo OBJ foi gerado, mas a conversão para GLB falhou.")
                else:
                    raise FileNotFoundError("O Wrapper finalizou mas não gerou o arquivo output.obj.")

            else:
                raise ValueError(f"Modelo desconhecido: {model_id}")

            # ====================================================
            # UPLOAD E FINALIZAÇÃO (Sessão Nova)
            # ====================================================
            
            if output_file_path and os.path.exists(output_file_path):
                file_ext = Path(output_file_path).suffix
                remote_path = f"jobs/{job_id}/model{file_ext}"
                file_size = os.path.getsize(output_file_path)
                
                logger.info(f"Fazendo upload do resultado para {remote_path}...")
                storage.upload_file(output_file_path, settings.MINIO_BUCKET, remote_path)

                # 2. Marca Sucesso (Nova Sessão)
                update_job_finish(job_id, JobStatus.SUCCEEDED, remote_path, file_size)

            else:
                raise FileNotFoundError("O Wrapper finalizou mas não gerou o arquivo de saída esperado.")

        except subprocess.CalledProcessError as e:
            logger.error(f"Erro na execução do Wrapper CLI: {e}")
            update_job_finish(job_id, JobStatus.FAILED, error_msg="Erro interno na execução do modelo.")
            
        except Exception as e:
            logger.error(f"Erro genérico no worker: {e}", exc_info=True)
            update_job_finish(job_id, JobStatus.FAILED, error_msg=str(e))