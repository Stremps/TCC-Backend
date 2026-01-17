import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base

# --- DEFINIÇÃO DO ENUM (Adicionado) ---
class ArtifactType(str, enum.Enum):
    INPUT = "INPUT"           # Imagem ou Texto de entrada
    MODEL_3D = "MODEL_3D"     # O arquivo .glb ou .obj final
    PREVIEW = "PREVIEW"       # Thumbnail ou render
    LOG = "LOG"               # Arquivos de log de erro

class Artifact(Base):
    __tablename__ = "artifacts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("jobs.id"), nullable=False, index=True)
    
    # Armazena como string no banco, mas usamos o Enum no código
    type: Mapped[str] = mapped_column(String, nullable=False) 
    storage_path: Mapped[str] = mapped_column(String, nullable=False)
    file_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    job = relationship("app.models.job_model.Job", back_populates="artifacts")