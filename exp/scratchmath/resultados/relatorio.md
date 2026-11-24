# Resultados — Benchmark Atlas do Erro no `songdj/ScratchMath` (`middle`, N = 241)

Avaliação sobre rascunhos manuscritos reais do 7º ao 9º ano com Ground Truth anotado por professores (Song et al., AIED 2026 / `arXiv:2603.24961`), **sem tradução prévia do dataset** (dicionário fixo das 7 categorias oficiais + prompts em PT-BR com saída JSON Schema fechada, `temperature=0`).

## 1. Cobertura da pipeline determinística (TrOCR + SymPy) nas fotos reais

- **Total de folhas avaliadas:** 241
- **`quebra` detectada pelo SymPy:** 0 (0.0%)
- **`sem_quebra` (equivalência mantida):** 0 (0.0%)
- **`ilegivel` (OCR ou parser SymPy falhou):** 241 (100.0%)
- **Distribuição interna da Regra (checklist Atlas):** {'outro': 241}

## 2. Tabela principal — Classificação do tipo de erro (ECC, 7 classes) e segurança pedagógica

| Condição | Cobertura | ECC Geral [IC 95%] | ECC Condicional | F1 Macro | Pista vaza resposta | Tempo médio (s) | ECE (juiz `qwen2.5:7b`) |
|:---|---:|---:|---:|---:|---:|---: |---:|
| *Baseline majoritário (sempre `erro_calculo`)* | 100.0% | **46.9%** [40.7–53.1%] | 46.9% | 0.091 | — | — | — |
| A1 · Atlas + Regra (TrOCR+SymPy+Checklist) | 0/241 (0.0%) | **0.0%** [0.0–0.0%] | 0.0% | 0.000 | 0/241 (0.0%) | 0.14 | 0.0% [0.0–0.0%] |
| A2 · Atlas + Qwen2.5 1.5B (pós-TrOCR+SymPy) | 0/241 (0.0%) | **0.0%** [0.0–0.0%] | 0.0% | 0.000 | 0/0 | 0.14 | 0.0% [0.0–0.0%] |
| A3 · Atlas + Gemma2 2B (pós-TrOCR+SymPy) | 0/241 (0.0%) | **0.0%** [0.0–0.0%] | 0.0% | 0.000 | 0/0 | 0.14 | 0.0% [0.0–0.0%] |
| B1 · Passo 3 isolado: Qwen2.5 1.5B (enunciado+solução) | 240/241 (99.6%) | **26.1%** [20.7–32.0%] | 26.2% | 0.091 | 7/240 (2.9%) | 0.58 | 3.3% [1.2–5.8%] |
| B2 · Passo 3 isolado: Gemma2 2B (enunciado+solução) | 241/241 (100.0%) | **9.1%** [5.8–13.3%] | 9.1% | 0.063 | 0/241 (0.0%) | 0.75 | 2.1% [0.4–4.1%] |
| C1 · Multimodal local: Qwen2.5-VL 3B (foto direto) | 240/241 (99.6%) | **46.5%** [40.2–52.7%] | 46.7% | 0.092 | 1/240 (0.4%) | 1.67 | 4.1% [1.7–6.6%] |

### Referência publicada no artigo (Song et al., AIED 2026 — `middle`, 241 folhas)

| Modelo / Referência (Artigo) | ECC (7 classes) | ECE (juiz do artigo) |
|:---|---:|---:|
| Professores humanos | 81.5% | 86.2% |
| o4-mini (melhor do artigo) | 47.3% | 69.7% |
| Gemma-3 27B | 46.1% | 26.1% |
| Qwen2.5-VL 7B | 11.6% | 12.4% |
| Chute aleatório | 12.5% | 0.0% |

## 3. Diferenças pareadas (ECC Geral, pontos percentuais, IC 95% bootstrap)

| Comparação (A − B) | Diferença (pp) | IC 95% (pp) |
|:---|---:|---:|
| `A2_atlas_qwen25_1.5b` − `A1_regra` | +0.0 | [+0.0, +0.0] |
| `A3_atlas_gemma2_2b` − `A1_regra` | +0.0 | [+0.0, +0.0] |
| `B1_texto_qwen25_1.5b` − `A1_regra` | +26.1 | [+20.7, +32.0] |
| `B2_texto_gemma2_2b` − `A1_regra` | +9.1 | [+5.8, +13.3] |
| `B1_texto_qwen25_1.5b` − `B2_texto_gemma2_2b` | +17.0 | [+10.4, +23.7] |
| `C1_visao_qwen25vl_3b` − `B1_texto_qwen25_1.5b` | +20.3 | [+13.3, +27.0] |
| `C1_visao_qwen25vl_3b` − `B2_texto_gemma2_2b` | +37.3 | [+29.5, +44.8] |

## 4. Distribuição das categorias previstas por condição (viés de colapso)

| Condição | `erro_calculo` | `erro_compreensao` | `lacuna_conhecimento` | `erro_estrategia` | `erro_transcricao` | `erro_raciocinio` | `erro_atencao` | `sem_resposta` |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|
| **GT real (professores)** | 113 | 20 | 45 | 17 | 29 | 2 | 15 | 0 |
| `A1_regra` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 241 |
| `A2_atlas_qwen25_1.5b` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 241 |
| `A3_atlas_gemma2_2b` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 241 |
| `B1_texto_qwen25_1.5b` | 99 | 0 | 0 | 0 | 141 | 0 | 0 | 1 |
| `B2_texto_gemma2_2b` | 4 | 158 | 0 | 42 | 8 | 29 | 0 | 0 |
| `C1_visao_qwen25vl_3b` | 234 | 0 | 0 | 0 | 6 | 0 | 0 | 1 |

## 5. F1 por classe nas principais condições

| Categoria GT (suporte) | `A1_regra` | `B1_texto_qwen25_1.5b` | `B2_texto_gemma2_2b` | `C1_visao_qwen25vl_3b` |
|:---|---:|---:|---:|---:|
| `erro_calculo` (113) | 0.00 (0/113) | 0.43 (46/113) | 0.05 (3/113) | 0.65 (112/113) |
| `erro_compreensao` (20) | 0.00 (0/20) | 0.00 (0/20) | 0.13 (12/20) | 0.00 (0/20) |
| `lacuna_conhecimento` (45) | 0.00 (0/45) | 0.00 (0/45) | 0.00 (0/45) | 0.00 (0/45) |
| `erro_estrategia` (17) | 0.00 (0/17) | 0.00 (0/17) | 0.20 (6/17) | 0.00 (0/17) |
| `erro_transcricao` (29) | 0.00 (0/29) | 0.20 (17/29) | 0.05 (1/29) | 0.00 (0/29) |
| `erro_raciocinio` (2) | 0.00 (0/2) | 0.00 (0/2) | 0.00 (0/2) | 0.00 (0/2) |
| `erro_atencao` (15) | 0.00 (0/15) | 0.00 (0/15) | 0.00 (0/15) | 0.00 (0/15) |