"""
DIVIServer — Entry point.

API REST para el asistente educacional Euler de la Facultad de Ingeniería
de la Universidad Nacional de La Pampa.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.database import init_db
from src.routers import chat_router, document_router, health_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)-25s | %(levelname)-7s | %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan — inicio y apagado de la aplicación
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestiona el ciclo de vida de la app:
    - Startup: inicializa DB y arranca eviction loop.
    - Shutdown: detiene eviction loop.
    """
    logger.info("Iniciando DIVIServer...")

    # Inicializar base de datos (crear tablas + extensión pgvector)
    await init_db()
    logger.info("Base de datos inicializada.")

    # Arrancar loop de eviction de sesiones inactivas
    from src.routers.chat_router import get_chat_service
    chat_service = get_chat_service()
    chat_service.start_eviction_loop()
    logger.info(
        "Eviction loop iniciado (timeout: %d min, intervalo: %d min).",
        settings.chat_session_timeout_minutes,
        settings.chat_eviction_interval_minutes,
    )

    yield

    # Shutdown
    chat_service.stop_eviction_loop()
    logger.info("DIVIServer detenido.")


# ---------------------------------------------------------------------------
# App FastAPI
# ---------------------------------------------------------------------------

app = FastAPI(
    title="DIVIServer — Euler",
    description=(
        "API REST del asistente educacional Euler para la Facultad de "
        "Ingeniería de la UNLPam. Integra un agente de IA local con RAG, "
        "gestión de sesiones y logging de tokens."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(chat_router.router, prefix="/api")
app.include_router(document_router.router, prefix="/api")
app.include_router(health_router.router, prefix="/api")


@app.get("/", tags=["Root"])
async def root():
    """Endpoint raíz — info básica de la API."""
    return {
        "name": "DIVIServer — Euler",
        "version": "1.0.0",
        "docs": "/docs",
    }
