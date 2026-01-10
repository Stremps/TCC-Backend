import time
import logging
from uuid import UUID

# Importamos a nova sessão síncrona
from app.core.database import SessionLocal 
from app.models.job_model import Job

# --- Configuração de Logs ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Funções de Banco (Síncronas e Robustas) ---
def update_job_status(job_id_str: str, status: str):
    """
    Atualiza o status do Job de forma síncrona.
    Abre e fecha a conexão a cada chamada para garantir atomicidade no Worker.
    """
    session = SessionLocal() # Abre conexão
    try:
        job_uuid = UUID(job_id_str)
        # session.get é o método padrão do SQLAlchemy
        job = session.get(Job, job_uuid)
        
        if job:
            job.status = status
            session.add(job)
            session.commit()
            logger.info(f"Job {job_id_str} atualizado para {status}")
        else:
            logger.error(f"Job {job_id_str} não encontrado no banco!")
            
    except Exception as e:
        logger.error(f"Erro de banco ao atualizar job: {e}")
        session.rollback()
    finally:
        session.close() # Fecha conexão (Crucial no Worker)

# --- A Lógica Principal ---
def process_job(job_id: str, model_id: str, input_params: dict):
    """
    Função principal executada pelo Worker (RQ).
    """
    logger.info(f"> Iniciando processamento do Job: {job_id} (Modelo: {model_id})")

    try:
        # 1. Marca como RUNNING
        update_job_status(job_id, "RUNNING")

        # 2. Simula o processamento pesado da IA
        logger.info("> IA Pensando... (Simulando processamento de 5s)")
        time.sleep(5) 

        # 3. Marca como SUCCEEDED
        update_job_status(job_id, "SUCCEEDED")
        logger.info(f"> Job {job_id} concluído com sucesso!")

    except Exception as e:
        logger.error(f"> Erro ao processar job {job_id}: {e}")
        # Em caso de erro, importante marcar como FAILED
        update_job_status(job_id, "FAILED")
        raise e