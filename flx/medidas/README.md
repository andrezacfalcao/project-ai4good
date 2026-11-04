# Medidas do flx

Medidas usadas no § 2 de [flx.md](../flx.md), feitas em 04/11/2026 no notebook Linux da aluna
(WSL2, Intel i5-13450HX, 16 GB, RTX 4050), com o ambiente `tec/.venv` e o Ollama 0.32.1.
Os scripts repetem a lógica de `tec/ler_caderno.py` (commit `abf1638`) sem alterá-lo.

| Script | Saída | O que mede |
| --- | --- | --- |
| [tempo_regras.py](tempo_regras.py) | [tempo_regras.saida.txt](tempo_regras.saida.txt) | SymPy por caderno (passo 6) e contagem do atlas com 120 entradas |
| [tokens_qwen.py](tokens_qwen.py) | [tokens_qwen.saida.txt](tokens_qwen.saida.txt) | tokens de entrada e saída e tempo de cada chamada do Qwen |
| [ponta_a_ponta.py](ponta_a_ponta.py) | [ponta_a_ponta.saida.txt](ponta_a_ponta.saida.txt) | OCR, SymPy e Qwen por caderno, e o total da foto à pista |

Na raiz do repositório:

```bash
tec/.venv/bin/python -I flx/medidas/tempo_regras.py
python3 -I flx/medidas/tokens_qwen.py
HF_HUB_OFFLINE=1 tec/.venv/bin/python -I flx/medidas/ponta_a_ponta.py tec/cadernos/caderno-*.png
```

São execuções únicas sobre as três imagens sintéticas do tec, não um benchmark. O OCR roda em
CPU e o Qwen na GPU. Nada foi medido em celular.
