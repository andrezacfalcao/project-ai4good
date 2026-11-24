# Plano V2 · Escopo, OCR Manuscrito e Tradução (`ScratchMath`)

Documento de planejamento técnico do próximo ciclo do experimento **Atlas do Erro** sobre o benchmark `songdj/ScratchMath` (`middle`, 241 folhas reais, Song et al., AIED 2026).

---

## 1. Definição de Escopo (baseada na auditoria real das 241 folhas)

A auditoria automática de `dados/middle.jsonl` mostrou a composição real do split `middle`:

| Subconjunto temático | Qtd | % das 241 | Compatível com `SymPy` atual (1º grau em `x`)? |
|:---|---:|---:|:---|
| **Equações do 1º grau** | **57** | **23,7%** | **Sim — escopo nativo do Atlas** |
| Inequações | 60 | 24,9% | Não (exige solver de desigualdades) |
| Equações do 2º grau | 40 | 16,6% | Parcial (múltiplas raízes) |
| Sistemas de equações | 19 | 7,9% | Não (2+ incógnitas) |
| Outros (geometria, funções, problemas textuais) | 65 | 27,0% | Não |

Distribuição das classes GT dentro das **57 equações do 1º grau**:
- `erro_calculo`: 32 (56,1%) · `erro_transcricao`: 8 (14,0%) · `erro_atencao`: 8 (14,0%) · `lacuna_conhecimento`: 5 (8,8%) · `erro_estrategia`: 3 (5,3%) · `erro_raciocinio`: 1 (1,8%).

### Recorte recomendado (reportado em 2 níveis transparentes)
1. **Recorte Principal — Escopo do Atlas (`N = 57` equações do 1º grau):** testa a pipeline completa (`Foto → OCR Matemático → SymPy → Regra / Qwen / Gemma`) no exato tipo de problema para o qual o Atlas foi projetado (7º ano).
2. **Recorte Completo — Benchmark do Artigo (`N = 241`):** mantém comparabilidade direta com a tabela publicada de Song et al. (AIED 2026), mostrando o comportamento das LLMs e do VLM no dataset inteiro.

---

## 2. Escolha do Modelo de OCR para o Passo 1

| Opção | Tipo | Pontos fortes | Limitações | Recomendação |
|:---|:---|:---|:---|:---|
| **`Qwen2.5-VL 7B` (ou `3B`) como transcritor puro** | VLM local no Ollama (Apache-2.0) | Lê rascunho inteiro em 2D sem recorte horizontal; entende frações, sinais, rabiscos e devolve lista de equações limpa para o `SymPy`; roda na RTX 5070 (12 GB) | Mais pesado que OCR clássico (~3,2–6 GB VRAM); exige prompt estrito de transcrição literal (sem corrigir o erro do aluno!) | **Escolha principal (V2)** |
| **`Pix2Text` (MFR + Layout) / `UniMERNet`** | Pipeline OCR matemático dedicado (MIT/Apache-2.0) | Leve, roda até em CPU, gera LaTeX de fórmulas | Sofre com rascunhos livres, traços encostados e rabiscos fora de linha | **Alternativa leve / ablação** |
| **`TrOCR-base-handwritten`** | Encoder-decoder linha a linha (MIT) | Melhor que `printed` para texto cursivo | Não foi treinado em álgebra/frações e ainda depende de recorte por linhas | **Descartado** |

### Regra de ouro do Passo 1 (VLM-como-OCR)
O modelo de visão **NÃO diagnostica nem corrige** — ele apenas transcreve literalmente cada equação manuscrita na ordem em que o aluno escreveu (JSON `{"linhas": ["...", "..."]}`), preservando os erros do aluno para que o **SymPy** (Passo 2) encontre a quebra de forma determinística.

---

## 3. Como implementar o Pipeline V2 (passo a passo)

1. **Etapa 1 — Filtrar e congelar o subconjunto de escopo (`N = 57`):**
   - Salvar `dados/escopo_1grau.jsonl` (com os índices exatos das 57 equações do 1º grau) sem alterar `middle.jsonl`.
2. **Etapa 2 — Camada de tradução PT-BR com cache (`dados/middle_pt.jsonl`):**
   - Traduzir `question`, `solution` e `error_explanation` de chinês → português **uma única vez**, preservando intactas todas as expressões LaTeX (`$...$`).
   - O **GT não é criado pela API**: ele já vem pronto no dataset (`error_category` + `error_explanation` dos 5 professores); a API apenas traduz o texto para remover o viés de idioma e permitir auditoria humana em português.
3. **Etapa 3 — Novo Passo 1 (Transcrição manuscrita) + Passo 2 (`SymPy` com suporte a frações):**
   - Rodar `Qwen2.5-VL 7B` (ou `3B`) exclusivamente para transcrever `student_scratchwork` em lista de equações (`linhas_vlm`).
   - Adaptar `regra.py` para aceitar frações simples (`\frac{a}{b}` → `(a)/(b)`) antes do `SymPy`, mantendo a verificação determinística.
   - Medir a **nova cobertura do SymPy** (quantas das 57 equações do 1º grau passam de `0%` para `quebra` legível!).
4. **Etapa 4 — Comparação justa no Passo 3 (agora com transcrição legível e texto em PT-BR):**
   - Sobre as mesmas folhas legíveis, rodar lado a lado:
     - `Regra das correções típicas` (sem IA)
     - `qwen2.5:1.5b` (e opcionalmente `qwen2.5:7b` como teto local)
     - `gemma2:2b`
   - E sobre as 241 folhas traduzidas em PT-BR, reavaliar `B1`, `B2` e `C1` para isolar quanto do erro anterior vinha do idioma chinês.
5. **Etapa 5 — Avaliação completa e atualização dos resultados:**
   - Métricas: Cobertura do OCR+SymPy, ECC geral e condicional (IC 95% bootstrap), F1 Macro, ECE (com juiz consistente), taxa de vazamento de resposta e inspeção qualitativa de 10 casos reais.

---

## 4. Tradução e API da OpenAI: precisa mesmo?

- **O GT já existe:** não estamos criando gabarito; estamos apenas **traduzindo** os textos em chinês (`question`, `solution`, `error_explanation`) do `ScratchMath` para português.
- **Opção A — API da OpenAI (`gpt-4o-mini`):**
  - Tradução de alta fidelidade preservando LaTeX (~US$ 0,05 para todas as 241 amostras) + possibilidade de usar `gpt-4o-mini` também como **juiz ECE** (mais próximo do protocolo do artigo).
  - Requer apenas colocar `OPENAI_API_KEY=...` em um `.env` local (fora do Git).
- **Opção B — 100% local com `qwen2.5:7b` (custo zero):**
  - O `qwen2.5:7b` já está baixado na RTX 5070 e é muito forte em chinês → português; traduz as 241 amostras em ~2–3 minutos sem API externa.
  - Desvantagem: qualidade de tradução ligeiramente menor que `gpt-4o-mini` em problemas textuais longos e não serve como referência independente externa para o juiz ECE.
