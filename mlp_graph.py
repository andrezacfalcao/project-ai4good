"""
mlp_graph.py — MLP implementada como grafo (networkx), com feedforward e
backpropagation manuais em numpy. Usado tanto pelo notebook
(notebooks/heart_disease_mlp_graph.ipynb) quanto pelo app Streamlit
(app_streamlit.py), para que os dois usem exatamente o mesmo código/engine —
sem duplicação e sem risco de os resultados divergirem entre os dois.

Representação: cada neurônio é um nó (`LxNy` = neurônio y da camada x) e cada
conexão sináptica é uma aresta com atributo `weight`. Os parâmetros treináveis
moram nas arestas (pesos) e nos nós (bias) do grafo; a cada passo de
gradiente eles são extraídos para matrizes numpy (rápido para treinar em
lote) e escritos de volta no grafo.
"""

import numpy as np
import networkx as nx

# ---------------------------------------------------------------------------
# Configuração padrão (única fonte de verdade dos hiperparâmetros usados no
# modelo final — o notebook e o app Streamlit particem daqui).
# ---------------------------------------------------------------------------
DEFAULT_CONFIG = {
    "architecture": [13, 8, 5, 1],   # 13 features de entrada -> 8 -> 5 -> 1 (saída)
    "hidden_activation": "relu",
    "output_activation": "sigmoid",
    "weight_init": "he_normal",
    "loss": "binary_cross_entropy",
    "learning_rate": 0.05,
    "l2": 0.1,
    "epochs": 300,
    "batch_size": 32,
    "optimizer": "mini-batch gradient descent",
    "preprocessing": "standardize (StandardScaler, fit no treino)",
    "seed": 42,
}


# ---------------------------------------------------------------------------
# Funções de ativação / perda
# ---------------------------------------------------------------------------
def relu(z):
    return np.maximum(0.0, z)


def relu_deriv(z):
    return (z > 0).astype(z.dtype if isinstance(z, np.ndarray) else float)


def sigmoid(z):
    z = np.clip(z, -500, 500)
    return 1.0 / (1.0 + np.exp(-z))


def bce_loss(y_true, y_pred, eps=1e-8):
    y_pred = np.clip(y_pred, eps, 1 - eps)
    return -np.mean(y_true * np.log(y_pred) + (1 - y_true) * np.log(1 - y_pred))


def accuracy(y_true, y_pred_proba):
    return float(np.mean((y_pred_proba >= 0.5).astype(int) == y_true))


# ---------------------------------------------------------------------------
# Grafo <-> parâmetros
# ---------------------------------------------------------------------------
def build_graph(layer_sizes, seed=42):
    """Cria o grafo da MLP: nós = neurônios, arestas = pesos."""
    rng = np.random.default_rng(seed)
    G = nx.DiGraph()
    for l, size in enumerate(layer_sizes):
        for i in range(size):
            G.add_node(
                f"L{l}N{i}", layer=l, a=0.0, z=0.0,
                bias=0.0 if l == 0 else float(rng.normal(0, 0.1)),
            )
    for l in range(len(layer_sizes) - 1):
        fan_in = layer_sizes[l]
        scale = np.sqrt(2.0 / fan_in)  # inicialização He (boa para ReLU)
        for i in range(layer_sizes[l]):
            for j in range(layer_sizes[l + 1]):
                G.add_edge(f"L{l}N{i}", f"L{l+1}N{j}", weight=float(rng.normal(0, scale)))
    return G


def graph_to_params(G, layer_sizes):
    """Extrai (W, b) de cada camada a partir das arestas/nós do grafo."""
    params = []
    for l in range(len(layer_sizes) - 1):
        n_in, n_out = layer_sizes[l], layer_sizes[l + 1]
        W = np.zeros((n_in, n_out))
        b = np.zeros(n_out)
        for j in range(n_out):
            vnode = f"L{l+1}N{j}"
            b[j] = G.nodes[vnode]["bias"]
            for i in range(n_in):
                W[i, j] = G[f"L{l}N{i}"][vnode]["weight"]
        params.append({"W": W, "b": b})
    return params


