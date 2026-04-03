"""
Modelos Pydantic y tabla ORM para el chat.
"""

from datetime import datetime

from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from src.database import Base


# ---------------------------------------------------------------------------
# Schemas de request / response (API)
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    """Cuerpo de la petición al endpoint de chat."""
    user_id: str = Field(..., description="Código único del usuario")
    message: str = Field(..., min_length=1, description="Mensaje del usuario")


class ChatResponse(BaseModel):
    """Respuesta del endpoint de chat."""
    user_id: str
    response: str
    tokens_in: int
    tokens_out: int


# ---------------------------------------------------------------------------
# Modelo interno de mensaje de conversación
# ---------------------------------------------------------------------------

class ConversationMessage(BaseModel):
    """Representa un mensaje individual dentro de una conversación."""
    role: str = Field(..., description="'user' | 'assistant' | 'system'")
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Tabla ORM — conversations
# ---------------------------------------------------------------------------

class ConversationRecord(Base):
    """Registro persistente de un mensaje de conversación en PostgreSQL."""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(128), nullable=False, index=True)
    role = Column(String(16), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
