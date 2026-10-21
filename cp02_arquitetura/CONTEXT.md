# CONTEXT · cp02_arquitetura

Artefatos **[5] arquitetura git repo** (`arq·c`) e **tech report** (`arq·p`): reprodução
de uma rede da literatura e modificação arquitetural, com re-treino e métricas comparadas.
O relatório LaTeX está em `../../overleaf-relatorio/arq_p/report-arch.tex`.

## itens da atividade (`arq·c`) e onde está a evidência

| item | onde |
|:--|:--|
| 1. subrepositório com `CONTEXT.md` | esta pasta e este arquivo |
| 2. dataset do artigo | `data/ETT-small/` (ETTh2, baixada do repositório público ETDataset) |
| 3. inferência funcional | `moderntcn_oficial/results/*/pred.npy` (previsões do teste) e as janelas de `analise_qualitativa.py` |
| 4. baseline *as-is* | `rodar_baseline.sh` + `logs/baseline_semente_*.log`: 0,2645 de MSE vs 0,263 do artigo |
| 5. modificação arquitetural | classe `PatchAttention` em `moderntcn_mod/models/ModernTCN.py`, marcada com `[MODIFICAÇÃO CP02]`; mudanças exatas em [`moderntcn_mod/DIFF_vs_oficial.patch`](moderntcn_mod/DIFF_vs_oficial.patch); re-treino em `logs/modificado_semente_*.log` |

## artigo base

Luo, D.; Wang, X. **ModernTCN: A Modern Pure Convolution Structure for General Time
Series Analysis.** ICLR 2024. PDF: [`paper_moderntcn.pdf`](paper_moderntcn.pdf).
Código oficial (MIT): <https://github.com/luodhhh/ModernTCN>.

Uma CNN pura para séries temporais: divide cada variável em patches, usa convolução
*depthwise* de kernel grande (51, com ramo de kernel 5 reparametrizável) e duas ConvFFN
(uma por variável, outra entre variáveis), com normalização RevIN.

**Por que este artigo:** ≥ 2023, CNN, código aberto com scripts de todos os hiperparâmetros,
base pública pequena (ETT) e treina em ~20 s por época na GPU de um Mac. Uma tentativa
anterior com o HCBiLSTM (2023) foi descartada por não publicar código.

## dados e tarefa

- **Base:** ETTh2, 17.420 medições horárias de 7 variáveis (HUFL, HULL, MUFL, MULL, LUFL,
  LULL, OT), baixada de <https://github.com/zhouhaoyi/ETDataset> para `data/ETT-small/`.
- **Tarefa:** prever 96 h a partir das 336 h anteriores (multivariado).
- **Partição:** cronológica 6:2:2 (8.209 treino / 2.785 validação / 2.785 teste), dados
  padronizados com média e desvio do treino. Métricas: MSE e MAE nos dados padronizados.
- O código oficial testa com `drop_last`: as métricas usam 2.560 das 2.785 janelas.

## as duas redes

| | baseline (oficial) | modificada |
|:--|:--|:--|
| código | [`moderntcn_oficial/`](moderntcn_oficial) | [`moderntcn_mod/`](moderntcn_mod) |
| arquitetura | ModernTCN, 1 estágio, 1 bloco, 64 canais | idêntica + atenção sobre patches |
| parâmetros | 659.844 | 681.989 (+3,4%) |
| flag | `--use_attn 0` | `--use_attn 1` |

**Modificação** (detalhes em [`moderntcn_mod/MODIFICACAO.md`](moderntcn_mod/MODIFICACAO.md)):
`x ← x + γ · MHA(LN(x) + posição)` após o bloco, com `γ` aprendido e inicializado em 0
(ReZero). Hipótese: filtros convolucionais são fixos, e a atenção pondera o passado
conforme a entrada. Com `γ = 0` o modelo é idêntico ao oficial (`testar_modificacao.py`).

**Treino (igual nas duas):** Adam 1e-4, lote 512, até 100 épocas, parada antecipada com
paciência 20, sementes 2021 a 2025.

## resultados (ETTh2, horizonte 96, 5 sementes)

| | artigo | reproduzido | modificado |
|:--|:--|:--|:--|
| MSE | 0,263 | 0,2645 ± 0,0006 | 0,2654 ± 0,0007 |
| MAE | 0,332 | 0,3331 ± 0,0004 | 0,3337 ± 0,0007 |

- **Reprodução:** feita; diferença de 0,0015 de MSE para o artigo.
- **Modificação:** *não melhora*. Piora 0,0009 de MSE, vence em 39,9% das janelas, e o
  ganho aprendido `γ` fica em ~0,02 (a rede quase ignora a atenção).
- **Análise** (`analise_qualitativa.py`, `reports_analise.json`): os dois modelos acertam
  o ciclo diário e erram o *nível*; 4% das janelas concentram o erro, e nelas os dois são iguais.
  Hipótese (não testada): mudança de regime entre treino e teste.

## limitações

- Uma base (ETTh2) e um horizonte (96); a modificação tem um único desenho.
- Os intervalos por janela são otimistas (as janelas se sobrepõem).
- O artigo não informa o desvio entre sementes dele.
- Ajustes no código oficial, só de compatibilidade: ver `moderntcn_oficial/ORIGEM.txt`.

## arquivos

```
cp02_arquitetura/
├── CONTEXT.md
├── paper_moderntcn.pdf             # artigo base
├── moderntcn_oficial/              # código oficial (commit 56a9a2c), baseline as-is
├── moderntcn_mod/                  # cópia com a modificação (+ MODIFICACAO.md e DIFF_vs_oficial.patch)
├── data/ETT-small/                 # ETTh1.csv, ETTh2.csv (ignorados pelo git)
├── logs/                           # 1 log por semente e modelo (10)
├── rodar_baseline.sh / rodar_modificado.sh   # uma semente: sh rodar_baseline.sh 2021
├── rodar_5_sementes.sh / rodar_5_sementes_mod.sh
├── agregar_resultados.py           # média ± desvio dos logs vs. artigo
├── analise_qualitativa.py          # por variável, passo e janela; gera as figuras
├── testar_modificacao.py           # γ=0 reproduz o oficial
├── reports_analise.json
└── apresentacao/                   # slides (cp02_slides.pptx, com notas), FALA_APRESENTACAO.md e criar_slides.js
```

## como rodar

Da pasta `cp02_arquitetura`, com o `.venv` da raiz (precisa de `torch`, `einops`, `matplotlib`):

```bash
sh rodar_5_sementes.sh         # baseline, 5 sementes (~1 h na GPU do Mac)
sh rodar_5_sementes_mod.sh     # modificado, 5 sementes
python agregar_resultados.py
python analise_qualitativa.py  # figuras em ../../overleaf-relatorio/arq_p/figures/
```

`moderntcn_*/checkpoints` e `results` são gerados pelo treino e não vão para o git.
