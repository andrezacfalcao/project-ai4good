# Checklist para os slides

Guia do que capturar (print de tela) e onde colar em cada slide. Os prints
são pessoais — cada integrante roda os comandos na própria máquina/IDE e
tira o próprio print (ninguém consegue tirar isso por vocês).

## Onde tudo mora no repositório

```
project-ai4good/
├── README.md                                # visão geral do projeto
├── mlp_graph.py                             # motor da MLP-grafo (feedforward/backprop)
├── app_streamlit.py                         # app Streamlit (mesmo motor, interativo)
├── requirements.txt
├── data/
│   └── heart.csv                            # cópia local do dataset (fallback do kagglehub)
├── notebooks/
│   └── heart_disease_mlp_graph.ipynb        # notebook principal (todo o exercício)
├── reports/
│   ├── model_card.md                        # cartão de parâmetros (gerado pelo notebook)
│   └── model_card.json
└── docs/
    └── SLIDES_CHECKLIST.md                  # este arquivo
```

Todo `.md` do projeto fica em **`reports/`** (saídas geradas — cartão de
parâmetros) e **`docs/`** (documentação escrita à mão, como este checklist) —
além do `README.md` na raiz.

## Slide 1 — Setup (3 prints)

1. **Harness rodando**: print do terminal com o Claude Code (`claude`) em uso
   nesta sessão — ou, alternativamente, print de `jupyter nbconvert --execute
   notebooks/heart_disease_mlp_graph.ipynb` rodando no terminal.
2. **Estrutura de pastas**: print do explorer da sua IDE (ou saída de
   `tree -L 2` / `find . -not -path './.git*' -not -path './.venv*'` no
   terminal) mostrando a árvore acima — deixe visível onde ficam os `.md`
   (`README.md`, `reports/model_card.md`, `docs/SLIDES_CHECKLIST.md`).
3. **Git + Gitflow**: print de
   `git log --graph --oneline --all --decorate` (mostra `main`, `develop` e
   as branches `feature/*` mergeadas) e/ou `git branch -a`.

## Slide 2 — Cada integrante (3 prints)

Cada pessoa do grupo faz esses 3 prints **rodando o próprio notebook** (ou o
app Streamlit) na própria máquina:

1. **Código rodando**: célula de imports/setup executando sem erro (topo do
   notebook), ou `streamlit run app_streamlit.py` no terminal.
2. **Treinamento**: a saída ao vivo da Seção 9 (*Treinamento do modelo
   final*) — o grafo com pesos/ativações + as curvas de perda/acurácia sendo
   atualizadas (rode a célula interativamente no Jupyter/VS Code para
   capturar um frame no meio do treino, não só o último).
3. **Inferência**: a saída da Seção 11 (*Visualizando uma inferência em tempo
   real*) — o grafo com a propagação camada a camada de um paciente, com a
   predição final impressa.

## Slide 3 — Cartão de parâmetros (já preenchido)

Copie os campos de [`reports/model_card.md`](../reports/model_card.md)
(gerado pela Seção 12 do notebook) direto pro slide. Ele já vem com os
valores calculados — não precisa preencher nada, só copiar/formatar:

- `accuracy`, `precision`, `recall`, `f1_score`
- `learning_rate`, `l2_regularization`
- `activation`, `architecture`
- `weight_init`, `optimizer`, `batch_size`, `epochs`, `loss`
- `pre_processing`, `train_test_split`, `seed`
- `comentarios` (achados reais: efeito da padronização e da deduplicação)

## Slide 4 — Duplicar o Slide 3 para o próximo integrante

Copie o Slide 3 inteiro (mesmo layout/campos) e cole abaixo dele. Cada
integrante roda o notebook com sua própria seed/config (pode mudar
`DEFAULT_CONFIG` em `mlp_graph.py`, ou usar os sliders do
`app_streamlit.py`) e preenche os mesmos campos com os próprios números —
assim dá pra comparar resultados entre integrantes lado a lado.

Modelo em branco para copiar:

```
accuracy: ____
precision: ____
recall: ____
f1_score: ____
learning rate: ____
l2 (weight decay): ____
activation: ____
architecture: ____
weight init: ____
optimizer: ____
batch size: ____
epochs: ____
pre-processing: ____
comentários: ____
```