def params_to_graph(G, layer_sizes, params):
    """Escreve (W, b) de volta nas arestas/nós do grafo (pós-atualização de gradiente)."""
    for l, p in enumerate(params):
        n_in, n_out = layer_sizes[l], layer_sizes[l + 1]
        for j in range(n_out):
            vnode = f"L{l+1}N{j}"
            G.nodes[vnode]["bias"] = float(p["b"][j])
            for i in range(n_in):
                G[f"L{l}N{i}"][vnode]["weight"] = float(p["W"][i, j])


def sync_activations(G, layer_sizes, activations):
    """Grava um vetor de ativações (uma amostra) nos nós do grafo, para plot."""
    for l, a in enumerate(activations):
        for i in range(layer_sizes[l]):
            G.nodes[f"L{l}N{i}"]["a"] = float(a[i])


def copy_params(params):
    return [{"W": p["W"].copy(), "b": p["b"].copy()} for p in params]


# ---------------------------------------------------------------------------
# Feedforward — duas implementações (percurso literal no grafo vs. vetorizada)
# ---------------------------------------------------------------------------
def feedforward_graph_single(G, layer_sizes, x):
    """Feedforward literal: percorre o grafo nó a nó / aresta a aresta, em
    ordem topológica. Mais lento, mas mostra a propagação diretamente sobre
    a estrutura do grafo. Usado só para validar a versão vetorizada."""
    for i in range(layer_sizes[0]):
        G.nodes[f"L0N{i}"]["a"] = float(x[i])

    L_out = len(layer_sizes) - 1
    for node in nx.topological_sort(G):
        layer = G.nodes[node]["layer"]
        if layer == 0:
            continue
        z = G.nodes[node]["bias"]
        for pred in G.predecessors(node):
            z += G.nodes[pred]["a"] * G[pred][node]["weight"]
        G.nodes[node]["z"] = z
        G.nodes[node]["a"] = sigmoid(z) if layer == L_out else relu(z)

    return np.array([G.nodes[f"L{L_out}N{j}"]["a"] for j in range(layer_sizes[L_out])])


def feedforward(X, params):
    """Feedforward vetorizado (usado no treino), com os pesos extraídos do grafo."""
    A = X
    caches = [A]
    zs = []
    L = len(params)
    for l, p in enumerate(params):
        Z = A @ p["W"] + p["b"]
        zs.append(Z)
        A = sigmoid(Z) if l == L - 1 else relu(Z)
        caches.append(A)
    return caches, zs


def backward(y, caches, zs, params, l2=0.0):
    """Backpropagation: gradientes de cada camada via regra da cadeia.
    `l2` adiciona weight decay (regularização L2) ao gradiente dos pesos:
    dW += (l2/m) * W  <=>  perda += (l2/(2m)) * sum(W**2).
    """
    m = y.shape[0]
    L = len(params)
    grads = [None] * L
    dZ = caches[-1] - y  # gradiente combinado sigmoid + entropia cruzada binária
    for l in reversed(range(L)):
        A_prev = caches[l]
        dW = A_prev.T @ dZ / m + (l2 / m) * params[l]["W"]
        db = np.mean(dZ, axis=0)
        grads[l] = {"dW": dW, "db": db}
        if l > 0:
            dA_prev = dZ @ params[l]["W"].T
            dZ = dA_prev * relu_deriv(zs[l - 1])
    return grads


def update_params(params, grads, lr):
    for p, g in zip(params, grads):
        p["W"] -= lr * g["dW"]
        p["b"] -= lr * g["db"]


# ---------------------------------------------------------------------------
# Visualização (compartilhada pelo notebook e pelo Streamlit)
# ---------------------------------------------------------------------------
COLOR_TRAIN = "#2a78d6"   # azul  -> sempre "treino"
COLOR_TEST = "#eb6834"    # laranja -> sempre "teste"/"validação"
COLOR_POS_W = "#2a78d6"   # azul  -> peso positivo (par divergente)
COLOR_NEG_W = "#e34948"   # vermelho -> peso negativo (par divergente)
COLOR_MID_W = "#f0efec"   # cinza neutro -> peso ~ 0
INK = "#0b0b0b"
MUTED = "#8a8880"


def edge_colors_widths(G):
    from matplotlib.colors import LinearSegmentedColormap
    weights = np.array([G[u][v]["weight"] for u, v in G.edges()])
    max_abs = max(np.max(np.abs(weights)), 1e-9) if len(weights) else 1.0
    norm = weights / max_abs  # em [-1, 1]
    cmap = LinearSegmentedColormap.from_list("diverging_w", [COLOR_NEG_W, COLOR_MID_W, COLOR_POS_W])
    colors = [cmap((n + 1) / 2) for n in norm]
    widths = 0.6 + 3.0 * np.abs(norm)
    return colors, widths


