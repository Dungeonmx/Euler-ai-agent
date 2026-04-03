#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

MODELS_DIR=".models"
LLM_MODEL="LFM2-2.6B-Exp-Q8_0.gguf"
EMB_MODEL="nomic-embed-text-v2-moe.Q8_0.gguf"

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info()  { echo -e "${GREEN}[✓]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[✗]${NC} $1"; }
step()  { echo -e "\n${GREEN}▶${NC} $1"; }

# ---------------------------------------------------------------------------
# Verificar dependencias del host
# ---------------------------------------------------------------------------

step "Verificando dependencias del sistema..."

command -v docker >/dev/null 2>&1 || { error "Docker no está instalado."; exit 1; }
command -v curl   >/dev/null 2>&1 || { error "curl no está instalado.";    exit 1; }

info "Docker instalado: $(docker --version)"
info "curl instalado"

# ---------------------------------------------------------------------------
# Descargar modelos
# ---------------------------------------------------------------------------

step "Verificando modelos..."
mkdir -p "$MODELS_DIR"

download_if_missing() {
    local url="$1"
    local dest="$2"
    local name
    name=$(basename "$dest")

    if [ -f "$dest" ]; then
        info "$name ya existe, omitiendo descarga."
    else
        warn "Descargando $name..."
        curl -L -# -o "$dest" "$url"
        info "$name descargado correctamente."
    fi
}

download_if_missing \
    "https://huggingface.co/ss-lab/LFM2-2.6B-Exp-GGUF/resolve/main/$LLM_MODEL" \
    "$MODELS_DIR/$LLM_MODEL"

download_if_missing \
    "https://huggingface.co/nomic-ai/nomic-embed-text-v2-moe-GGUF/resolve/main/$EMB_MODEL" \
    "$MODELS_DIR/$EMB_MODEL"

# ---------------------------------------------------------------------------
# Construir y levantar servicios
# ---------------------------------------------------------------------------

step "Construyendo imagen de la aplicación..."
docker compose build --quiet

step "Levantando servicios (llama.cpp, PostgreSQL, app)..."
docker compose up -d

# ---------------------------------------------------------------------------
# Esperar a que la app esté lista
# ---------------------------------------------------------------------------

step "Esperando a que los servicios estén saludables..."

MAX_WAIT=180
ELAPSED=0
INTERVAL=3

while [ $ELAPSED -lt $MAX_WAIT ]; do
    if curl -sf http://localhost:8080/api/health >/dev/null 2>&1; then
        info "¡DIVIServer está listo!"
        echo ""
        echo "=============================================="
        echo "  Euler AI Agent — DIVIServer"
        echo "=============================================="
        echo ""
        echo "  API:        http://localhost:8080"
        echo "  Docs:       http://localhost:8080/docs"
        echo "  Health:     http://localhost:8080/api/health"
        echo ""
        echo "  LLM:        http://localhost:8000"
        echo "  Embeddings: http://localhost:8001"
        echo "  PostgreSQL: localhost:5432"
        echo ""
        echo "  Detener:    docker compose down"
        echo "  Logs:       docker compose logs -f"
        echo "=============================================="
        exit 0
    fi
    sleep $INTERVAL
    ELAPSED=$((ELAPSED + INTERVAL))
done

error "Timeout: la aplicación no respondió en ${MAX_WAIT}s."
warn "Revisar logs: docker compose logs -f app"
exit 1
