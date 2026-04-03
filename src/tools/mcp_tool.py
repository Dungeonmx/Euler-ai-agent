"""
Herramienta MCP — permite al agente obtener recursos específicos
desde un servidor MCP configurable.
"""

import logging

import httpx
from langchain_core.tools import tool

from src.config import settings

logger = logging.getLogger(__name__)


@tool
async def mcp_get_resource(resource_uri: str) -> str:
    """Obtiene un recurso específico desde el servidor MCP.

    Úsala cuando necesites consultar información institucional actualizada,
    como horarios, planes de estudio, contactos, o cualquier recurso
    que el servidor MCP provea.

    Args:
        resource_uri: URI del recurso a obtener (ej: 'horarios/2026',
                      'carreras/ingenieria-sistemas').

    Returns:
        Contenido del recurso en texto plano, o un mensaje de error
        si el recurso no está disponible.
    """
    base_url = getattr(settings, "mcp", None)
    if base_url and hasattr(base_url, "base_url"):
        url = f"{base_url.base_url}/{resource_uri}"
    else:
        url = f"http://localhost:8080/mcp/{resource_uri}"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text
    except httpx.HTTPStatusError as e:
        logger.warning("MCP recurso no encontrado: %s — %s", resource_uri, e)
        return f"No se encontró el recurso: {resource_uri}"
    except httpx.RequestError as e:
        logger.error("MCP error de conexión: %s", e)
        return f"Error al conectar con el servidor MCP: {e}"
