"""
Repositorio de documentos — almacenamiento de chunks con embeddings y búsqueda
por similitud vectorial usando pgvector.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.document import DocumentChunkRecord


class DocumentRepository:
    """Acceso a la tabla `document_chunks` para RAG."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save_chunks(
        self,
        document_id: str,
        filename: str,
        chunks: list[str],
        embeddings: list[list[float]],
    ) -> int:
        """Persiste los chunks de un documento con sus embeddings.

        Args:
            document_id: Identificador único del documento.
            filename: Nombre original del archivo.
            chunks: Lista de textos (trozos del documento).
            embeddings: Lista de vectores correspondientes a cada chunk.

        Returns:
            Cantidad de chunks almacenados.
        """
        records = [
            DocumentChunkRecord(
                document_id=document_id,
                filename=filename,
                chunk_index=i,
                content=chunk,
                embedding=embedding,
            )
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))
        ]
        self._session.add_all(records)
        await self._session.commit()
        return len(records)

    async def search_similar(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> list[str]:
        """Busca los chunks más similares al embedding dado usando distancia coseno.

        Args:
            query_embedding: Vector de la consulta.
            top_k: Cantidad de resultados a retornar.

        Returns:
            Lista con el contenido de los chunks más relevantes.
        """
        stmt = (
            select(DocumentChunkRecord.content)
            .order_by(DocumentChunkRecord.embedding.cosine_distance(query_embedding))
            .limit(top_k)
        )
        result = await self._session.execute(stmt)
        return [row[0] for row in result.fetchall()]
