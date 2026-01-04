from fastapi import APIRouter
from app.api.endpoints import jobs

# O roteador principal que agrupa todos
api_router = APIRouter()

# Adicionamos o roteador de jobs com o prefixo "/jobs"
# Assim, todas as rotas lá dentro responderão em http://.../api/v1/jobs/...
api_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])