def draw_graph_panel(ax, G, pos, title):
    colors, widths = edge_colors_widths(G)
    node_colors = [G.nodes[n]["a"] for n in G.nodes()]
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color=colors, width=widths, arrows=False)
    nx.draw_networkx_nodes(
        G, pos, ax=ax, node_color=node_colors, cmap="Blues", vmin=0, vmax=1,
        node_size=220, edgecolors=INK, linewidths=0.4,
    )
    ax.set_title(title, fontsize=10)
    ax.axis("off")


# ---------------------------------------------------------------------------
# Classe GraphMLP
# ---------------------------------------------------------------------------
class GraphMLP:
    def __init__(self, layer_sizes, seed=42):
        self.layer_sizes = layer_sizes
        self.G = build_graph(layer_sizes, seed=seed)
        self.params = graph_to_params(self.G, layer_sizes)
        self.pos = nx.multipartite_layout(self.G, subset_key="layer")

    def forward(self, X):
        return feedforward(X, self.params)

    def predict_proba(self, X):
        caches, _ = self.forward(X)
        return caches[-1]

    def predict(self, X):
        return (self.predict_proba(X) >= 0.5).astype(int)

    def train(self, X_train, y_train, X_val, y_val, epochs=300, lr=0.05,
              batch_size=32, l2=0.0, early_stopping=False, patience=25,
              min_delta=1e-4, restore_best=True, seed=42,
              visualize_every=None, on_epoch=None):
        """Treina com mini-batch gradient descent.

        - `l2`: força da regularização L2 (weight decay).
        - `early_stopping`: para o treino se `val_loss` não melhorar por
          `patience` épocas seguidas, e restaura os pesos da melhor época
          (`restore_best=True`).
        - `on_epoch(epoch, epochs, history, model)`: callback opcional,
          chamado a cada época (usado pelo notebook e pelo Streamlit para
          desenhar o grafo/curvas "em tempo real" sem este módulo depender
          de matplotlib/IPython/Streamlit diretamente).
        """
        rng = np.random.default_rng(seed)
        n = X_train.shape[0]
        history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}

        best_val_loss = np.inf
        best_params = None
        best_epoch = 0
        no_improve = 0
        epoch = 0

        for epoch in range(1, epochs + 1):
            idx = rng.permutation(n)
            X_shuf, y_shuf = X_train[idx], y_train[idx]
            for start in range(0, n, batch_size):
                xb = X_shuf[start:start + batch_size]
                yb = y_shuf[start:start + batch_size]
                caches, zs = feedforward(xb, self.params)
                grads = backward(yb, caches, zs, self.params, l2=l2)
                update_params(self.params, grads, lr)

            # sincroniza os pesos atualizados de volta no grafo (fonte de verdade)
            params_to_graph(self.G, self.layer_sizes, self.params)

            train_pred = self.predict_proba(X_train)
            val_pred = self.predict_proba(X_val)
            history["train_loss"].append(bce_loss(y_train, train_pred))
            history["val_loss"].append(bce_loss(y_val, val_pred))
            history["train_acc"].append(accuracy(y_train, train_pred))
            history["val_acc"].append(accuracy(y_val, val_pred))

            if early_stopping:
                if history["val_loss"][-1] < best_val_loss - min_delta:
                    best_val_loss = history["val_loss"][-1]
                    best_params = copy_params(self.params)
                    best_epoch = epoch
                    no_improve = 0
                else:
                    no_improve += 1

            if on_epoch is not None and (
                visualize_every is None or epoch % visualize_every == 0 or epoch == epochs
            ):
                on_epoch(epoch, epochs, history, self)

            if early_stopping and no_improve >= patience:
                break

        history["best_epoch"] = best_epoch if early_stopping else epoch
        history["stopped_epoch"] = epoch

        if early_stopping and restore_best and best_params is not None:
            self.params = best_params
            params_to_graph(self.G, self.layer_sizes, self.params)
            if on_epoch is not None:
                on_epoch(epoch, epochs, history, self)

        return history
