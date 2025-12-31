from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0"
)

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