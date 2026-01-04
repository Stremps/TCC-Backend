from fastapi import FastAPI
from app.core.config import settings
from app.api.api import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0"
)

# Incluímos todas as rotas da API com o prefixo /api/v1
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "API TCC Pipeline 3D está online!"}

@app.get("/health")
def health_check():
    """
    Rota simples para verificar se a API está de pé.
    Futuramente pode verificar conexão com Redis/Banco.
    """
    return {"status": "ok", "env": settings.PROJECT_NAME}