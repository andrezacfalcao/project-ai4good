# Resultados V2 — OCR Manuscrito + Escopo 1º Grau (`N = 57`) + Tradução PT-BR (`N = 241`)

- **Tradução PT-BR:** 100% local via `qwen2.5:7b` (Opção B), salva em `dados/middle_pt.jsonl`.
- **OCR vencedor adotado no Atlas V2 (`N = 57`):** `OCR_qwen25vl_3b`.

## 1. Comparação de OCR no Passo 1 (`N = 57` equações do 1º grau)

| Modelo de OCR (Passo 1) | Equações válidas/folha | ≥1 eq. válida | SymPy quebra (puro) | SymPy quebra (ancorado) | Regra acertou GT | Tempo médio (s) |
|:---|---:|---:|---:|---:|---:|---:|
| TrOCR-printed (V1) | 0.00 | 0/57 | 0/57 (0.0%) | **0/57 (0.0%)** | 0/57 (0.0%) | 0.24 |
| Pix2Text (CPU, dedicado) | 1.23 | 26/57 | 17/57 (29.8%) | **25/57 (43.9%)** | 8/57 (14.0%) | 1.72 |
| Qwen2.5-VL 3B (VLM-OCR) | 1.54 | 30/57 | 15/57 (26.3%) | **28/57 (49.1%)** | 7/57 (12.3%) | 1.96 |
| Qwen2.5-VL 7B (VLM-OCR) | 1.67 | 29/57 | 18/57 (31.6%) | **27/57 (47.4%)** | 7/57 (12.3%) | 2.89 |

## 2. Pipeline Atlas V2 no escopo nativo (Equações do 1º grau) (`N = 57`)

| Condição | Cobertura | ECC Geral [IC 95%] | ECC Cond. | F1 Macro | Vaza resposta | Tempo (s) | ECE (juiz `qwen2.5:7b`) |
|:---|---:|---:|---:|---:|---:|---: |---:|
| *Chute majoritário (`erro_calculo`)* | 100.0% | **56.1%** [43.9–68.4%] | 56.1% | 0.103 | — | — | — |
| A1 · Atlas V2 + Regra (OCR vencedor + SymPy) | 21/57 (36.8%) | **12.3%** [5.3–21.1%] | 33.3% | 0.044 | 0/31 (0.0%) | 1.96 | 0.0% [0.0–0.0%] |
| A2 · Atlas V2 + Qwen2.5 1.5B (pós-SymPy, PT) | 28/57 (49.1%) | **8.8%** [1.8–17.5%] | 17.9% | 0.044 | 0/28 (0.0%) | 1.27 | 0.0% [0.0–0.0%] |
| A3 · Atlas V2 + Gemma2 2B (pós-SymPy, PT) | 28/57 (49.1%) | **1.8%** [0.0–5.3%] | 3.6% | 0.011 | 0/28 (0.0%) | 1.36 | 3.5% [0.0–8.8%] |
| A4 · Atlas V2 + Qwen2.5 7B (pós-SymPy, PT) | 28/57 (49.1%) | **22.8%** [12.3–35.1%] | 46.4% | 0.066 | 0/28 (0.0%) | 1.65 | 1.8% [0.0–5.3%] |
| B1 · Qwen2.5 1.5B (PT-BR + transcrição OCR) | 57/57 (100.0%) | **24.6%** [14.0–36.8%] | 24.6% | 0.082 | 1/57 (1.8%) | 0.57 | 0.0% [0.0–0.0%] |
| B2 · Gemma2 2B (PT-BR + transcrição OCR) | 57/57 (100.0%) | **7.0%** [1.8–14.0%] | 7.0% | 0.115 | 0/57 (0.0%) | 0.76 | 1.8% [0.0–5.3%] |
| B3 · Qwen2.5 7B (PT-BR + transcrição OCR) | 57/57 (100.0%) | **45.6%** [33.3–57.9%] | 45.6% | 0.094 | 0/57 (0.0%) | 1.13 | 12.3% [5.3–21.1%] |
| C2 · Qwen2.5-VL 7B (foto direto + PT-BR) | 57/57 (100.0%) | **43.9%** [31.6–56.1%] | 43.9% | 0.090 | 0/57 (0.0%) | 3.05 | 5.3% [0.0–12.3%] |

### Distribuição das categorias previstas (colapso de classes)

