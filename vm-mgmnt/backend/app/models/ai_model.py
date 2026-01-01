from datetime import datetime
from typing import Any
from sqlalchemy import String, Boolean, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.models.base import Base

class AIModel(Base):
    __tablename__ = "models"  # Nome da tabela no banco (conforme MER)

    id: Mapped[str] = mapped_column(String, primary_key=True)  # Ex: "sf3d-v1"
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # JSONB permite flexibilidade total de parâmetros por modelo
    default_params: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    # Relacionamento com Jobs
    jobs = relationship("Job", back_populates="model")