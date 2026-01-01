import asyncio
import json
import logging
from pathlib import Path

from passlib.context import CryptContext
from sqlalchemy import select

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.user_model import User
from app.models.ai_model import AIModel

# Configuração de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Contexto de Criptografia
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def seed_users(session):
    """
    Cria ou atualiza o Super Usuário definido no .env
    """
    username = settings.FIRST_SUPERUSER_USERNAME
    # Importante: Hashear a senha antes de salvar/comparar
    password_hash = pwd_context.hash(settings.FIRST_SUPERUSER_PASSWORD)
    api_key = settings.FIRST_SUPERUSER_API_KEY

    logger.info(f"> Verificando Super Usuário: {username}")

    # Busca usuário existente
    result = await session.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if not user:
        logger.info("-> Usuário não encontrado. Criando novo...")
        user = User(
            username=username,
            password_hash=password_hash,
            api_key=api_key,
            is_active=True
        )
        session.add(user)
    else:
        logger.info("-> Usuário existe. Atualizando credenciais (Senha/Key) para garantir consistência...")
        user.password_hash = password_hash
        user.api_key = api_key
        # O SQLAlchemy detecta a mudança e fará o UPDATE no commit
        session.add(user)

async def seed_models(session):
    """
    Lê o arquivo JSON e sincroniza com o banco de dados.
    """
    # Caminho absoluto para o arquivo JSON (baseado na localização deste script)
    # Assume que o script está em app/initial_data.py e o json em app/db/seeds/ai_models.json
    json_path = Path(__file__).parent / "db" / "seeds" / "ai_models.json"
    
    if not json_path.exists():
        logger.error(f"Arquivo de seed não encontrado: {json_path}")
        return

    logger.info(f"Lendo definições de modelos em: {json_path.name}")
    
    with open(json_path, "r", encoding="utf-8") as f:
        models_data = json.load(f)

    for data in models_data:
        model_id = data["id"]
        logger.info(f"> Processando modelo: {model_id}")

        result = await session.execute(select(AIModel).where(AIModel.id == model_id))
        model = result.scalar_one_or_none()

        if not model:
            logger.info("-> Novo modelo detectado. Inserindo...")
            model = AIModel(
                id=model_id,
                name=data["name"],
                description=data.get("description"),
                default_params=data["default_params"],
                is_active=data.get("is_active", True)
            )
            session.add(model)
        else:
            logger.info("-> Modelo já existe. Atualizando parâmetros e definições...")
            # Atualiza campos que podem ter mudado no JSON
            model.name = data["name"]
            model.description = data.get("description")
            model.default_params = data["default_params"]
            model.is_active = data.get("is_active", True)
            session.add(model)

async def main():
    logger.info("Iniciando Seed (Idempotente)...")
    
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # O bloco 'async with session.begin()' garante que:
            # Tudo roda numa transação. Se der erro, faz Rollback. Se der certo, faz Commit no final.
            await seed_users(session)
            await seed_models(session)
            
    logger.info("Seed concluído com sucesso!")

if __name__ == "__main__":
    asyncio.run(main())