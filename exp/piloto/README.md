# Piloto do exp

Scripts, dados e resultados dos pilotos de [exp.md](../exp.md). Tudo roda no notebook Linux da
aluna (WSL2, i5-13450HX, 16 GB, RTX 4050), com o ambiente `tec/.venv` e o Ollama 0.32.1.

| Arquivo | O que é |
| --- | --- |
| [gerar_dados.py](gerar_dados.py) | gera as 60 resoluções sintéticas do E1 e o gabarito, com semente fixa |
| [dados/](dados/) | as imagens e o `gabarito.json` |
| [fontes/](fontes/) | Patrick Hand, Caveat e Kalam, com as licenças SIL Open Font License 1.1 |
| [piloto_e1.py](piloto_e1.py) | o piloto do E1: Atlas completo e ablações, com intervalo de 95% |
| [recontar_pistas.py](recontar_pistas.py) | emenda 2 do E1: recontagem das pistas com a resposta, sem rodar os modelos de novo |
| [piloto_e2.py](piloto_e2.py) | o piloto do E2, primeira versão: protocolo testado com persona de IA |
| [piloto_e2_v2.py](piloto_e2_v2.py) | o piloto do E2, segunda versão, com os defeitos da primeira corrigidos (emenda 4) |
| [resultados/](resultados/) | as tabelas e os registros de cada caso |

Na raiz do repositório:

```bash
tec/.venv/bin/python -I exp/piloto/gerar_dados.py
HF_HUB_OFFLINE=1 tec/.venv/bin/python -I exp/piloto/piloto_e1.py
tec/.venv/bin/python -I exp/piloto/recontar_pistas.py
tec/.venv/bin/python -I exp/piloto/piloto_e2.py
tec/.venv/bin/python -I exp/piloto/piloto_e2_v2.py
```

As resoluções são sintéticas, digitadas em fontes que imitam letra à mão: não representam
cadernos reais de alunos.
