from fastapi import APIRouter
from app.api.endpoints import jobs
from app.api.endpoints import auth

# O roteador principal que agrupa todos
api_router = APIRouter()

# Adicionamos o roteador de jobs com o prefixo "/jobs"
# Assim, todas as rotas lá dentro responderão em http://.../api/v1/jobs/...
api_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])

# Rotas de Autenticação
# Nota: prefixo vazio para /login ficar em /api/v1/login e /users/me em /api/v1/users/me
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"]) # <--- Adicionar Router
api_router.include_router(auth.router, prefix="/users", tags=["Users"]) # <--- Reutiliza para /me