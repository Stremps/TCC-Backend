import uuid
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.models.ai_model import AIModel
from app.models.artifact_model import Artifact
from app.models.job_model import Job
from app.schemas.job import JobCreate, JobRead
from app.api.deps import CurrentUser, db_session
from app.core.queue import job_queue
from app.core.storage import storage
from app.worker import process_job

router = APIRouter()

@router.post("/", response_model=JobRead, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_in: JobCreate,       # O JSON que o Unity mandou (validado pelo Pydantic)
    current_user: CurrentUser, # O Usuário dono da chave (validado pelo deps.py)
    session: db_session,     # A conexão com o banco
):
    """
    Cria um novo Job de geração 3D.
    Valida se o modelo existe e associa ao usuário autenticado.
    """
    
    # 1. Validação de Negócio: O modelo de IA existe?
    # Não podemos criar um job para "modelo-fantasma"
    stmt = select(AIModel).where(AIModel.id == job_in.model_id)
    result = await session.execute(stmt)
    ai_model = result.scalar_one_or_none()

    if not ai_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Modelo de IA '{job_in.model_id}' não encontrado."
        )

    # 2. Criação do Objeto Job
    # Note que injetamos o user_id do usuário autenticado aqui
    new_job = Job(
        user_id=current_user.id,
        model_id=job_in.model_id,
        prompt=job_in.prompt,
        input_params=job_in.input_params,
        status="QUEUED"  # Estado inicial obrigatório
    )

    # 3. Persistência
    session.add(new_job)
    await session.commit()
    await session.refresh(new_job) # Atualiza o objeto com o ID e Created_at gerados pelo banco

    # 4. Envio para a Fila
    # "app.worker.process_job" é o nome da função que criaremos no Card 2.
    job_queue.enqueue(     # Passamos apenas dados simples (strings/dicts), nunca objetos do Banco.
        process_job,
        str(new_job.id),      # Converta UUID para string
        new_job.model_id,
        new_job.input_params
    )

    return new_job

@router.get("/{job_id}", response_model=JobRead)
async def get_job_status(
    job_id: uuid.UUID,           # 1. Validação automática de formato UUID
    current_user: CurrentUser,   # 2. Garante que quem chama está autenticado
    session: db_session,         # 3. Injeção do banco de dados
):
    """
    Busca os detalhes de um Job pelo ID.
    Segurança: Apenas o dono do Job pode visualizá-lo.
    """
    
    # Busca pela Chave Primária (Primary Key)
    # session.get é o jeito mais moderno e otimizado do SQLAlchemy 2.0
    job = await session.get(Job, job_id)

    # Verificação 1: Existência
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job não encontrado"
        )

    # Verificação 2: Propriedade (Authorization)
    # Se o usuário logado (current_user.id) for diferente do dono do job (job.user_id)
    if job.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para acessar este job"
        )

    return job

@router.get("/{job_id}/download", status_code=status.HTTP_200_OK)
async def download_job_artifact(
    job_id: uuid.UUID,
    current_user: CurrentUser,
    session: db_session,
):
    """
    Gera uma URL temporária (Presigned URL) para baixar o resultado final.
    A API não faz o download, apenas autoriza e redireciona.
    """
    
    # 1. Busca o Job
    job = await session.get(Job, job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job não encontrado")

    # 2. Segurança: Apenas o dono pode baixar
    if job.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado")

    # 3. Validação de Estado
    if job.status != "SUCCEEDED":
        raise HTTPException(
            status_code=400, 
            detail=f"O Job ainda não foi finalizado. Status atual: {job.status}"
        )

    # 4. Busca o Artefato no Banco
    # Precisamos achar onde o arquivo está guardado (caminho no MinIO)
    stmt = select(Artifact).where(
        Artifact.job_id == job_id,
        Artifact.type == "OUTPUT_MODEL" # Buscamos especificamente o modelo 3D
    )
    result = await session.execute(stmt)
    artifact = result.scalar_one_or_none()

    if not artifact:
        raise HTTPException(
            status_code=404, 
            detail="Artefato não encontrado. O processamento pode ter falhado silenciosamente."
        )

    # 5. Gera o Ticket VIP (Presigned URL)
    # Validade: 1 hora (3600 segundos)
    presigned_url = storage.generate_presigned_url(artifact.storage_path, expiration=600)

    if not presigned_url:
        raise HTTPException(status_code=500, detail="Erro ao gerar link de download")

    # Retorna o link para o cliente (Unity/Front) baixar
    return {"download_url": presigned_url, "expires_in": 600}