import time
import logging
import os
from uuid import UUID

from app.core.database import SessionLocal
from app.models.job_model import Job
from app.models.artifact_model import Artifact  
from app.core.storage import storage            

# Configuração de Logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Funções de Banco (Síncronas) ---

def update_job_status(job_id_str: str, status: str):
    """Atualiza o status do Job no banco."""
    session = SessionLocal()
    try:
        job_uuid = UUID(job_id_str)
        job = session.get(Job, job_uuid)
        if job:
            job.status = status
            session.add(job)
            session.commit()
            logger.info(f"Job {job_id_str} atualizado para {status}")
        else:
            logger.error(f"Job {job_id_str} não encontrado!")
    except Exception as e:
        logger.error(f"Erro ao atualizar status: {e}")
        session.rollback()
    finally:
        session.close()

def save_artifact(job_id_str: str, storage_path: str, file_size: int):
    """
    Cria o registro na tabela 'artifacts' apontando para o arquivo no MinIO.
    Isso é crucial para que a API saiba onde está o download depois.
    """
    session = SessionLocal()
    try:
        job_uuid = UUID(job_id_str)
        
        artifact = Artifact(
            job_id=job_uuid,
            type="OUTPUT_MODEL",  # Tipo fixo para o modelo 3D final
            storage_path=storage_path,
            file_size_bytes=file_size
        )
        
        session.add(artifact)
        session.commit()
        logger.info(f"Artefato registrado no banco: {storage_path}")
    except Exception as e:
        logger.error(f"Erro ao salvar artefato: {e}")
        session.rollback()
        # Nota: Em produção, talvez devêssemos apagar o arquivo do S3 se falhar aqui
    finally:
        session.close()

# --- Lógica Principal ---

def process_job(job_id: str, model_id: str, input_params: dict):
    """
    Função executada pelo Worker (RQ).
    Simula a geração de IA e faz upload do resultado.
    """
    logger.info(f"> Iniciando Job: {job_id}")
    
    # Nome do arquivo local temporário e caminho remoto
    local_filename = f"{job_id}_temp.glb"
    remote_path = f"jobs/{job_id}/output.glb" # Padrão: jobs/{uuid}/output.glb

    try:
        # 1. Muda status para RUNNING
        update_job_status(job_id, "RUNNING")

        # 2. Simulação da IA (Fake Generation)
        logger.info("> Gerando modelo 3D (Fake)...")
        time.sleep(5) 
        
        # Cria um arquivo local "fake"
        with open(local_filename, "w") as f:
            f.write(f"Conteudo 3D Fake do Job {job_id}")
        
        # Pega o tamanho para salvar no banco
        file_size = os.path.getsize(local_filename)

        # 3. Upload para o MinIO (Storage)
        logger.info(f"> Fazendo upload para: {remote_path}")
        storage.upload_file(local_filename, remote_path)

        # 4. Salva referência no Banco (Artifacts)
        save_artifact(job_id, remote_path, file_size)

        # 5. Sucesso
        update_job_status(job_id, "SUCCEEDED")
        logger.info("> Job finalizado com sucesso!")

    except Exception as e:
        logger.error(f"> Falha no Job {job_id}: {e}")
        update_job_status(job_id, "FAILED")
        # Relança para o RQ contar como falha
        raise e
        
    finally:
        # 6. Limpeza (Sempre apaga o arquivo local, dando certo ou errado)
        if os.path.exists(local_filename):
            os.remove(local_filename)
            logger.info("> Arquivo temporário removido.")