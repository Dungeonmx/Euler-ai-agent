"""
Router de chat — endpoint para interactuar con el agente.
"""

from fastapi import APIRouter

from src.models.chat import ChatRequest, ChatResponse
from src.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["Chat"])

# Instancia singleton del servicio de chat
_chat_service = ChatService()


def get_chat_service() -> ChatService:
    """Retorna la instancia singleton del servicio de chat."""
    return _chat_service


@router.post(
    "",
    response_model=ChatResponse,
    summary="Enviar mensaje al asistente",
    description="Envía un mensaje al agente Euler y recibe una respuesta. "
    "Se debe incluir el `user_id` para identificar al usuario.",
)
async def send_message(request: ChatRequest) -> ChatResponse:
    """Procesa un mensaje del usuario y retorna la respuesta del agente."""
    service = get_chat_service()
    return await service.send_message(request.user_id, request.message)
