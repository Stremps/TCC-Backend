from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import db_session, CurrentUser
from app.core.security import verify_password
from app.models.user_model import User
from app.schemas.user import LoginRequest, LoginResponse, UserRead

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: LoginRequest,
    session: db_session # <--- Use diretamente o tipo anotado
):
    """
    Recebe username e password.
    Se válido, devolve a API Key do utilizador.
    """
    # 1. Buscar utilizador no banco
    stmt = select(User).where(User.username == form_data.username)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    # 2. Verificar se existe e se a senha bate
    if not user:
        # Segurança: Mensagem genérica para evitar enumeração de utilizadores
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )
    
    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Utilizador inativo"
        )

    # 3. Sucesso: Devolve a chave
    return LoginResponse(
        api_key=user.api_key,
        username=user.username,
        message="Login realizado com sucesso"
    )

@router.get("/me", response_model=UserRead)
def read_current_user(current_user: CurrentUser):
    """
    Valida a API Key enviada no Header e devolve os dados do utilizador.
    Usado pelo Frontend para persistir a sessão ao recarregar a página.
    """
    return current_user