import uuid
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from typing import List

from app.models.ai_model import AIModel
from app.models.artifact_model import Artifact, ArtifactType
from app.models.job_model import Job, JobStatus
from app.schemas.artifact import ArtifactDownload, ArtifactUploadRequest, ArtifactUploadResponse
from app.schemas.job import JobCreate, JobRead
from app.api.deps import CurrentUser, db_session
from app.core.queue import job_queue
from app.core.storage import storage

router = APIRouter()

@router.post("/upload-ticket", response_model=ArtifactUploadResponse)
async def generate_upload_ticket(
    ticket_in: ArtifactUploadRequest,
    current_user: CurrentUser, # Segurança: Apenas logados podem subir arquivos
):
    """
    Gera uma URL assinada (Ticket) para o Frontend subir arquivos diretamente para o MinIO.
    Fluxo:
    1. Frontend pede permissão enviando nome e tipo do arquivo.
    2. API gera um caminho único e uma URL assinada (PUT).
    3. Frontend usa a URL para enviar o arquivo.
    4. Frontend cria o Job enviando o 'object_name' retornado aqui.
    """
    
    # 1. Gerar um identificador único para evitar colisão de nomes
    # Estrutura: uploads/inputs/{uuid}-{filename_original}
    file_uuid = uuid.uuid4()
    sanitized_filename = ticket_in.filename.replace(" ", "_") # Limpeza básica
    object_name = f"uploads/inputs/{file_uuid}-{sanitized_filename}"

    # 2. Gerar a URL assinada no Storage
    # Validade de 300 segundos (5 minutos) é suficiente para iniciar o upload
    expiration = 300 
    upload_url = storage.generate_presigned_upload_url(
        object_name=object_name,
        content_type=ticket_in.content_type,
        expiration=expiration
    )

    if not upload_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Falha ao gerar ticket de upload no Storage."
        )

    return ArtifactUploadResponse(
        upload_url=upload_url,
        object_name=object_name,
        expires_in=expiration
    )

@router.post("/", response_model=JobRead, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_in: JobCreate,       # O JSON que o Unity mandou (validado pelo Pydantic)
    current_user: CurrentUser, # O Usuário dono da chave (validado pelo deps.py)
    session: db_session,     # A conexão com o banco
):
    """
    Cria um novo Job de geração 3D.
    Valida se o modelo existe, associa ao usuário autenticado e e registra seus artefatos de entrada.
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

    # 2. TRATAMENTO DE DADOS (Sanitização), caso input esteja em parametros 
    # Trabalhamos numa cópia para não alterar o objeto de entrada original
    clean_params = job_in.input_params.copy()
    
    # Define o valor inicial do prompt vindo do payload (pode ser None no payload)
    final_prompt = job_in.prompt

    # Se o prompt veio "escondido" dentro dos parâmetros técnicos (comum em frontends antigos),
    # nós o resgatamos e limpamos o dicionário.
    if "prompt" in clean_params:
        # Se o prompt principal estava vazio, usamos o que estava no dict
        if not final_prompt:
            final_prompt = clean_params["prompt"]
        
        # REMOVE do dict para evitar duplicação no banco (SSOT - Single Source of Truth)
        del clean_params["prompt"]
    
    # 3. Criação do Objeto Job
    # Note que injetamos o user_id do usuário autenticado aqui
    new_job = Job(
        user_id=current_user.id,
        model_id=job_in.model_id,
        status=JobStatus.QUEUED,
        prompt=final_prompt,      # <--- Vai para a coluna TEXT (Indexável e buscável)
        input_params=clean_params # <--- Vai para a coluna JSONB (Apenas configs técnicas)
    )

    session.add(new_job)
    # Flush para garantir que new_job.id esteja disponível para uso no artefato
    await session.flush() 

    # 4. Registro do Artefato de Entrada (Se houver)
    # Se o job tem um input de imagem (vindo do upload-ticket), registramos agora na tabela Artifacts.
    # Isso garante rastreabilidade total: Job -> Artifact(INPUT) -> MinIO
    input_image_path = job_in.input_params.get("image_path")

    if input_image_path:
        # Cria o registro do artefato linkado ao Job
        input_artifact = Artifact(
            job_id=new_job.id,                 
            type=ArtifactType.INPUT,           # Classificação correta via Enum
            storage_path=input_image_path,     # Caminho no MinIO
            file_size_bytes=None               # O Frontend não mandou o tamanho, fica None por enquanto
        )
        session.add(input_artifact)

    # 4. Commit Atômico (Job + Artifact são salvos juntos)
    await session.commit()
    await session.refresh(new_job)

    # 5. Enfileiramento no Redis
    # Timeout de 1h30min (5400s) para suportar modelos pesados como DreamFusion
    job_queue.enqueue(     # Passamos apenas dados simples (strings/dicts), nunca objetos do Banco.
        "app.worker.process_job",
        str(new_job.id),      # Converta UUID para string
        new_job.model_id,
        new_job.input_params,
        job_timeout=5400
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

@router.get("/{job_id}/download", response_model=ArtifactDownload)
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
    return ArtifactDownload(
        download_url=presigned_url,
        expires_in=600
    )

@router.get("/", response_model=List[JobRead])
async def list_jobs(
    current_user: CurrentUser,
    session: db_session,
    skip: int = 0,
    limit: int = 50  # Default seguro para não travar o front
):
    """
    Lista todos os jobs do usuário logado.
    Ordenados do mais recente para o mais antigo.
    """
    stmt = (
        select(Job)
        .where(Job.user_id == current_user.id)
        .order_by(Job.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    
    result = await session.execute(stmt)
    jobs = result.scalars().all()
    
    return jobs