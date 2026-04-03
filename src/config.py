"""
DIVIServer — Módulo de configuración.

Carga variables de entorno (.env) mediante pydantic-settings.
"""

import os
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Configuración de la aplicación cargada desde variables de entorno."""

    # Server
    server_host: str = "0.0.0.0"
    server_port: int = 8080

    # LLM
    llm_base_url: str = "http://localhost:8000/v1"
    llm_api_key: str = "not-needed"
    llm_model: str = "LFM2-2.6B-Exp"
    llm_temperature: float = 0.5

    # Embeddings
    embeddings_base_url: str = "http://localhost:8001/v1"
    embeddings_api_key: str = "not-needed"
    embeddings_model: str = "nomic-embed-text-v2-moe.Q8_0"

    # Database
    database_host: str = "localhost"
    database_port: int = 5432
    database_user: str = "postgres"
    database_password: str = "postgres"
    database_name: str = "postgres"

    # Chat
    chat_session_timeout_minutes: int = 30
    chat_eviction_interval_minutes: int = 5

    # RAG
    rag_chunk_size: int = 512
    rag_chunk_overlap: int = 50
    rag_top_k: int = 5

    @property
    def database_async_url(self) -> str:
        """URL de conexión asíncrona para SQLAlchemy."""
        return (
            f"postgresql+asyncpg://{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.database_port}/{self.database_name}"
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
