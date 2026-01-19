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
                logger.error(f"Falha crítica ao criar bucket: {e}")
                raise e

    def upload_file(self, file_path: str, object_name: str) -> str:
        """
        Faz o upload de um arquivo local para o MinIO.
        (Utilizado principalmente pelo Worker ou seeds internas)
        
        Args:
            file_path: Caminho do arquivo no disco local (ex: /tmp/cubo.glb)
            object_name: Nome que o arquivo terá no MinIO (ex: jobs/123/cubo.glb)
            
        Returns:
            O object_name em caso de sucesso.
        """
        try:
            self.s3_client.upload_file(file_path, self.bucket_name, object_name)
            logger.info(f"Upload realizado com sucesso: {object_name}")
            return object_name
        except ClientError as e:
            logger.error(f"Erro ao fazer upload para o MinIO: {e}")
            raise e

    def generate_presigned_url(self, object_name: str, expiration: int = 3600) -> str:
        """
        Gera uma URL temporária para download direto do MinIO.
        
        Args:
            object_name: O caminho do arquivo no bucket (ex: jobs/123/output.glb)
            expiration: Tempo de vida do link em segundos (Padrão: 1 hora)
            
        Returns:
            A URL completa e assinada.
        """

        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': object_name
                },
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.error(f"Erro ao gerar URL de download assinada: {e}")
            return ""

    def generate_presigned_upload_url(self, object_name: str, content_type: str, expiration: int = 300) -> str:
        """
        Gera uma URL temporária para UPLOAD (PUT) direto para o MinIO.
        O Frontend usará esta URL para enviar o arquivo binário.

        Args:
            object_name: Caminho final do arquivo (ex: uploads/inputs/uuid.png)
            content_type: Tipo MIME do arquivo (ex: image/png). Importante para validar no MinIO.
            expiration: Tempo de validade do ticket em segundos (Default: 5 min)
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': object_name,
                    'ContentType': content_type
                },
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.error(f"Erro ao gerar URL de upload assinada: {e}")
            return ""

# Instância Singleton:
# Ao importar 'storage' em outros arquivos, usaremos sempre esta mesma conexão
storage = StorageClient()