#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

tec_python="${TEC_PYTHON:-$PWD/.venv/bin/python}"
if [[ ! -x "$tec_python" && -z "${TEC_PYTHON:-}" && -x ../.venv/bin/python ]]; then
    tec_python="$PWD/../.venv/bin/python"
fi
if [[ ! -x "$tec_python" ]]; then
    echo "Crie o ambiente de tec/ seguindo o README.md." >&2
    exit 1
fi

modo="${1:-adaptado}"
if [[ $# -gt 0 ]]; then shift; fi
case "$modo" in
    oficial)
        exec "$tec_python" -u exemplo_oficial.py
        ;;
    adaptado)
        if [[ $# -eq 0 ]]; then
            set -- cadernos/caderno-1.png cadernos/caderno-2.png cadernos/caderno-3.png
        fi
        exec "$tec_python" -u ler_caderno.py "$@"
        ;;
    *)
        echo "Uso: ./tec/rodar.sh [oficial|adaptado [cadernos/imagem.png ...]]" >&2
        exit 2
        ;;
esac
