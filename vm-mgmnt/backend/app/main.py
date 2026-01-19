from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.api import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0"
)

# --- Configuração de CORS (Cross-Origin Resource Sharing) ---
# Permite que o Frontend (localhost:3000, etc) converse com este Backend
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        # Converte os objetos Pydantic Url/String para string pura
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True, # Permite Cookies e Headers de Autenticação
        allow_methods=["*"],    # Permite GET, POST, PUT, DELETE, OPTIONS, etc.
        allow_headers=["*"],    # Permite todos os headers (Authorization, Content-Type, etc.)
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