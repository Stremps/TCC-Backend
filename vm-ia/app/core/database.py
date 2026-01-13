from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from app.core.config import settings

# === NOVA PARTE SÍNCRONA (Para o Worker/RQ) ===
# Precisamos ajustar a URL pois o 'postgresql+asyncpg' não funciona no driver sync.
# O replace abaixo troca para 'postgresql://' padrão ou usamos a string direta se soubermos.
# Geralmente o sync aceita apenas 'postgresql://user:pass@...'
SYNC_DATABASE_URL = settings.DATABASE_URL.replace("postgresql+asyncpg", "postgresql")

sync_engine = create_engine(SYNC_DATABASE_URL, echo=True)
# Fábrica de Sessões Síncrona
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
Base = declarative_base()