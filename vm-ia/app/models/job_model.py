import uuid
import enum  # <--- Importante
from datetime import datetime
from typing import Any
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.models.base import Base

# --- DEFINIÇÃO DO ENUM (Adicionado) ---
class JobStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"

class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Chaves Estrangeiras
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    model_id: Mapped[str] = mapped_column(ForeignKey("models.id"), nullable=False)

    # Estados e Progresso
    status: Mapped[str] = mapped_column(String, default=JobStatus.QUEUED, index=True)
    progress_percent: Mapped[int] = mapped_column(Integer, default=0)
    
    # Inputs
    prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    input_params: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)

    # Timestamps do ciclo de vida
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relacionamentos
    # Strings literais evitam import circular se os outros models não estiverem carregados ainda
    user = relationship("app.models.user_model.User", back_populates="jobs")
    model = relationship("app.models.ai_model.AIModel", back_populates="jobs")
    
    # Relacionamento com tabelas filhas
    artifacts = relationship("Artifact", back_populates="job", cascade="all, delete-orphan")
    events = relationship("JobEvent", back_populates="job", cascade="all, delete-orphan")