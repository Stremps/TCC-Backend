import os
import boto3
import logging
from botocore.exceptions import ClientError
from app.core.config import settings

logger = logging.getLogger(__name__)

class StorageClient:
    def __init__(self):
        """
        Construtor: Configura a conexão com o MinIO assim que a classe é instanciada.
        """
        self.bucket_name = settings.MINIO_BUCKET
        
        # Inicializa o cliente boto3 com as configs do nosso .env
        # Mantendo o nome original 's3_client'
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=settings.MINIO_ENDPOINT,
            aws_access_key_id=settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_SECRET_KEY,
            use_ssl=settings.MINIO_SECURE,
        )
        
        # Verificação de segurança (apenas para Dev):
        # Garante que o bucket existe antes de começarmos a trabalhar.
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        try:
            # Tenta ler os metadados do bucket para ver se ele existe
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError:
            # Se der erro (404), tentamos criar
            logger.warning(f"Bucket '{self.bucket_name}' não encontrado. Criando...")
            try:
                self.s3_client.create_bucket(Bucket=self.bucket_name)
                logger.info(f"Bucket '{self.bucket_name}' criado com sucesso.")
            except Exception as e:
                logger.error(f"Erro crítico ao criar bucket: {e}")
                raise e

    def upload_file(self, file_path: str, bucket: str, object_name: str = None) -> bool:
        """
        Faz upload de um arquivo local para o MinIO.
        
        Args:
            file_path: Caminho local do arquivo.
            bucket: Nome do bucket de destino.
            object_name: Nome do objeto no bucket (se None, usa o nome do arquivo).
        """
        if object_name is None:
            object_name = os.path.basename(file_path)

        try:
            # Correção: Usando self.s3_client (consistente com __init__)
            self.s3_client.upload_file(file_path, bucket, object_name)
            logger.info(f"Upload realizado com sucesso: {file_path} -> {bucket}/{object_name}")
            return True
        except Exception as e:
            logger.error(f"Erro no upload para o MinIO: {e}")
            raise e

    def download_file(self, bucket: str, object_name: str, file_path: str) -> bool:
        """
        Baixa um arquivo do MinIO para o disco local.
        
        Args:
            bucket: Nome do bucket de origem.
            object_name: Nome do objeto no MinIO.
            file_path: Caminho local onde salvar o arquivo.
        """
        try:
            # Correção: Assinatura corrigida para receber bucket, object_name e file_path
            self.s3_client.download_file(bucket, object_name, file_path)
            logger.info(f"Download realizado com sucesso: {object_name} -> {file_path}")
            return True
        except Exception as e:
            logger.error(f"Erro ao baixar arquivo do MinIO: {e}")
            raise e

# Instância Singleton:
# Ao importar 'storage' em outros arquivos, usaremos sempre esta mesma conexão
storage = StorageClient()