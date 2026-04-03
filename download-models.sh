#!/usr/bin/env bash
set -e

MODELS_DIR=".models"
mkdir -p "$MODELS_DIR"

# ---------------------------------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------------------------------

download_if_missing() {
    local url="$1"
    local dest="$2"
    local name
    name=$(basename "$dest")

    if [ -f "$dest" ]; then
        echo "[OK] $name ya existe, omitiendo descarga."
    else
        echo "[↓] Descargando $name..."
        curl -L -# -o "$dest" "$url"
        echo "[✓] $name descargado correctamente."
    fi
}

# ---------------------------------------------------------------------------
# Descarga de modelos
# ---------------------------------------------------------------------------

echo "=============================================="
echo "  Descargando modelos para Euler AI Agent"
echo "=============================================="
echo ""

# LLM principal — LFM2-2.6B-Exp Q8_0
download_if_missing \
    "https://huggingface.co/ss-lab/LFM2-2.6B-Exp-GGUF/resolve/main/LFM2-2.6B-Exp-Q8_0.gguf" \
    "$MODELS_DIR/LFM2-2.6B-Exp-Q8_0.gguf"

# Embeddings — nomic-embed-text-v2-moe Q8_0
download_if_missing \
    "https://huggingface.co/nomic-ai/nomic-embed-text-v2-moe-GGUF/resolve/main/nomic-embed-text-v2-moe.Q8_0.gguf" \
    "$MODELS_DIR/nomic-embed-text-v2-moe.Q8_0.gguf"

echo ""
echo "=============================================="
echo "  Modelos listos en $MODELS_DIR/"
echo "=============================================="
ls -lh "$MODELS_DIR"
