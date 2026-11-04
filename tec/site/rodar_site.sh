#!/usr/bin/env bash
# Abre o site do Atlas do Erro em http://localhost:8501. Precisa do Ollama ativo para a pista.
set -euo pipefail
cd "$(dirname "$0")/../.."
exec env HF_HUB_OFFLINE="${HF_HUB_OFFLINE:-1}" tec/.venv/bin/streamlit run tec/site/app.py "$@"
