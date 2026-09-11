# MLP a partir de uma estrutura de grafo — Heart Disease

Implementação de uma rede neural Multi-Layer Perceptron (MLP) **do zero**
(sem frameworks de deep learning), representando a arquitetura como um grafo
dirigido (`networkx.DiGraph`): neurônios são nós, pesos são atributos de
aresta. Inclui feedforward, backpropagation, treino/inferência na base
*Heart Disease* (80/20), visualização em tempo real do grafo/pesos, escolha
de hiperparâmetros por validação cruzada e um app Streamlit para inspecionar
tudo interativamente.

## Estrutura do projeto

```
project-ai4good/
├── mlp_graph.py                          # motor da MLP-grafo (feedforward/backprop/L2/early stopping)
├── app_streamlit.py                      # app Streamlit — mesmo motor, interativo (streamlit run app_streamlit.py)
├── requirements.txt
├── data/heart.csv                        # cópia local do dataset (fallback do kagglehub)
├── notebooks/heart_disease_mlp_graph.ipynb  # notebook principal (todo o exercício)
├── reports/                              # saídas geradas pelo notebook
│   ├── model_card.md                     # cartão de parâmetros — pronto para colar num slide
│   └── model_card.json
└── docs/
    └── SLIDES_CHECKLIST.md               # checklist de prints/slides para a apresentação
```

## Notebook

- [`notebooks/heart_disease_mlp_graph.ipynb`](notebooks/heart_disease_mlp_graph.ipynb) — dados → grafo → feedforward/backprop → padronização (evidência real) → validação cruzada → treino final → inferência → cartão de parâmetros.

## App Streamlit

```bash
streamlit run app_streamlit.py
```

Sliders para arquitetura, learning rate, L2, épocas, batch size,
padronização e early stopping; treina com um clique e mostra o grafo e as
curvas atualizando em tempo real, métricas finais, matriz de confusão, o
cartão de parâmetros e uma inferência passo a passo.

## Dados

O dataset (`johnsmith88/heart-disease-dataset` no Kaggle) é baixado
automaticamente via `kagglehub` (não exige login/token para datasets
públicos). Uma cópia local está incluída em `data/heart.csv` como fallback.

> Nota: essa versão do dataset contém muitas linhas duplicadas (1025 linhas,
> apenas 302 pacientes únicos) — o notebook remove as duplicatas antes do
> split para evitar vazamento de dados entre treino e teste.

## Como rodar

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter lab notebooks/heart_disease_mlp_graph.ipynb
```

Execute as células em ordem. As visualizações "em tempo real" (grafo e curvas
de treinamento sendo atualizados a cada época) usam
`IPython.display.clear_output` e são melhor apreciadas rodando interativamente
(Jupyter/VS Code, ou o app Streamlit); ao exportar estaticamente, apenas o
último quadro fica salvo no arquivo.

## Apresentação / slides

Veja [`docs/SLIDES_CHECKLIST.md`](docs/SLIDES_CHECKLIST.md) para o roteiro de
prints (harness, estrutura de pastas, git/gitflow, código/treino/inferência
de cada integrante) e como preencher o cartão de parâmetros no slide.
