"""
Servicio de token logging — conteo y registro del consumo de tokens.
"""

import tiktoken

from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.token_log_repo import TokenLogRepository


# ---------------------------------------------------------------------------
# Contador de tokens
# ---------------------------------------------------------------------------

def count_tokens(text: str, model: str = "gpt-4") -> int:
    """Cuenta la cantidad de tokens de un texto usando tiktoken.

    Nota: tiktoken no tiene encodings específicos para modelos locales,
    se usa cl100k_base (GPT-4) como aproximación razonable.
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


# ---------------------------------------------------------------------------
# Servicio
# ---------------------------------------------------------------------------

class TokenLogService:
    """Registra el consumo de tokens de cada interacción."""

    def __init__(self, session: AsyncSession) -> None:
        self._repo = TokenLogRepository(session)

    async def log_usage(
        self,
        user_id: str,
        question: str,
        answer: str,
    ) -> tuple[int, int]:
        """Cuenta tokens de pregunta y respuesta, persiste el log.

        Returns:
            Tupla ``(tokens_in, tokens_out)``.
        """
        tokens_in = count_tokens(question)
        tokens_out = count_tokens(answer)
        await self._repo.save_log(user_id, tokens_in, tokens_out)
        return tokens_in, tokens_out
