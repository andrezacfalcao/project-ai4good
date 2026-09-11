"""
App Streamlit para inspecionar a MLP-grafo em ação: treina ao vivo na base
Heart Disease e redesenha o grafo (pesos das arestas, ativações dos nós) e as
curvas de treino a cada N épocas, além de mostrar as métricas finais e uma
inferência passo a passo.

Rodar com:
    streamlit run app_streamlit.py
"""

import os
import time

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, confusion_matrix,
    ConfusionMatrixDisplay,
)

from mlp_graph import (
    DEFAULT_CONFIG, GraphMLP, feedforward, draw_graph_panel, edge_colors_widths,
    sync_activations, COLOR_TRAIN, COLOR_TEST, INK, MUTED,
)

st.set_page_config(page_title="MLP-Grafo — Heart Disease", layout="wide")

plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white", "axes.edgecolor": MUTED,
    "axes.grid": True, "grid.color": "#e7e6e1", "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False, "font.size": 10,
})

st.title("MLP a partir de um grafo — Heart Disease")
st.caption(
    "Rede neural implementada do zero (numpy + networkx): neurônios são nós, "
    "pesos são arestas. Ajuste os hiperparâmetros na barra lateral e treine "
    "para ver o grafo e as curvas atualizando em tempo real."
)


# ---------------------------------------------------------------------------
# Dados (cache para não recarregar/recalcular a cada interação)
# ---------------------------------------------------------------------------
@st.cache_data
def load_data():
    data_path = os.path.join(os.path.dirname(__file__), "data", "heart.csv")
    csv_path = None
    try:
        import kagglehub
        kaggle_dir = kagglehub.dataset_download("johnsmith88/heart-disease-dataset")
        candidate = os.path.join(kaggle_dir, "heart.csv")
        if os.path.exists(candidate):
            csv_path = candidate
    except Exception:
        pass
    if csv_path is None:
        csv_path = data_path
    df = pd.read_csv(csv_path)
    n_before = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    return df, n_before


df, n_before = load_data()
feature_cols = [c for c in df.columns if c != "target"]

with st.sidebar:
    st.header("Dados")
    st.write(f"{n_before} linhas originais → **{len(df)}** pacientes únicos "
             f"({n_before - len(df)} duplicatas removidas).")
    test_size = st.slider("Proporção de teste", 0.1, 0.4, 0.20, 0.05)
    standardize = st.checkbox("Padronizar features (StandardScaler)", value=True)
    seed = st.number_input("Seed", value=DEFAULT_CONFIG["seed"], step=1)

    st.header("Arquitetura")
    hidden_str = st.text_input("Camadas ocultas (separadas por vírgula)", "8, 5")
    hidden_sizes = [int(x.strip()) for x in hidden_str.split(",") if x.strip()]

    st.header("Otimização")
    lr = st.number_input("Learning rate", value=DEFAULT_CONFIG["learning_rate"],
                          min_value=0.0001, max_value=1.0, step=0.01, format="%.4f")
    l2 = st.number_input("Regularização L2", value=DEFAULT_CONFIG["l2"],
                          min_value=0.0, max_value=2.0, step=0.01, format="%.3f")
    epochs = st.slider("Épocas", 10, 1000, DEFAULT_CONFIG["epochs"], 10)
    batch_size = st.slider("Batch size", 4, 128, DEFAULT_CONFIG["batch_size"], 4)
    early_stopping = st.checkbox("Early stopping", value=False)
    patience = st.slider("Paciência (early stopping)", 5, 100, 25, 5, disabled=not early_stopping)
    visualize_every = st.slider("Redesenhar a cada N épocas", 1, 50, 10)

    train_clicked = st.button("Treinar", type="primary", use_container_width=True)


X = df[feature_cols].values.astype(np.float64)
y = df["target"].values.astype(np.float64).reshape(-1, 1)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=test_size, random_state=int(seed), stratify=y
)
if standardize:
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

