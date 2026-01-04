import uuid
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.models.ai_model import AIModel
from app.models.job_model import Job
from app.schemas.job import JobCreate, JobRead
from app.api.deps import CurrentUser, db_session  # Importamos nossas dependências

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
    
    # Atualiza o objeto com o ID e Created_at gerados pelo banco
    await session.refresh(new_job)

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