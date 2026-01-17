import redis
from rq import Queue
from app.core.config import settings

# Criamos uma conexão, que só conecta quando usar
redis_conn = redis.from_url(settings.REDIS_URL) # Usamos a URL definida no .env

# Criamos a fila padrão do sistema
# É para esta fila que enviaremos os jobs de geração 3D
job_queue = Queue("default", connection=redis_conn, default_timeout=5400)

def get_queue() -> Queue:
    """
    Retorna a instância da fila para ser usada nos endpoints.
    Padrão Singleton implícito (o módulo Python cacheia a instância).
    """
    return job_queue