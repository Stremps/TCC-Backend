from pydantic import BaseModel
from uuid import UUID

# O que o Frontend envia para logar
class LoginRequest(BaseModel):
    username: str
    password: str

# O que o Backend devolve após logar (inclui a API Key)
class LoginResponse(BaseModel):
    api_key: str
    username: str
    message: str

# O que o Backend devolve na rota /me (sem dados sensíveis)
class UserRead(BaseModel):
    id: UUID
    username: str
    is_active: bool

    class Config:
        from_attributes = True # Antigo orm_mode