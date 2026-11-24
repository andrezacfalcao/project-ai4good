# ScratchMath · Avaliação do Atlas do Erro sobre Ground Truth real

Avaliação empírica da pipeline do **Atlas do Erro** sobre o split `middle` (7º ao 9º ano, **241 rascunhos manuscritos reais**) do dataset [`songdj/ScratchMath`](https://huggingface.co/datasets/songdj/ScratchMath) (Song et al., AIED 2026, `arXiv:2603.24961`), executada em **dois ciclos** 100% localmente (Ollama + RTX 5070, sem API paga):

- **Ciclo 1 (`resultados/relatorio.md`):** pipeline original (`TrOCR-printed` + `SymPy` + Regra/Qwen/Gemma) e modelos locais nas 241 folhas originais em chinês (com dicionário fixo das 7 categorias).
- **Ciclo 2 (`resultados_v2/relatorio_v2.md`):** escopo filtrado para as **57 equações do 1º grau**, tradução local PT-BR das 241 folhas (`qwen2.5:7b`), comparação de 4 leitores no Passo 1 (`TrOCR-printed`, `Pix2Text` CPU, `Qwen2.5-VL 3B`, `Qwen2.5-VL 7B`) e confronto direto no Passo 3 (`Regra` × `Qwen2.5 1.5B` × `Gemma2 2B` × `Qwen2.5 7B`).

## Arquivos

| Arquivo | Função |
|:---|:---|
| [`categorias.py`](categorias.py) | Taxonomia oficial das 7 categorias do ScratchMath (chinês, inglês, português) e mapeamento determinístico da Regra |
| [`baixar_dataset.py`](baixar_dataset.py) | Baixa `songdj/ScratchMath` (`middle`), salva imagens em `dados/imagens/` (ignorado no Git) e gera `dados/middle.jsonl` e `dados/raiox_dataset.md` |
| [`regra.py`](regra.py) | Pipeline determinística (`SymPy` com normalizador LaTeX) + **Regra das correções típicas** (`distributiva`, `troca_sinal`, `divisao`, `conta`, `outro`) com testes unitários (48/48 no piloto sintético limpo) |
| [`rodar_experimento.py`](rodar_experimento.py) | Executor do Ciclo 1 (`N = 241`, original) com checkpoint em `resultados/*.jsonl` |
| [`avaliar.py`](avaliar.py) | Métricas do Ciclo 1 (ECC, IC 95% bootstrap, F1 macro, vazamento e juiz local ECE) |
| [`PLANO_V2.md`](PLANO_V2.md) | Planejamento técnico do Ciclo 2 (escopo, OCRs, tradução) |
| [`preparar_v2.py`](preparar_v2.py) | Congela `dados/escopo_1grau.jsonl` (`N = 57`) e traduz as 241 folhas localmente via `qwen2.5:7b` para `dados/middle_pt.jsonl` |
| [`rodar_v2.py`](rodar_v2.py) | Executor do Ciclo 2: 4 OCRs no Passo 1 (`N = 57`), Atlas V2 (`N = 57`) e benchmark completo em PT-BR (`N = 241`) |
| [`avaliar_v2.py`](avaliar_v2.py) | Métricas e juiz ECE do Ciclo 2 (`resultados_v2/relatorio_v2.md`) |
| [`gerar_graficos_v2.py`](gerar_graficos_v2.py) | Gera gráficos em 300 DPI (`resultados_v2/figuras/`) na paleta da apresentação |
| [`atualizar_pptx.py`](atualizar_pptx.py) | Monta a apresentação narrativa de 10 slides com notas do apresentador |
| [`apresentacao_atlas_scratchmath.pptx`](apresentacao_atlas_scratchmath.pptx) | Cópia da apresentação atualizada com os resultados dos Ciclos 1 e 2 |

## Como reproduzir

A partir da raiz do repositório (com Ollama ativo e `qwen2.5:1.5b`, `gemma2:2b`, `qwen2.5:7b`, `qwen2.5vl:3b` e `qwen2.5vl:7b`):

```bash
# Ciclo 1
.venv/bin/python exp/scratchmath/baixar_dataset.py
.venv/bin/python exp/scratchmath/regra.py
.venv/bin/python exp/scratchmath/rodar_experimento.py
.venv/bin/python exp/scratchmath/avaliar.py --juiz-local qwen2.5:7b

# Ciclo 2 (escopo 1º grau + tradução PT-BR local + 4 OCRs)
.venv/bin/python exp/scratchmath/preparar_v2.py
.venv/bin/python exp/scratchmath/rodar_v2.py --fase todas
.venv/bin/python exp/scratchmath/avaliar_v2.py --juiz-local qwen2.5:7b
.venv/bin/python exp/scratchmath/gerar_graficos_v2.py
```
