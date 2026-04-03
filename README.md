# Euler AI Agent — DIVIServer

API REST para el asistente educacional **Euler** de la Facultad de Ingeniería de la Universidad Nacional de La Pampa (UNLPam). Integra un agente de IA local con RAG (Retrieval-Augmented Generation), gestión de sesiones conversacionales y registro de consumo de tokens.

## Características

- **Chat conversacional** con historial persistente por usuario
- **RAG** sobre documentos institucionales (ingesta, chunking, embeddings y búsqueda por similitud)
- **LLM local** mediante llama.cpp, sin dependencia de APIs externas
- **Embeddings** con modelo nomic-embed-text-v2-moe (768 dimensiones, multilingüe)
- **Eviction automática** de sesiones inactivas con persistencia a PostgreSQL
- **Registro de tokens** por interacción

## Requisitos

- **Docker** y **Docker Compose**
- **GPU con soporte Vulkan** (para inferencia local con llama.cpp)
- **curl** (para descarga de modelos y health checks)

## Estructura del proyecto

```
├── .env.example             # Plantilla de variables de entorno
├── .env                     # Configuración local (no versionado)
├── .dockerignore            # Excluye archivos del contexto Docker
├── docker-compose.yml       # Servicios: llama.cpp (x2) + PostgreSQL + app
```

## Puesta en marcha

### Opción rápida: un solo comando

El script `start.sh` automatiza todo: descarga modelos (si no existen), construye la imagen Docker, levanta todos los servicios y espera a que estén listos.

```bash
./start.sh
```

### Opción manual: paso a paso

**1. Descargar modelos** (solo si no quieres usar el script):

```bash
./download-models.sh
```

**2. Construir y levantar con Docker Compose:**

```bash
docker compose up -d --build
```

Esto levanta 4 servicios:
- **llama.cpp** (LLM) en `http://localhost:8000`
- **llama.cpp** (embeddings) en `http://localhost:8001`
- **PostgreSQL** con pgvector en `localhost:5432`
- **app** (DIVIServer) en `http://localhost:8080`

Los healthchecks garantizan que la app no arranca hasta que el LLM, embeddings y PostgreSQL estén listos.

### Acceso

| Servicio | URL |
|----------|-----|
| API REST | `http://localhost:8080` |
| Documentación interactiva | `http://localhost:8080/docs` |
| Health check | `http://localhost:8080/api/health` |
| LLM (llama.cpp) | `http://localhost:8000` |
| Embeddings (llama.cpp) | `http://localhost:8001` |

### Detener servicios

```bash
docker compose down
```

## Uso de la API

### Enviar un mensaje

```bash
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "usuario123", "message": "¿Cuáles son los requisitos para rendir final?"}'
```

### Subir un documento para RAG

```bash
curl -X POST http://localhost:8080/api/documents/upload \
  -F "file=@documento.pdf"
```

## Configuración

Editar `config.yaml` para ajustar:

| Sección | Parámetros clave |
|---------|-----------------|
| `server` | `host`, `port` |
| `llm` | `base_url`, `model`, `temperature` |
| `embeddings` | `base_url`, `model` |
| `database` | `host`, `port`, `user`, `password`, `name` |
| `chat` | `session_timeout_minutes`, `eviction_interval_minutes` |
| `rag` | `chunk_size`, `chunk_overlap`, `top_k` |

## Tecnologías

| Componente | Tecnología |
|------------|-----------|
| Web framework | FastAPI + Uvicorn |
| LLM | llama.cpp (LFM2-2.6B-Exp) |
| Embeddings | llama.cpp (nomic-embed-text-v2-moe) |
| Orquestación IA | LangChain |
| Base de datos | PostgreSQL 17 + pgvector |
| ORM | SQLAlchemy (async) |
| Configuración | Pydantic + YAML |
