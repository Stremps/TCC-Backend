from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
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