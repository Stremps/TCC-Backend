from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Nome do projeto
    PROJECT_NAME: str = "TCC Pipeline 3D"

    # --- CORS (Segurança de Acesso) ---
    # Lista de URLs permitidas. Ex no .env: BACKEND_CORS_ORIGINS="http://localhost:3000,http://localhost:8080"
    BACKEND_CORS_ORIGINS: list[str] | str = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        """
        Validador que transforma a string do .env em uma lista de strings.
        Aceita: "http://a.com,http://b.com" -> ["http://a.com", "http://b.com"]
        """
        # Se vier uma string (do .env), separamos por vírgula
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        # Se já vier lista ou for JSON válido, retorna direto
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Conexão com banco de dados
    DATABASE_URL: str

    # Conexão com storage (MinIO)
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET: str
    MINIO_SECURE: bool = False # Default False para dev

    # Conexão com a Fila
    REDIS_URL: str

    # Primeiro usuário
    FIRST_SUPERUSER_USERNAME: str
    FIRST_SUPERUSER_PASSWORD: str
    FIRST_SUPERUSER_API_KEY: str

    # Leitura do arquivo .env
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()