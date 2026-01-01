from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Nome do projeto
    PROJECT_NAME: str = "TCC Pipeline 3D"

    # Conexão com banco de dados
    DATABASE_URL: str

    # Primeiro usuário
    FIRST_SUPERUSER_USERNAME: str
    FIRST_SUPERUSER_PASSWORD: str
    FIRST_SUPERUSER_API_KEY: str

    # Leitura do arquivo .env
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()