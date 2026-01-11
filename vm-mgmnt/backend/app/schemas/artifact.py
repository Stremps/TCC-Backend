from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

# --- Schemas de Base (Atributos comuns) ---
class ArtifactBase(BaseModel):
    type: str
    file_size_bytes: int | None = None

# --- Schema para Leitura do Banco (Quando listarmos artefatos) ---
class ArtifactRead(ArtifactBase):
    id: UUID
    job_id: UUID
    storage_path: str  # Caminho interno (ex: jobs/123/output.glb)
    created_at: datetime

    class Config:
        from_attributes = True

# --- Schema para o Endpoint de Download (O Ticket VIP) ---
class ArtifactDownload(BaseModel):
    download_url: str  # A URL assinada gigante
    expires_in: int    # Tempo em segundos2