layer_sizes = [X_train.shape[1]] + hidden_sizes + [1]

col_info, col_arch = st.columns([1, 2])
with col_info:
    st.metric("Treino", len(X_train))
    st.metric("Teste", len(X_test))
with col_arch:
    st.write("**Arquitetura:** " + " → ".join(str(n) for n in layer_sizes))
    st.write(f"**Total de pesos (arestas):** "
             f"{sum(layer_sizes[i] * layer_sizes[i+1] for i in range(len(layer_sizes)-1))}")


# ---------------------------------------------------------------------------
# Treino ao vivo
# ---------------------------------------------------------------------------
graph_slot = st.empty()
curves_slot = st.empty()
status_slot = st.empty()

if "model" not in st.session_state:
    st.session_state.model = None
    st.session_state.history = None
    st.session_state.config = None

if train_clicked:
    model = GraphMLP(layer_sizes, seed=int(seed))

    def on_epoch(epoch, total_epochs, history, m):
        sample_caches, _ = m.forward(X_train[:1])
        sync_activations(m.G, m.layer_sizes, [c[0] for c in sample_caches])

        fig1, ax = plt.subplots(figsize=(5, 4.5))
        draw_graph_panel(ax, m.G, m.pos, f"Época {epoch}/{total_epochs}")
        graph_slot.pyplot(fig1, clear_figure=True)

        fig2, (ax_loss, ax_acc) = plt.subplots(1, 2, figsize=(9, 3.2))
        ep_range = range(1, len(history["train_loss"]) + 1)
        ax_loss.plot(ep_range, history["train_loss"], color=COLOR_TRAIN, label="Treino")
        ax_loss.plot(ep_range, history["val_loss"], color=COLOR_TEST, label="Teste")
        ax_loss.set_title("Perda (BCE)")
        ax_loss.legend(frameon=False)
        ax_acc.plot(ep_range, history["train_acc"], color=COLOR_TRAIN, label="Treino")
        ax_acc.plot(ep_range, history["val_acc"], color=COLOR_TEST, label="Teste")
        ax_acc.set_title("Acurácia")
        ax_acc.set_ylim(0, 1.02)
        ax_acc.legend(frameon=False)
        plt.tight_layout()
        curves_slot.pyplot(fig2, clear_figure=True)

        status_slot.text(
            f"Época {epoch}/{total_epochs} — "
            f"loss treino={history['train_loss'][-1]:.4f} | "
            f"loss teste={history['val_loss'][-1]:.4f} | "
            f"acc treino={history['train_acc'][-1]:.3f} | "
            f"acc teste={history['val_acc'][-1]:.3f}"
        )

    with st.spinner("Treinando..."):
        history = model.train(
            X_train, y_train, X_test, y_test,
            epochs=epochs, lr=lr, batch_size=batch_size, l2=l2,
            early_stopping=early_stopping, patience=patience,
            seed=int(seed), visualize_every=visualize_every, on_epoch=on_epoch,
        )

    st.session_state.model = model
    st.session_state.history = history
    st.session_state.config = {
        "architecture": " | ".join(str(n) for n in layer_sizes),
        "hidden_activation": "relu",
        "output_activation": "sigmoid",
        "weight_init": "he_normal",
        "loss": "binary_cross_entropy",
        "learning_rate": lr,
        "l2": l2,
        "epochs": epochs,
        "stopped_epoch": history["stopped_epoch"],
        "best_epoch": history["best_epoch"],
        "batch_size": batch_size,
        "optimizer": "mini-batch gradient descent",
        "preprocessing": "standardize (StandardScaler)" if standardize else "nenhum (dados brutos)",
        "seed": int(seed),
    }
    if early_stopping and history["stopped_epoch"] < epochs:
        st.info(f"Early stopping acionado na época {history['stopped_epoch']} "
                f"(melhor época: {history['best_epoch']}).")


