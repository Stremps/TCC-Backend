import sys
import os
import logging

# Adiciona o diretório atual ao path para garantir que conseguimos importar 'app'
sys.path.append(os.getcwd())

from redis import Redis
from rq import Worker, Queue
from rq.registry import FailedJobRegistry

# Configura Logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Tenta importar configurações
try:
    from app.core.config import settings
except ImportError as e:
    logger.error("Erro de Importação: Certifique-se de rodar este script da raiz 'vm-ia/'")
    logger.error(f"Detalhe: {e}")
    sys.exit(1)

listen = ['default']

def start_worker():
    # 1. Obtém a URL do settings (Garantia que vem do .env)
    redis_url = settings.REDIS_URL
    
    # 2. Cria a conexão Redis
    try:
        conn = Redis.from_url(redis_url)
        
        # Teste de Conexão (Prova Real)
        connection_kwargs = conn.connection_pool.connection_kwargs
        host = connection_kwargs.get('host')
        port = connection_kwargs.get('port')
        
        logger.info(f"Realizando conexão com host: {host}:{port}")
        conn.ping()
        logger.info(f"SUCESSO! Conectado ao Redis em: {host}:{port}")
        
    except Exception as e:
        logger.error(f"FALHA! ao conectar no Redis: {e}")
        sys.exit(1)

    # 3. Instancia as Filas com a Conexão Explícita (A CORREÇÃO ESTÁ AQUI)
    # Precisamos passar 'connection=conn' para CADA fila, não apenas para o Worker
    try:
        queues = [Queue(name, connection=conn) for name in listen]
        
        # 4. Inicia o Worker
        logger.info("Inicializando worker dedicado...")
        
        worker = Worker(
            queues, 
            connection=conn,
            name=f"worker-ia-{os.getpid()}" # Nome único para aparecer bonito no Dashboard
        )
        
        # Inicia o loop de processamento
        worker.work(with_scheduler=True)
        
    except Exception as e:
        logger.error(f"Erro ao iniciar o loop do Worker: {e}")
        sys.exit(1)

if __name__ == '__main__':
    start_worker()