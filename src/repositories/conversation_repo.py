"""
Repositorio de conversaciones — persistencia y recuperación de historial.
"""

from datetime import datetime

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.chat import ConversationRecord


class ConversationRepository:
    """Acceso a la tabla `conversations` para persistir/recuperar historiales."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save_messages(
        self,
        user_id: str,
        messages: list[dict[str, str]],
    ) -> None:
        """Persiste una lista de mensajes de historial en la base de datos.

        Args:
            user_id: Identificador único del usuario.
            messages: Lista de dicts con keys ``role`` y ``content``.
        """
        records = [
            ConversationRecord(
                user_id=user_id,
                role=msg["role"],
                content=msg["content"],
                timestamp=msg.get("timestamp", datetime.utcnow()),
            )
            for msg in messages
        ]
        self._session.add_all(records)
        await self._session.commit()

    async def load_messages(self, user_id: str) -> list[dict[str, str]]:
        """Recupera el historial completo de un usuario ordenado cronológicamente.

        Returns:
            Lista de dicts ``{"role": ..., "content": ...}``.
        """
        stmt = (
            select(ConversationRecord)
            .where(ConversationRecord.user_id == user_id)
            .order_by(ConversationRecord.timestamp.asc())
        )
        result = await self._session.execute(stmt)
        rows = result.scalars().all()
        return [{"role": r.role, "content": r.content} for r in rows]

    async def delete_messages(self, user_id: str) -> None:
        """Elimina todo el historial de un usuario."""
        stmt = delete(ConversationRecord).where(
            ConversationRecord.user_id == user_id
        )
        await self._session.execute(stmt)
        await self._session.commit()
