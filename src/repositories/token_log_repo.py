"""
Repositorio de logs de tokens — registro de consumo por interacción.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.token_log import TokenLogRecord


class TokenLogRepository:
    """Acceso a la tabla `token_logs`."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save_log(
        self,
        user_id: str,
        tokens_in: int,
        tokens_out: int,
    ) -> None:
        """Registra una entrada de consumo de tokens.

        Args:
            user_id: Identificador del usuario.
            tokens_in: Tokens consumidos en la pregunta.
            tokens_out: Tokens generados en la respuesta.
        """
        record = TokenLogRecord(
            user_id=user_id,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
        )
        self._session.add(record)
        await self._session.commit()
