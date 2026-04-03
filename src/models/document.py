"""
Modelos Pydantic y tabla ORM para documentos y embeddings (RAG).
"""

from pydantic import BaseModel, Field
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from src.database import Base


# ---------------------------------------------------------------------------
# Schemas de API
# ---------------------------------------------------------------------------

class DocumentUploadResponse(BaseModel):
    """Respuesta tras subir un documento para ser procesado."""
    document_id: str
    filename: str
    chunks_count: int
    status: str = "processed"


# ---------------------------------------------------------------------------
# Tabla ORM — document_chunks
# ---------------------------------------------------------------------------

EMBEDDING_DIM = 768  # Dimensión del modelo nomic-embed-text-v2-moe


class DocumentChunkRecord(Base):
    """Trozo de documento almacenado con su embedding vectorial."""
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String(128), nullable=False, index=True)
    filename = Column(String(256), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(EMBEDDING_DIM), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
