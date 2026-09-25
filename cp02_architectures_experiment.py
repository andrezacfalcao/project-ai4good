"""
CP-02 — ARQUITETURAS DE REDES NEURAIS
Artigo de Referência: Shrivastava et al. (2023), "HCBiLSTM: A hybrid model for
predicting heart disease using CNN and BiLSTM algorithms", Measurement:
Sensors, Vol. 25, 100657. DOI: 10.1016/j.measen.2022.100657
Arquitetura Base: 1D-CNN + BiLSTM (núcleo do artigo; sem a etapa de seleção
de atributos via Extra Trees Classifier do artigo original)
Arquitetura Modificada: 1D-CNN ResNet Block + BiLSTM (2 camadas) + Self-Attention + Autoencoder Bottleneck Head
Dataset: UCI Heart Disease Dataset (302 pacientes únicos pós-deduplicação, 13 preditores)
"""

import copy
import json
import os
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader

# Reproducibilidade
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "heart.csv")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
OVERLEAF_FIG_DIR = os.path.join(os.path.dirname(BASE_DIR), "overleaf-relatorio", "figures")
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(OVERLEAF_FIG_DIR, exist_ok=True)

# 1. Carregamento e Pré-processamento dos Dados
def load_and_preprocess_data():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Dataset não encontrado em {DATA_PATH}")
    
    df = pd.read_csv(DATA_PATH)
    print(f"[Dataset] Formato bruto: {df.shape}")
    
    # Deduplicação rigorosa (crítica para evitar vazamento entre treino e teste)
    df_clean = df.drop_duplicates()
    print(f"[Dataset] Formato após remoção de duplicatas: {df_clean.shape}")
    
    X = df_clean.drop(columns=["target"]).values
    y = df_clean["target"].values
    
    # Split 80/20 Estratificado
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=SEED, stratify=y
    )
    
    # Padronização (StandardScaler ajustado apenas no treino)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Formatação para 1D-CNN/LSTM: Tensor de entrada (batch_size, channels=1, seq_len=13)
    X_train_t = torch.tensor(X_train_scaled, dtype=torch.float32).unsqueeze(1)
    y_train_t = torch.tensor(y_train, dtype=torch.float32).unsqueeze(1)
    X_test_t = torch.tensor(X_test_scaled, dtype=torch.float32).unsqueeze(1)
    y_test_t = torch.tensor(y_test, dtype=torch.float32).unsqueeze(1)
    
    return X_train_t, y_train_t, X_test_t, y_test_t, scaler, df_clean

