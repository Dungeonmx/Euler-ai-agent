"""
Servicio de chat — gestión de sesiones en memoria con eviction automática
y persistencia/recuperación de historial en PostgreSQL.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage

from src.config import settings
from src.database import async_session
from src.models.chat import ChatResponse
from src.repositories.conversation_repo import ConversationRepository
from src.services.agent_service import create_chain
from src.services.rag_service import RAGService
from src.services.token_log_service import TokenLogService

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Datos de sesión
# ---------------------------------------------------------------------------


@dataclass
class SessionData:
    """Estado de una sesión activa en memoria."""

    history: ChatMessageHistory = field(default_factory=ChatMessageHistory)
    last_activity: datetime = field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Servicio
# ---------------------------------------------------------------------------


class ChatService:
    """Orquesta el ciclo de vida de las sesiones de chat.

    - Mantiene sesiones activas en memoria.
    - Evicta sesiones inactivas (persistiéndolas a DB).
    - Recupera historial de DB al reactivar un usuario.
    - Integra RAG para inyectar contexto relevante.
    - Registra logs de tokens por cada interacción.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, SessionData] = {}
        self._chain = create_chain()
        self._eviction_task: asyncio.Task | None = None

    # ----- Ciclo de vida -----

    def start_eviction_loop(self) -> None:
        """Inicia la tarea periódica de eviction en background."""
        self._eviction_task = asyncio.create_task(self._eviction_loop())

    def stop_eviction_loop(self) -> None:
        """Detiene la tarea de eviction."""
        if self._eviction_task:
            self._eviction_task.cancel()

    async def _eviction_loop(self) -> None:
        """Loop que revisa sesiones inactivas cada N minutos."""
        interval = settings.chat_eviction_interval_minutes * 60
        while True:
            await asyncio.sleep(interval)
            await self._evict_inactive_sessions()

    async def _evict_inactive_sessions(self) -> None:
        """Persiste a DB y elimina de memoria las sesiones inactivas."""
        timeout = timedelta(minutes=settings.chat_session_timeout_minutes)
        now = datetime.utcnow()
        to_evict = [
            uid
            for uid, data in self._sessions.items()
            if (now - data.last_activity) > timeout
        ]

        for user_id in to_evict:
            await self._persist_session(user_id)
            del self._sessions[user_id]
            logger.info(
                "Sesión eliminada de memoria principal y persistida: %s", user_id
            )

    async def _persist_session(self, user_id: str) -> None:
        """Guarda el historial en memoria de un usuario a PostgreSQL."""
        session_data = self._sessions.get(user_id)
        if not session_data:
            return

        messages = [
            {
                "role": "user" if isinstance(msg, HumanMessage) else "assistant",
                "content": msg.content,
            }
            for msg in session_data.history.messages
        ]

        if not messages:
            return

        async with async_session() as db:
            repo = ConversationRepository(db)
            # Borramos historial previo para evitar duplicados y guardamos el actual
            await repo.delete_messages(user_id)
            await repo.save_messages(user_id, messages)

    async def _restore_session(self, user_id: str) -> SessionData:
        """Recupera el historial de un usuario desde PostgreSQL."""
        session_data = SessionData()

        async with async_session() as db:
            repo = ConversationRepository(db)
            messages = await repo.load_messages(user_id)

        for msg in messages:
            if msg["role"] == "user":
                session_data.history.add_user_message(msg["content"])
            else:
                session_data.history.add_ai_message(msg["content"])

        return session_data

    # ----- API pública -----

    async def send_message(self, user_id: str, message: str) -> ChatResponse:
        """Procesa un mensaje del usuario y retorna la respuesta del agente.

        1. Recupera o crea sesión.
        2. Obtiene contexto RAG.
        3. Invoca la cadena LangChain.
        4. Registra log de tokens.
        5. Retorna respuesta.
        """
        # 1. Obtener sesión
        if user_id not in self._sessions:
            self._sessions[user_id] = await self._restore_session(user_id)

        session = self._sessions[user_id]
        session.last_activity = datetime.utcnow()

        # 2. Contexto RAG (tolerante a fallos)
        context = ""
        try:
            async with async_session() as db:
                rag = RAGService(db)
                relevant_chunks = await rag.retrieve(message)
                if relevant_chunks:
                    context = (
                        "Información relevante del contexto institucional:\n"
                        + "\n---\n".join(relevant_chunks)
                    )
        except Exception as e:
            logger.warning("RAG retrieval falló, continuando sin contexto: %s", e)

        # 3. Invocar cadena
        response = await self._chain.ainvoke(
            {
                "input_message": message,
                "history": session.history.messages,
                "context": context,
            }
        )

        # 4. Actualizar historial
        session.history.add_user_message(message)
        session.history.add_ai_message(response.content)

        # 5. Log de tokens
        async with async_session() as db:
            token_service = TokenLogService(db)
            tokens_in, tokens_out = await token_service.log_usage(
                user_id, message, response.content
            )

        return ChatResponse(
            user_id=user_id,
            response=response.content,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
        )