| Condição | `erro_calculo` | `erro_compreensao` | `lacuna_conhecimento` | `erro_estrategia` | `erro_transcricao` | `erro_raciocinio` | `erro_atencao` | `sem_resposta` |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|
| `V2_A1_regra` | 13 | 0 | 8 | 0 | 0 | 0 | 0 | 36 |
| `V2_A2_atlas_qwen25_1.5b` | 4 | 0 | 0 | 0 | 24 | 0 | 0 | 29 |
| `V2_A3_atlas_gemma2_2b` | 0 | 2 | 0 | 4 | 19 | 3 | 0 | 29 |
| `V2_A4_atlas_qwen25_7b` | 24 | 0 | 3 | 0 | 0 | 1 | 0 | 29 |
| `V2_B1_ocr_pt_qwen25_1.5b` | 10 | 0 | 0 | 0 | 47 | 0 | 0 | 0 |
| `V2_B2_ocr_pt_gemma2_2b` | 1 | 3 | 0 | 4 | 9 | 40 | 0 | 0 |
| `V2_B3_ocr_pt_qwen25_7b` | 47 | 0 | 0 | 0 | 8 | 1 | 1 | 0 |
| `V2_FULL_C2_visao_pt_qwen25vl_7b` | 47 | 0 | 0 | 0 | 10 | 0 | 0 | 0 |

## 3. Benchmark completo: efeito da tradução PT-BR e do Qwen2.5-VL 7B (`N = 241`)

| Condição | Cobertura | ECC Geral [IC 95%] | ECC Cond. | F1 Macro | Vaza resposta | Tempo (s) | ECE (juiz `qwen2.5:7b`) |
|:---|---:|---:|---:|---:|---:|---: |---:|
| *Chute majoritário (`erro_calculo`)* | 100.0% | **46.9%** [40.7–53.1%] | 46.9% | 0.091 | — | — | — |
| V1 (CH) · Qwen2.5 1.5B | 240/241 (99.6%) | **26.1%** [20.7–32.0%] | 26.2% | 0.091 | 7/240 (2.9%) | 0.58 | — |
| V2 (PT) · Qwen2.5 1.5B | 240/241 (99.6%) | **39.8%** [33.6–46.1%] | 40.0% | 0.153 | 5/240 (2.1%) | 0.58 | 2.5% [0.8–4.6%] |
| V1 (CH) · Gemma2 2B | 241/241 (100.0%) | **9.1%** [5.8–13.3%] | 9.1% | 0.063 | 0/241 (0.0%) | 0.75 | — |
| V2 (PT) · Gemma2 2B | 241/241 (100.0%) | **9.1%** [5.8–12.9%] | 9.1% | 0.107 | 2/241 (0.8%) | 0.71 | 3.7% [1.7–6.2%] |
| V1 (CH) · Qwen2.5-VL 3B (foto) | 240/241 (99.6%) | **46.5%** [40.2–52.7%] | 46.7% | 0.092 | 1/240 (0.4%) | 1.67 | — |
| V2 (PT) · Qwen2.5-VL 7B (foto) | 240/241 (99.6%) | **38.6%** [32.8–44.8%] | 38.8% | 0.114 | 1/240 (0.4%) | 3.00 | 6.2% [3.3–9.5%] |

### Distribuição das categorias previstas (colapso de classes)

| Condição | `erro_calculo` | `erro_compreensao` | `lacuna_conhecimento` | `erro_estrategia` | `erro_transcricao` | `erro_raciocinio` | `erro_atencao` | `sem_resposta` |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|
| `B1_texto_qwen25_1.5b` | 99 | 0 | 0 | 0 | 141 | 0 | 0 | 1 |
| `V2_FULL_B1_pt_qwen25_1.5b` | 164 | 20 | 0 | 0 | 55 | 0 | 1 | 1 |
| `B2_texto_gemma2_2b` | 4 | 158 | 0 | 42 | 8 | 29 | 0 | 0 |
| `V2_FULL_B2_pt_gemma2_2b` | 3 | 49 | 0 | 34 | 21 | 134 | 0 | 0 |
| `C1_visao_qwen25vl_3b` | 234 | 0 | 0 | 0 | 6 | 0 | 0 | 1 |
| `V2_FULL_C2_visao_pt_qwen25vl_7b` | 166 | 0 | 0 | 0 | 64 | 0 | 10 | 1 |