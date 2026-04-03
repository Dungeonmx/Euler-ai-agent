"""
Servicio RAG — ingesta de documentos, chunking, generación de embeddings
y recuperación por similitud.
"""

import uuid

from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.models.document import DocumentUploadResponse
from src.repositories.document_repo import DocumentRepository


# ---------------------------------------------------------------------------
# Cliente de embeddings
# ---------------------------------------------------------------------------

def create_embeddings_client() -> OpenAIEmbeddings:
    """Crea cliente de embeddings apuntando al segundo servidor llama.cpp."""
    return OpenAIEmbeddings(
        base_url=settings.embeddings_base_url,
        api_key=settings.embeddings_api_key,
        model=settings.embeddings_model,
    )


# ---------------------------------------------------------------------------
# Servicio
# ---------------------------------------------------------------------------

class RAGService:
    """Ingesta de documentos y recuperación de contexto relevante."""

    def __init__(self, session: AsyncSession) -> None:
        self._repo = DocumentRepository(session)
        self._embeddings = create_embeddings_client()
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.rag_chunk_size,
            chunk_overlap=settings.rag_chunk_overlap,
        )

    async def ingest_document(
        self,
        filename: str,
        content: str,
    ) -> DocumentUploadResponse:
        """Procesa un documento: lo divide en chunks, genera embeddings y
        almacena todo en la base de datos.

        Args:
            filename: Nombre original del archivo.
            content: Contenido textual del documento.

        Returns:
            Respuesta con información del procesamiento.
        """
        document_id = str(uuid.uuid4())

        # 1. Dividir en chunks
        chunks = self._splitter.split_text(content)

        # 2. Generar embeddings
        embeddings = await self._embeddings.aembed_documents(chunks)

        # 3. Persistir en DB
        chunks_count = await self._repo.save_chunks(
            document_id=document_id,
            filename=filename,
            chunks=chunks,
            embeddings=embeddings,
        )

        return DocumentUploadResponse(
            document_id=document_id,
            filename=filename,
            chunks_count=chunks_count,
        )

    async def retrieve(self, query: str, top_k: int | None = None) -> list[str]:
        """Busca los chunks más relevantes para una consulta.

        Args:
            query: Texto de la consulta del usuario.
            top_k: Cantidad de resultados (usa config por defecto).

        Returns:
            Lista con el contenido de los chunks más similares.
        """
        k = top_k or settings.rag_top_k
        query_embedding = await self._embeddings.aembed_query(query)
        return await self._repo.search_similar(query_embedding, k)
