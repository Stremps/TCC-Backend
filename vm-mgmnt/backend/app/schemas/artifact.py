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
    expires_in: int    # Tempo em segundos

# --- schemas para Upload (PUT - Ticket de Entrada) ---
class ArtifactUploadRequest(BaseModel):
    """
    O cliente avisa: 'Vou subir um arquivo com este nome e tipo'
    """
    filename: str       # Ex: "minha_textura.png"
    content_type: str   # Ex: "image/png" (Crucial para validação no MinIO)

class ArtifactUploadResponse(BaseModel):
    """
    A API responde: 'Use esta URL e guarde este caminho'
    """
    upload_url: str     # URL assinada para o Frontend fazer PUT direto
    object_name: str    # O caminho final gerado (ex: uploads/inputs/uuid.png). 
                        # IMPORTANTE: O Frontend deve enviar este valor ao criar o Job!
    expires_in: int