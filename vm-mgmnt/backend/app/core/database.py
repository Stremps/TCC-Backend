from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# 1. Criação da Engine Assíncrona
# O echo=True vai mostrar o SQL no terminal
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True, 
)

# 2. Fábrica de Sessões
# Configura como as sessões de banco serão criadas (sem expirar no commit, classe Async)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

# 3. Base para os Modelos (ORM)
# Todas as nossas tabelas (Jobs, Users) vão herdar dessa classe depois
Base = declarative_base()

# 4. Dependência para Injeção
# O FastAPI vai usar isso para entregar uma sessão de banco para cada rota
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            # Garante que a conexão fecha mesmo se der erro na rota
            await session.close()

# === NOVA PARTE SÍNCRONA (Para o Worker/RQ) ===
# Precisamos ajustar a URL pois o 'postgresql+asyncpg' não funciona no driver sync.
# O replace abaixo troca para 'postgresql://' padrão ou usamos a string direta se soubermos.
# Geralmente o sync aceita apenas 'postgresql://user:pass@...'
SYNC_DATABASE_URL = settings.DATABASE_URL.replace("postgresql+asyncpg", "postgresql")

sync_engine = create_engine(SYNC_DATABASE_URL, echo=True)

# Fábrica de Sessões Síncrona
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)