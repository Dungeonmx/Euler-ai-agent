"""
Modelos Pydantic y tabla ORM para logs de consumo de tokens.
"""

from datetime import datetime

from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from src.database import Base


# ---------------------------------------------------------------------------
# Schema Pydantic
# ---------------------------------------------------------------------------

class TokenLogEntry(BaseModel):
    """Entrada de log de tokens."""
    user_id: str
    tokens_in: int
    tokens_out: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Tabla ORM — token_logs
# ---------------------------------------------------------------------------

class TokenLogRecord(Base):
    """Registro persistente de consumo de tokens por interacción."""
    __tablename__ = "token_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(128), nullable=False, index=True)
    tokens_in = Column(Integer, nullable=False)
    tokens_out = Column(Integer, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