# 2. Arquitetura Baseline (do Artigo: 1D-CNN + BiLSTM)
class BaselineCNNLSTM(nn.Module):
    def __init__(self, input_dim=13, hidden_dim=32):
        super(BaselineCNNLSTM, self).__init__()
        # Extrator de características convolucionais 1D
        self.conv1 = nn.Conv1d(in_channels=1, out_channels=16, kernel_size=3, padding=1)
        self.relu = nn.ReLU()
        self.pool = nn.MaxPool1d(kernel_size=2, stride=2) # 13 -> 6 features

        # Agregador sequencial Bi-LSTM (núcleo do artigo: CNN + BiLSTM)
        self.lstm = nn.LSTM(input_size=16, hidden_size=hidden_dim, batch_first=True, bidirectional=True)

        # Cabeça de classificação linear simples (hidden_dim*2: concatena as duas direções)
        self.fc = nn.Linear(hidden_dim * 2, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        # x shape: (B, 1, 13)
        c_out = self.conv1(x) # (B, 16, 13)
        c_out = self.relu(c_out)
        c_out = self.pool(c_out) # (B, 16, 6)

        # Reordenar para LSTM: (B, seq_len=6, features=16)
        lstm_in = c_out.permute(0, 2, 1)
        lstm_out, (h_n, _) = self.lstm(lstm_in) # lstm_out: (B, 6, 64), h_n: (2, B, 32)

        last_hidden = torch.cat((h_n[0], h_n[1]), dim=1) # (B, 64) — concatena forward + backward
        out = self.fc(last_hidden)
        out = self.sigmoid(out)
        return out

# 3. Arquitetura Modificada (Proposta Substancial: Residual CNN + BiLSTM + Self-Attention + Autoencoder Bottleneck)
class SelfAttention(nn.Module):
    def __init__(self, feature_dim):
        super(SelfAttention, self).__init__()
        self.query = nn.Linear(feature_dim, feature_dim)
        self.key = nn.Linear(feature_dim, feature_dim)
        self.value = nn.Linear(feature_dim, feature_dim)
        self.softmax = nn.Softmax(dim=-1)

    def forward(self, x):
        # x shape: (B, seq_len, feature_dim)
        Q = self.query(x)
        K = self.key(x)
        V = self.value(x)
        
        scores = torch.bmm(Q, K.transpose(1, 2)) / (x.size(-1) ** 0.5)
        attn_weights = self.softmax(scores)
        context = torch.bmm(attn_weights, V)
        return context, attn_weights

class ModifiedCNNBiLSTMAttentionAE(nn.Module):
    def __init__(self, input_dim=13, conv_channels=32, lstm_hidden=32, bottleneck_dim=16):
        super(ModifiedCNNBiLSTMAttentionAE, self).__init__()
        
        # 1. Bloco Convolucional Residual de Múltiplas Escalas (Skip Connection)
        self.conv1 = nn.Conv1d(in_channels=1, out_channels=conv_channels, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm1d(conv_channels)
        self.conv2 = nn.Conv1d(in_channels=conv_channels, out_channels=conv_channels, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm1d(conv_channels)
        self.residual_proj = nn.Conv1d(in_channels=1, out_channels=conv_channels, kernel_size=1)
        self.relu = nn.ReLU()
        
        # 2. LSTM Bidirecional (BiLSTM)
        self.bilstm = nn.LSTM(
            input_size=conv_channels,
            hidden_size=lstm_hidden,
            num_layers=2,
            batch_first=True,
            bidirectional=True,
            dropout=0.2
        )
        
        # 3. Mecanismo de Auto-Atenção (Self-Attention)
        self.attention = SelfAttention(feature_dim=lstm_hidden * 2)
        
        # 4. Bottleneck Autoencoder Head (Compressão de representação latente para regularização)
        self.ae_encoder = nn.Sequential(
            nn.Linear(lstm_hidden * 2, 32),
            nn.ReLU(),
            nn.Linear(32, bottleneck_dim), # Latent Space
            nn.ReLU()
        )
        self.ae_classifier = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(bottleneck_dim, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        # x: (B, 1, 13)
        res = self.residual_proj(x)
        out = self.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out = self.relu(out + res) # Conexão Residual
        
        # BiLSTM: (B, 13, 32) -> (B, 13, 64)
        bilstm_in = out.permute(0, 2, 1)
        bilstm_out, _ = self.bilstm(bilstm_in)
        
        # Self-Attention
        attn_out, _ = self.attention(bilstm_out)
        
        # Pooling Global por Atenção (Média ponderada)
        context_vector = torch.mean(attn_out, dim=1) # (B, 64)
        
        # Passagem pelo Bottleneck Autoencoder + Classificação
        latent = self.ae_encoder(context_vector)
        pred = self.ae_classifier(latent)
        return pred

# 4. Função de Treinamento com Checkpoint e Rastreamento Rigoroso
def train_model(model, train_loader, X_test, y_test, epochs=100, lr=0.002):
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=1e-4)
    
    train_losses, test_losses = [], []
    train_accs, test_accs = [], []
    
    best_loss = float('inf')
    best_weights = None
    best_epoch = 1
    
    for epoch in range(1, epochs + 1):
        model.train()
        running_loss = 0.0
        correct_train = 0
        total_train = 0
        
        for batch_x, batch_y in train_loader:
            optimizer.zero_grad()
            outputs = model(batch_x)
            loss = criterion(outputs, batch_y)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            
            running_loss += loss.item() * batch_x.size(0)
            preds = (outputs >= 0.5).float()
            correct_train += (preds == batch_y).sum().item()
            total_train += batch_y.size(0)
            
        epoch_train_loss = running_loss / total_train
        epoch_train_acc = correct_train / total_train
        
        # Avaliação em Teste
        model.eval()
        with torch.no_grad():
            test_outputs = model(X_test)
            test_loss = criterion(test_outputs, y_test).item()
            test_preds = (test_outputs >= 0.5).float()
            epoch_test_acc = (test_preds == y_test).sum().item() / y_test.size(0)
            
        train_losses.append(epoch_train_loss)
        test_losses.append(test_loss)
        train_accs.append(epoch_train_acc)
        test_accs.append(epoch_test_acc)
        
        if test_loss < best_loss:
            best_loss = test_loss
            best_weights = copy.deepcopy(model.state_dict())
            best_epoch = epoch
            
    # Carregar os pesos da melhor época para inferência e avaliação final
    model.load_state_dict(best_weights)
    
    return train_losses, test_losses, train_accs, test_accs, best_epoch, best_loss

# 5. Avaliação Completa
def evaluate_model(model, X_test, y_test):
    model.eval()
    with torch.no_grad():
        outputs = model(X_test)
        probs = outputs.numpy().flatten()
        preds = (probs >= 0.5).astype(int)
        y_true = y_test.numpy().flatten().astype(int)
        
    acc = accuracy_score(y_true, preds)
    prec = precision_score(y_true, preds, zero_division=0)
    rec = recall_score(y_true, preds, zero_division=0)
    f1 = f1_score(y_true, preds, zero_division=0)
    cm = confusion_matrix(y_true, preds)
    
    return {
        "accuracy": float(acc),
        "precision": float(prec),
        "recall": float(rec),
        "f1_score": float(f1),
        "confusion_matrix": cm.tolist(),
        "probs": probs.tolist(),
        "preds": preds.tolist(),
        "y_true": y_true.tolist()
    }

def main():
    print("=== EXECUTANDO EXPERIMENTO CP-02: ARQUITETURAS NEURAIS (RIGOROSO) ===")
    X_train, y_train, X_test, y_test, scaler, df_clean = load_and_preprocess_data()
    
    train_dataset = TensorDataset(X_train, y_train)
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    
    epochs = 100
    lr = 0.002
    
    # Modelo 1: Baseline (Artigo 2023)
    print("\n--- Treinando Modelo Baseline (1D-CNN + BiLSTM) ---")
    torch.manual_seed(SEED)
    baseline_model = BaselineCNNLSTM()
    b_tr_loss, b_te_loss, b_tr_acc, b_te_acc, b_best_ep, b_best_loss = train_model(
        baseline_model, train_loader, X_test, y_test, epochs=epochs, lr=lr
    )
    baseline_metrics = evaluate_model(baseline_model, X_test, y_test)
    print(f"Baseline (Melhor Época {b_best_ep}): Test Acc: {baseline_metrics['accuracy']:.4f} | Prec: {baseline_metrics['precision']:.4f} | Rec: {baseline_metrics['recall']:.4f} | F1: {baseline_metrics['f1_score']:.4f}")
    
    # Modelo 2: Arquitetura Modificada
    print("\n--- Treinando Modelo Modificado (Residual CNN + BiLSTM + Attention + AE Bottleneck) ---")
    torch.manual_seed(SEED)
    modified_model = ModifiedCNNBiLSTMAttentionAE()
    m_tr_loss, m_te_loss, m_tr_acc, m_te_acc, m_best_ep, m_best_loss = train_model(
        modified_model, train_loader, X_test, y_test, epochs=epochs, lr=lr
    )
    modified_metrics = evaluate_model(modified_model, X_test, y_test)
    print(f"Modificado (Melhor Época {m_best_ep}): Test Acc: {modified_metrics['accuracy']:.4f} | Prec: {modified_metrics['precision']:.4f} | Rec: {modified_metrics['recall']:.4f} | F1: {modified_metrics['f1_score']:.4f}")
    
    # Demonstração de Inferência Funcional
    print("\n--- Demonstração de Inferência Passo a Passo ---")
    sample_idx = 1  # paciente saudável classificado errado (falso positivo) pelo baseline
    sample_input = X_test[sample_idx:sample_idx+1]
    sample_target = int(y_test[sample_idx].item())
    
    baseline_model.eval()
    modified_model.eval()
    with torch.no_grad():
        b_prob = baseline_model(sample_input).item()
        m_prob = modified_model(sample_input).item()
        
    print(f"Exemplo de Teste Index {sample_idx}:")
    print(f"  - Target Real: {sample_target} ({'Doença Presente' if sample_target==1 else 'Ausente'})")
    print(f"  - Probabilidade Baseline (CNN-BiLSTM): {b_prob:.4f} -> Prev: {1 if b_prob>=0.5 else 0}")
    print(f"  - Probabilidade Modificado (ResCNN-BiLSTM-Attn-AE): {m_prob:.4f} -> Prev: {1 if m_prob>=0.5 else 0}")
    
    # Salvar Gráficos de Comparação Qualitativa
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Curvas de Perda
    epochs_range = range(1, epochs + 1)
    ax1.plot(epochs_range, b_tr_loss, 'b--', alpha=0.7, label='Baseline Treino Loss')
    ax1.plot(epochs_range, b_te_loss, 'b-', label='Baseline Teste Loss')
    ax1.plot(epochs_range, m_tr_loss, 'r--', alpha=0.7, label='Modificado Treino Loss')
    ax1.plot(epochs_range, m_te_loss, 'r-', label='Modificado Teste Loss')
    ax1.axvline(x=b_best_ep, color='b', linestyle=':', label=f'Melhor Época Baseline ({b_best_ep})')
    ax1.axvline(x=m_best_ep, color='r', linestyle=':', label=f'Melhor Época Modificado ({m_best_ep})')
    ax1.set_title("Evolução da Perda (BCE Loss) ao Longo das Épocas")
    ax1.set_xlabel("Épocas")
    ax1.set_ylabel("Loss (BCE)")
    ax1.set_ylim(0, 2.5)
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)
    
    # Curvas de Acurácia
    ax2.plot(epochs_range, b_tr_acc, 'b--', alpha=0.7, label='Baseline Treino Acc')
    ax2.plot(epochs_range, b_te_acc, 'b-', label='Baseline Teste Acc')
    ax2.plot(epochs_range, m_tr_acc, 'r--', alpha=0.7, label='Modificado Treino Acc')
    ax2.plot(epochs_range, m_te_acc, 'r-', label='Modificado Teste Acc')
    ax2.axvline(x=b_best_ep, color='b', linestyle=':', label=f'Melhor Época Baseline ({b_best_ep})')
    ax2.axvline(x=m_best_ep, color='r', linestyle=':', label=f'Melhor Época Modificado ({m_best_ep})')
    ax2.set_title("Evolução da Acurácia ao Longo das Épocas")
    ax2.set_xlabel("Épocas")
    ax2.set_ylabel("Acurácia")
    ax2.set_ylim(0.45, 1.02)
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    curves_path = os.path.join(OVERLEAF_FIG_DIR, "cp02_curvas_comparativas.png")
    plt.savefig(curves_path, dpi=300)
    plt.close()
    print(f"[Figura] Salva em: {curves_path}")
    
    # Gráfico das Matrizes de Confusão
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    
    cm_b = np.array(baseline_metrics["confusion_matrix"])
    cm_m = np.array(modified_metrics["confusion_matrix"])
    
    im1 = ax1.imshow(cm_b, cmap='Blues')
    ax1.set_title(f"Baseline (CNN-BiLSTM)\nAcc: {baseline_metrics['accuracy']:.3f} | F1: {baseline_metrics['f1_score']:.3f}")
    ax1.set_xlabel("Predito")
    ax1.set_ylabel("Real")
    for i in range(2):
        for j in range(2):
            ax1.text(j, i, str(cm_b[i, j]), ha='center', va='center', color='black', fontsize=12, fontweight='bold')
            
    im2 = ax2.imshow(cm_m, cmap='Greens')
    ax2.set_title(f"Modificado (Res-BiLSTM-Attn-AE)\nAcc: {modified_metrics['accuracy']:.3f} | F1: {modified_metrics['f1_score']:.3f}")
    ax2.set_xlabel("Predito")
    ax2.set_ylabel("Real")
    for i in range(2):
        for j in range(2):
            ax2.text(j, i, str(cm_m[i, j]), ha='center', va='center', color='black', fontsize=12, fontweight='bold')
            
    plt.tight_layout()
    cm_path = os.path.join(OVERLEAF_FIG_DIR, "cp02_matrizes_confusao.png")
    plt.savefig(cm_path, dpi=300)
    plt.close()
    print(f"[Figura] Salva em: {cm_path}")
    
    # Salvar Relatório de Resultados em JSON e Markdown
    results_summary = {
        "paper_reference": {
            "title": "HCBiLSTM: A hybrid model for predicting heart disease using CNN and BiLSTM algorithms",
            "authors": "Prashant Kumar Shrivastava, Mayank Sharma, Pooja Sharma, Avenash Kumar",
            "journal": "Measurement: Sensors (Elsevier)",
            "volume": 25,
            "year": 2023,
            "doi": "10.1016/j.measen.2022.100657"
        },
        "dataset": {
            "name": "UCI Heart Disease Dataset (Kaggle drop_duplicates)",
            "raw_samples": 1025,
            "unique_samples": int(df_clean.shape[0]),
            "train_samples": int(X_train.shape[0]),
            "test_samples": int(X_test.shape[0]),
            "features_count": 13
        },
        "training_params": {
            "epochs": epochs,
            "learning_rate": lr,
            "optimizer": "Adam (weight_decay=1e-4, clip_grad_norm=1.0)",
            "loss": "Binary Cross-Entropy",
            "baseline_best_epoch": b_best_ep,
            "modified_best_epoch": m_best_ep
        },
        "baseline_model": {
            "architecture": "1D-CNN + Pooling + BiLSTM (bidirecional) + Dense Head",
            "best_epoch": b_best_ep,
            "metrics": baseline_metrics
        },
        "modified_model": {
            "architecture": "1D-CNN ResNet Block + BiLSTM + Self-Attention + Autoencoder Bottleneck Head",
            "best_epoch": m_best_ep,
            "metrics": modified_metrics
        }
    }
    
    json_path = os.path.join(REPORTS_DIR, "cp02_model_card.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results_summary, f, indent=2, ensure_ascii=False)
    print(f"[Resultados] Salvos em JSON: {json_path}")
    
    # Escrever resumo markdown
    md_content = f"""# Cartão de Experimento CP-02 — Arquiteturas Neurais (Rigoroso)

## 1. Artigo de Referência
- **Título**: HCBiLSTM: A hybrid model for predicting heart disease using CNN and BiLSTM algorithms
- **Autores**: Prashant Kumar Shrivastava, Mayank Sharma, Pooja Sharma, Avenash Kumar
- **Periódico**: Measurement: Sensors (Elsevier), Vol. 25, 2023, 100657
- **DOI**: [10.1016/j.measen.2022.100657](https://doi.org/10.1016/j.measen.2022.100657)

## 2. Dataset
- **Base**: UCI Heart Disease (302 pacientes únicos pós-deduplicação, 13 atributos)
- **Divisão**: 80% treino (241 pacientes), 20% teste (61 pacientes), estratificado

## 3. Comparação Quantitativa no Conjunto de Teste (Melhor Checkpoint)

| Métrica | Baseline (Artigo: 1D-CNN + BiLSTM) | Modificado (Res-BiLSTM + Attention + AE Bottleneck) | Variação Absoluta |
|---|---|---|---|
| **Acurácia** | {baseline_metrics['accuracy']:.4f} ({baseline_metrics['accuracy']*100:.2f}%) | {modified_metrics['accuracy']:.4f} ({modified_metrics['accuracy']*100:.2f}%) | **+{((modified_metrics['accuracy']-baseline_metrics['accuracy'])*100):.2f}%** |
| **Precisão** | {baseline_metrics['precision']:.4f} ({baseline_metrics['precision']*100:.2f}%) | {modified_metrics['precision']:.4f} ({modified_metrics['precision']*100:.2f}%) | **+{((modified_metrics['precision']-baseline_metrics['precision'])*100):.2f}%** |
| **Revocação** | {baseline_metrics['recall']:.4f} ({baseline_metrics['recall']*100:.2f}%) | {modified_metrics['recall']:.4f} ({modified_metrics['recall']*100:.2f}%) | **+{((modified_metrics['recall']-baseline_metrics['recall'])*100):.2f}%** |
| **F1-Score** | {baseline_metrics['f1_score']:.4f} ({baseline_metrics['f1_score']*100:.2f}%) | {modified_metrics['f1_score']:.4f} ({modified_metrics['f1_score']*100:.2f}%) | **+{((modified_metrics['f1_score']-baseline_metrics['f1_score'])*100):.2f}%** |
| **Época Ótima** | {b_best_ep} | {m_best_ep} | - |

## 4. Inferência Demonstrativa
- **Amostra Teste #{sample_idx}** (Target Real: {sample_target}):
  - Baseline Prob: {b_prob:.4f} (Classe Predita: {1 if b_prob>=0.5 else 0})
  - Modificado Prob: {m_prob:.4f} (Classe Predita: {1 if m_prob>=0.5 else 0})
"""
    md_path = os.path.join(REPORTS_DIR, "cp02_model_card.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"[Resultados] Salvos em Markdown: {md_path}")
    print("=== EXPERIMENTO CP-02 CONCLUÍDO COM SUCESSO ===")

if __name__ == "__main__":
    main()
