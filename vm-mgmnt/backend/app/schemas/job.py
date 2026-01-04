import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# 1. JobBase: A fundação
# Tudo que é comum tanto na criação quanto na leitura fica aqui.
class JobBase(BaseModel):
    # Field(...) ajuda na documentação automática (Swagger UI)
    model_id: str = Field(..., description="ID do modelo de IA (ex: sf3d-v1, dreamfusion-sd)")
    
    # Opção 1 que escolhemos: Pode ser None se o modelo for Image-to-3D
    prompt: str | None = Field(None, description="Texto para geração (Obrigatório p/ Text-to-3D)")
    
    # Decisão de Arquitetura: JSONB vira dict[str, Any] no Python.
    # Deixamos flexível para aceitar qualquer parâmetro que o modelo novo exija.
    input_params: dict[str, Any] = Field(default_factory=dict, description="Parâmetros técnicos (steps, seed, etc)")

# 2. JobCreate: O Input
# Herda de JobBase. Neste caso, não adicionamos nada extra, 
# mas poderíamos adicionar campos como 'callback_url' no futuro.
class JobCreate(JobBase):
    pass

# 3. JobRead: O Output
# Herda de JobBase e ADICIONA o que o Banco de Dados gerou.
class JobRead(JobBase):
    id: uuid.UUID
    status: str
    progress_percent: int
    created_at: datetime
    
    # Campos opcionais de tempo (podem ser nulos se o job acabou de ser criado)
    started_at: datetime | None = None
    completed_at: datetime | None = None

    # CONFIGURAÇÃO CRÍTICA (Pydantic V2)
    # Isso diz: "Pydantic, aceite ler dados não só de dicionários, 
    # mas também de Objetos do SQLAlchemy (ORM)".
    # Sem isso, ele grita erro ao tentar converter a linha do banco para JSON.
    model_config = ConfigDict(from_attributes=True)