"""
Router de health — estado del servicio.
"""

import logging

import httpx
from fastapi import APIRouter
from sqlalchemy import text

from src.config import settings
from src.database import async_session

router = APIRouter(prefix="/health", tags=["Health"])
logger = logging.getLogger(__name__)


@router.get(
    "",
    summary="Estado del servicio",
    description="Verifica la conectividad con la base de datos y los "
    "servidores de llama.cpp (chat y embeddings).",
)
async def health_check() -> dict:
    """Retorna el estado de conexión de cada componente."""
    status = {
        "api": "ok",
        "database": "unknown",
        "llamacpp_chat": "unknown",
        "llamacpp_embeddings": "unknown",
    }

    # Database
    try:
        async with async_session() as db:
            await db.execute(text("SELECT 1"))
        status["database"] = "ok"
    except Exception as e:
        logger.warning("Health check DB falló: %s", e)
        status["database"] = f"error: {e}"

    # LlamaCPP — chat
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            base = settings.llm_base_url.replace("/v1", "")
            resp = await client.get(f"{base}/health")
            status["llamacpp_chat"] = "ok" if resp.status_code == 200 else f"status {resp.status_code}"
    except Exception as e:
        logger.warning("Health check LlamaCPP chat falló: %s", e)
        status["llamacpp_chat"] = f"error: {e}"

    # LlamaCPP — embeddings
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            base = settings.embeddings_base_url.replace("/v1", "")
            resp = await client.get(f"{base}/health")
            status["llamacpp_embeddings"] = "ok" if resp.status_code == 200 else f"status {resp.status_code}"
    except Exception as e:
        logger.warning("Health check LlamaCPP embeddings falló: %s", e)
        status["llamacpp_embeddings"] = f"error: {e}"

    return status
