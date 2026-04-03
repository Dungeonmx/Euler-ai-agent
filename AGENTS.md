# AGENTS.md — Euler AI Agent

## Project Overview

DIVIServer — API REST para el asistente educacional **Euler** de la Facultad de Ingeniería de la UNLPam. FastAPI + LangChain + PostgreSQL/pgvector + LLM local (llama.cpp).

## Commands

### Quick start (automated)
```bash
./start.sh                    # downloads models, builds, starts everything
```

### Manual start
```bash
docker compose up -d --build  # build and start all services
docker compose down           # stop all services
docker compose logs -f app    # follow app logs
```

### Run locally (dev mode)
```bash
pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload
```

### Download models only
```bash
./download-models.sh
```

### Testing
No test framework is currently configured. When adding tests, use **pytest**:
```bash
pip install pytest pytest-asyncio
pytest                          # run all tests
pytest tests/test_file.py       # run a single test file
pytest tests/test_file.py::test_name  # run a single test
```

### Linting / Formatting
No linter/formatter is currently configured. Recommended additions:
```bash
pip install ruff
ruff check src/                 # lint
ruff format src/                # format
```

## Architecture

```
src/
  main.py            — FastAPI app entry point, lifespan, CORS
  config.py          — Pydantic config models, loads config.yaml
  database.py        — SQLAlchemy async engine, session, Base
  models/            — Pydantic schemas + SQLAlchemy ORM tables
  repositories/      — Data access layer (DB queries)
  services/          — Business logic (chat, RAG, agent, tokens)
  routers/           — FastAPI APIRouter endpoints
  tools/             — MCP tool integrations
```

**Layer flow:** `routers → services → repositories → database`

## Code Style

### Imports
- Standard library first, then third-party, then `src.*` local imports
- Group imports with a blank line between groups
- Use absolute imports: `from src.config import settings` (never relative)

### Formatting
- 4-space indentation, no tabs
- Max line length: ~100 chars (implied by existing code)
- Use section dividers for large files:
  ```python
  # ---------------------------------------------------------------------------
  # Section Name
  # ---------------------------------------------------------------------------
  ```

### Naming Conventions
| Element | Convention | Example |
|---------|-----------|---------|
| Modules/files | `snake_case.py` | `chat_service.py` |
| Classes | `PascalCase` | `ChatService`, `ChatRequest` |
| Functions/methods | `snake_case` | `send_message()`, `create_chain()` |
| Private attrs | `_leading_underscore` | `_sessions`, `_eviction_task` |
| Constants | `UPPER_SNAKE_CASE` | `SYSTEM_PROMPT`, `EMBEDDING_DIM` |
| Variables | `snake_case` | `user_id`, `query_embedding` |

### Type Hints
- Use Python 3.10+ union syntax: `str | None` (not `Optional[str]`)
- Annotate all function signatures: `async def foo(x: str) -> int:`
- Use `-> None` for functions that return nothing
- Use `dict[str, SessionData]`, `list[str]` (built-in generics, not `typing.Dict`)

### Docstrings
- Triple double-quotes `"""..."""` for module, class, and method docstrings
- Spanish language for docstrings (project convention)
- Use Google-style Args/Returns sections for methods with parameters:
  ```python
  async def ingest_document(self, filename: str, content: str) -> DocResponse:
      """Procesa un documento: lo divide en chunks, genera embeddings y almacena.

      Args:
          filename: Nombre original del archivo.
          content: Contenido textual del documento.

      Returns:
          Respuesta con información del procesamiento.
      """
  ```

### Error Handling
- Use `try/except` with specific exceptions; avoid bare `except`
- Log failures with `logger.warning()` or `logger.error()` and continue gracefully
- External services (RAG, DB, LLM) must be fault-tolerant — never crash the app
- Example pattern from `chat_service.py`:
  ```python
  try:
      async with async_session() as db:
          rag = RAGService(db)
          chunks = await rag.retrieve(message)
  except Exception as e:
      logger.warning("RAG retrieval falló, continuando sin contexto: %s", e)
  ```

### Async Patterns
- All I/O operations are async: `async def`, `await`, `async with`
- Use `asyncio.create_task()` for background tasks (eviction loop)
- Use `async with async_session() as db:` for database sessions
- Cancel background tasks on shutdown

### Pydantic Models
- Separate **API schemas** (request/response) from **ORM tables**
- API schemas inherit `BaseModel`, ORM tables inherit `Base` (DeclarativeBase)
- Use `Field(...)` for required fields with descriptions
- Keep models in `src/models/`, one file per domain

### Logging
- Module-level logger: `logger = logging.getLogger(__name__)`
- Structured format defined in `main.py`
- Use `%s` placeholders, not f-strings, in log messages

### Configuration
- All config loaded from `.env` via `pydantic-settings` in `src/config.py`
- Access via singleton: `from src.config import settings`
- Add new settings as fields in the `Settings` class
- Env var naming: `SECTION_KEY` (e.g., `LLM_BASE_URL`, `RAG_CHUNK_SIZE`)
- Copy `.env.example` to `.env` for local development

## Key Dependencies

| Package | Purpose |
|---------|---------|
| `fastapi` | Web framework |
| `uvicorn` | ASGI server |
| `pydantic` / `pydantic-settings` | Config & validation |
| `langchain` / `langchain-openai` | LLM chains & prompts |
| `sqlalchemy[asyncio]` | Async ORM |
| `asyncpg` | Async PostgreSQL driver |
| `pgvector` | Vector similarity search |
| `tiktoken` | Token counting |

## Important Notes

- **Language:** Comments and docstrings are in Spanish — follow this convention
- **No tests exist yet** — add pytest when implementing new features
- **No linter exists yet** — consider adding Ruff for consistency
- **LLM runs locally** via llama.cpp (Docker), not cloud APIs
- **Embedding dimension:** 768 (nomic-embed-text-v2-moe model)
- **CORS:** Currently allows all origins (`["*"]`)
