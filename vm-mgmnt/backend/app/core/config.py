from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "TCC Pipeline 3D"
    
    # Validação automática: Se não tiver no .env, o app não sobe
    DATABASE_URL: str

    # Configuração para ler o arquivo .env
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()