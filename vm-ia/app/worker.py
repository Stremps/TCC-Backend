import sys
import os
import time
import json
import logging
import subprocess
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

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

def get_job_session(job_id):
    """Helper para obter sessão e job atualizados"""
    session = SessionLocal()
    try:
        job = session.query(Job).filter(Job.id == job_id).first()
        return session, job
    except Exception as e:
        session.close()
        raise e

def process_job(job_id: str, model_id: str, input_params: dict):
    """
    Função principal executada pelo RQ Worker.
    """
    logger.info(f"Iniciando processamento do Job {job_id} (Model: {model_id})")
    
    session, job = get_job_session(job_id)
    if not job:
        logger.error(f"Job {job_id} não encontrado no banco.")
        return

    # 1. Atualiza Status para PROCESSING
    job.status = JobStatus.PROCESSING
    job.started_at = datetime.utcnow()
    session.commit()

    # Cria diretório temporário para isolar este job
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            output_file_path = None
            artifact_type = ArtifactType.OUTPUT_MODEL
            
            # ====================================================
            # LÓGICA DO STABLE FAST 3D (Image-to-3D)
            # ====================================================
            if model_id == "sf3d-v1":
                image_filename = input_params.get("image_path", "teste_input.png")
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
                prompt = job.prompt or input_params.get("prompt")
                
                if not prompt:
                    # Log de erro mais detalhado para debug
                    logger.error(f"Job {job_id} falhou: Prompt vazio. Coluna DB: {job.prompt}, Params: {input_params.keys()}")
                    raise ValueError("Parâmetro 'prompt' é obrigatório para DreamFusion.")
                
                local_output = os.path.join(temp_dir, "output.obj")
                
                wrapper_script = WRAPPERS_DIR / "dreamfusion" / "run.py"
                cmd = [
                    sys.executable, str(wrapper_script),
                    "--prompt", prompt,
                    "--output_path", local_output,
                    "--max_steps", str(input_params.get("max_steps", 1000))
                ]

                logger.info(f"Chamando Wrapper DreamFusion...")
                subprocess.run(cmd, check=True)
                
                output_file_path = local_output

            else:
                raise ValueError(f"Modelo desconhecido: {model_id}")

            # ====================================================
            # UPLOAD E FINALIZAÇÃO
            # ====================================================
            
            if output_file_path and os.path.exists(output_file_path):
                file_ext = Path(output_file_path).suffix
                remote_path = f"jobs/{job_id}/model{file_ext}"
                file_size = os.path.getsize(output_file_path)
                
                logger.info(f"Fazendo upload do resultado para {remote_path}...")
                storage.upload_file(output_file_path, settings.MINIO_BUCKET, remote_path)

                # CORREÇÃO AQUI: Alinhado com artifact_model.py
                artifact = Artifact(
                    job_id=job_id,
                    type=artifact_type,
                    storage_path=remote_path,
                    file_size_bytes=file_size
                )
                session.add(artifact)
                
                job.status = JobStatus.SUCCEEDED
                job.completed_at = datetime.utcnow()
                job.progress_percent = 100
                session.commit()
                logger.info(f"Job {job_id} concluído com sucesso!")

            else:
                raise FileNotFoundError("O Wrapper finalizou mas não gerou o arquivo de saída esperado.")

        except subprocess.CalledProcessError as e:
            logger.error(f"Erro na execução do Wrapper CLI: {e}")
            job.status = JobStatus.FAILED
            job.error_message = "Erro interno na execução do modelo de IA."
            session.commit()
            
        except Exception as e:
            logger.error(f"Erro genérico no worker: {e}", exc_info=True)
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            session.commit()
            
        finally:
            session.close()