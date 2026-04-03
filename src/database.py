"""
DIVIServer — Configuración de base de datos.

Motor asíncrono SQLAlchemy + Base declarativa + init_db().
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text

from src.config import settings


# ---------------------------------------------------------------------------
# Motor y sesión
# ---------------------------------------------------------------------------

engine = create_async_engine(settings.database_async_url, echo=False)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# ---------------------------------------------------------------------------
# Base declarativa
# ---------------------------------------------------------------------------

class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# Inicialización
# ---------------------------------------------------------------------------

logger = logging.getLogger(__name__)


async def init_db() -> None:
    """Crea todas las tablas y habilita la extensión pgvector.

    Si la base de datos no está disponible, se loguea un warning y
    la aplicación continúa (las operaciones de DB fallarán hasta que
    PostgreSQL esté disponible).
    """
    try:
        async with engine.begin() as conn:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Tablas e extensión pgvector creadas correctamente.")
    except Exception as e:
        logger.warning(
            "No se pudo conectar a PostgreSQL al inicio: %s. "
            "La app continuará, pero las operaciones de DB fallarán "
            "hasta que la base esté disponible.",
            e,
        )


async def get_db() -> AsyncSession:
    """Generador de sesiones para inyección de dependencias en FastAPI."""
    async with async_session() as session:
        yield session