# ---------------------------------------------------------------------------
# Resultados / cartão de parâmetros (formato pronto para colar num slide)
# ---------------------------------------------------------------------------
if st.session_state.model is not None:
    model = st.session_state.model
    cfg = st.session_state.config

    st.divider()
    st.subheader("Avaliação no conjunto de teste")

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Acurácia", f"{acc:.3f}")
    m2.metric("Precisão", f"{prec:.3f}")
    m3.metric("Revocação", f"{rec:.3f}")
    m4.metric("F1-score", f"{f1:.3f}")

    col_cm, col_card = st.columns(2)
    with col_cm:
        cm = confusion_matrix(y_test, y_pred)
        fig, ax = plt.subplots(figsize=(3.8, 3.8))
        ConfusionMatrixDisplay(cm, display_labels=["Ausência", "Presença"]).plot(
            ax=ax, cmap="Blues", colorbar=False)
        ax.grid(False)
        st.pyplot(fig, clear_figure=True)

    with col_card:
        st.markdown("**Parâmetros usados (para o slide):**")
        st.code(
            f"accuracy: {acc:.3f}\n"
            f"precision: {prec:.3f}\n"
            f"recall: {rec:.3f}\n"
            f"f1-score: {f1:.3f}\n"
            f"learning rate: {cfg['learning_rate']}\n"
            f"l2 (weight decay): {cfg['l2']}\n"
            f"activation: {cfg['hidden_activation']} (oculta) / {cfg['output_activation']} (saída)\n"
            f"architecture: {cfg['architecture']}\n"
            f"weight init: {cfg['weight_init']}\n"
            f"optimizer: {cfg['optimizer']}\n"
            f"batch size: {cfg['batch_size']}\n"
            f"epochs (rodadas/parada): {cfg['epochs']} (parou em {cfg['stopped_epoch']})\n"
            f"pre-processing: {cfg['preprocessing']}\n"
            f"seed: {cfg['seed']}",
            language="yaml",
        )

    st.divider()
    st.subheader("Inferência passo a passo")
    idx = st.slider("Paciente do conjunto de teste", 0, len(X_test) - 1, 0)
    reach_layer = st.slider("Propagar até a camada", 0, len(layer_sizes) - 1, len(layer_sizes) - 1)

    caches, _ = model.forward(X_test[idx:idx + 1])
    activations = [c[0] for c in caches]
    colors, widths = edge_colors_widths(model.G)

    node_colors, edgecolors = [], []
    for node in model.G.nodes():
        layer = model.G.nodes[node]["layer"]
        node_idx = int(node.split("N")[1])
        reached = layer <= reach_layer
        node_colors.append(activations[layer][node_idx] if reached else 0.0)
        edgecolors.append(INK if reached else MUTED)

    import networkx as nx
    fig, ax = plt.subplots(figsize=(5, 4.5))
    nx.draw_networkx_edges(model.G, model.pos, ax=ax, edge_color=colors, width=widths, arrows=False)
    nx.draw_networkx_nodes(
        model.G, model.pos, ax=ax, node_color=node_colors, cmap="Blues", vmin=0, vmax=1,
        node_size=280, edgecolors=edgecolors, linewidths=1.0,
    )
    ax.set_title(f"Propagação até a camada {reach_layer} de {len(layer_sizes) - 1}")
    ax.axis("off")
    st.pyplot(fig, clear_figure=True)

    pred_proba = float(activations[-1][0])
    pred_label = int(pred_proba >= 0.5)
    true_label = int(y_test[idx, 0])
    st.write(f"Predição: **classe {pred_label}** (probabilidade = {pred_proba:.3f}) "
             f"| Classe real: **{true_label}** "
             f"{'✅' if pred_label == true_label else '❌'}")
else:
    st.info("Ajuste os hiperparâmetros na barra lateral e clique em **Treinar**.")
