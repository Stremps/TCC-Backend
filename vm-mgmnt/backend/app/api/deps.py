from typing import Annotated
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import APIKeyHeader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user_model import User

# Define que o token deve vir no header com o nome "x-api-key"
# O auto_error=False permite que a gente trate o erro manualmente se quiser
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

async def get_current_user(
    api_key: str = Security(api_key_header),
    session: AsyncSession = Depends(get_db)
) -> User:
    """
    Busca o usuário associado à API Key fornecida no Header.
    Se não encontrar ou a chave for inválida, lança erro.
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key ausente no header 'x-api-key'"
        )

    # Query direta no banco: SELECT * FROM users WHERE api_key = ...
    # Note que aqui a lógica é dinâmica: funciona para admin ou qualquer usuário futuro
    query = select(User).where(User.api_key == api_key)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key inválida ou usuário inativo"
        )
    
    return user

# Atalho de tipagem para usar nas rotas
CurrentUser = Annotated[User, Depends(get_current_user)]
db_session = Annotated[AsyncSession, Depends(get_db)]