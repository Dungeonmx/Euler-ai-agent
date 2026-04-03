"""
Router de documentos — endpoint para subir documentos al sistema RAG.
"""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models.document import DocumentUploadResponse
from src.services.rag_service import RAGService

router = APIRouter(prefix="/documents", tags=["Documentos"])


@router.post(
    "",
    response_model=DocumentUploadResponse,
    summary="Subir documento para RAG",
    description="Sube un archivo de texto (.txt) para que sea procesado, "
    "dividido en chunks y almacenado con embeddings vectoriales para "
    "alimentar el contexto del agente.",
)
async def upload_document(
    file: UploadFile = File(..., description="Archivo de texto a procesar"),
    db: AsyncSession = Depends(get_db),
) -> DocumentUploadResponse:
    """Procesa un archivo: chunking → embeddings → almacenamiento."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="El archivo debe tener un nombre.")

    # Leer contenido
    raw = await file.read()
    try:
        content = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="El archivo debe estar en formato de texto UTF-8.",
        )

    if not content.strip():
        raise HTTPException(status_code=400, detail="El archivo está vacío.")

    service = RAGService(db)
    return await service.ingest_document(file.filename, content)
