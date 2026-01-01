import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# 1. Importar as configurações e os Modelos do projeto
from app.core.config import settings
from app.models import Base

# Configuração de Log do Alembic
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 2. Definir os metadados (Para o autogenerate funcionar)
target_metadata = Base.metadata

# 3. Sobrescrever a URL do alembic.ini com a do nosso .env
# Isso garante que ele use a senha correta sem hardcode
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


def run_migrations_offline() -> None:
    """Executa migrações no modo 'offline'.
    Isso gera apenas o script SQL sem conectar no banco.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Executa migrações no modo 'online'.
    Cria uma Engine Async e conecta no banco de verdade.
    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())