from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Nome do projeto
    PROJECT_NAME: str = "TCC Pipeline 3D"

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

    # SF3D
    SF3D_PYTHON_PATH: str
    SF3D_SCRIPT_PATH: str

    # DreamFusion
    DREAMFUSION_PYTHON_PATH: str
    DREAMFUSION_SCRIPT_PATH: str
    DREAMFUSION_CONFIG: str = "configs/dreamfusion-sd.yaml" # Valor padrão

    # Leitura do arquivo .env
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
