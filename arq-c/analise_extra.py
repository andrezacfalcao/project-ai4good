"""Análises extras do artigo (sem treino): deslocamento entre partições, baselines simples, decomposição
nível × forma do erro, relação erro × deslocamento de nível por janela e teste pareado entre sementes."""
import glob, json, os
import numpy as np, pandas as pd
from scipy import stats
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
VARS, SEEDS, L, H, N = ["HUFL", "HULL", "MUFL", "MULL", "LUFL", "LULL", "OT"], range(2021, 2026), 336, 96, 2560
FIG = "../../overleaf-relatorio/arq_p/figures"
raw = pd.read_csv("data/ETT-small/ETTh2.csv").iloc[:14400, 1:].values
mu, sd = raw[:8640].mean(0), raw[:8640].std(0); Z = (raw - mu) / sd          # padronização do treino (a do artigo)
B = {"treino": (0, 8640), "validação": (8640, 11520), "teste": (11520, 14400)}
res = {"deslocamento": {k: {"media": Z[a:b].mean(0).round(3).tolist(), "desvio": Z[a:b].std(0).round(3).tolist()} for k, (a, b) in B.items()}}

def windows(a, b):  # janelas (lookback 336 -> horizonte 96) cujo lookback começa em a-... como no código oficial
    n = b - a - L - H + 1
    return np.stack([Z[a + i:a + i + L] for i in range(n)]), np.stack([Z[a + i + L:a + i + L + H] for i in range(n)])
Xtr, Ytr = windows(0, 8640)
t0 = 11520 - L
Xte, Yte = windows(t0, 14400); Xte, Yte = Xte[:N], Yte[:N]
assert len(Xtr) == 8209

# baselines simples (mesmas 2.560 janelas, escala padronizada)
mse = lambda p: float(((p - Yte) ** 2).mean()); mae = lambda p: float(np.abs(p - Yte).mean())
last = np.repeat(Xte[:, -1:, :], H, axis=1)
seas = np.tile(Xte[:, -24:, :], (1, H // 24, 1))
A = Xtr.transpose(0, 2, 1).reshape(-1, L); Y = Ytr.transpose(0, 2, 1).reshape(-1, H)   # canal-independente (como DLinear)
A1 = np.c_[A, np.ones(len(A))]; W = np.linalg.solve(A1.T @ A1 + 10 * np.eye(L + 1), A1.T @ Y)
lin = (np.c_[Xte.transpose(0, 2, 1).reshape(-1, L), np.ones(N * 7)] @ W).reshape(N, 7, H).transpose(0, 2, 1)
res["baselines_simples"] = {n: {"mse": mse(p), "mae": mae(p)} for n, p in [("repetir último valor", last), ("sazonal ingênuo (24 h)", seas), ("regressão linear (ridge)", lin)]}

# previsões dos modelos (média das sementes e por semente)
P = {k: np.stack([np.load(glob.glob(f"{d}/results/*Exp_s{s}_0/pred.npy")[0]) for s in SEEDS]) for k, d in [("baseline", "moderntcn_oficial"), ("modificado", "moderntcn_mod")]}
P = {k: v for k, v in P.items()}
for k, v in P.items(): assert v.shape[1:] == (N, H, 7)
# nesse repositório os pred.npy do modificado ficam em moderntcn_mod/results/*attn_ModernTCN* (sem o γ=1 da ablação)
res["mse_por_semente"] = {k: [float(((v[i] - Yte) ** 2).mean()) for i in range(5)] for k, v in P.items()}
d = np.array(res["mse_por_semente"]["modificado"]) - np.array(res["mse_por_semente"]["baseline"])
res["pareado_5_sementes"] = {"dif_media": float(d.mean()), "t_pareado_p": float(stats.ttest_rel(res["mse_por_semente"]["modificado"], res["mse_por_semente"]["baseline"]).pvalue),
                              "wilcoxon_p": float(stats.wilcoxon(res["mse_por_semente"]["modificado"], res["mse_por_semente"]["baseline"]).pvalue), "d_cohen_pareado": float(d.mean() / d.std(ddof=1))}
Pm = {k: v.mean(0) for k, v in P.items()}                       # média das sementes [N,H,7]
E = {k: v - Yte for k, v in Pm.items()}
# decomposição do erro por janela e variável: nível (média sobre o horizonte) + forma (resto)
dec = {}
for k, e in E.items():
    lvl = e.mean(1, keepdims=True); shape = e - lvl
    dec[k] = {"mse_total": float((e ** 2).mean()), "nivel": float((lvl ** 2).mean()), "forma": float((shape ** 2).mean())}
    dec[k]["frac_nivel"] = dec[k]["nivel"] / dec[k]["mse_total"]
res["decomposicao"] = dec
w = (E["baseline"] ** 2).mean((1, 2)); top = np.argsort(w)[::-1][:100]; rest = np.setdiff1d(np.arange(N), top)
res["decomposicao_piores_4pct"] = {g: {k: float(((E[k][idx].mean(1)) ** 2).mean() / (E[k][idx] ** 2).mean()) for k in E} for g, idx in [("piores100", top), ("demais", rest)]}
# erro × deslocamento de nível entre lookback e horizonte (o que um modelo com RevIN não consegue prever)
shift2 = ((Yte.mean(1) - Xte.mean(1)) ** 2).mean(1)             # [N]
rho = stats.spearmanr(w, shift2)
res["erro_vs_deslocamento"] = {"spearman": float(rho.statistic), "p": float(rho.pvalue), "r2_linear": float(np.corrcoef(w, shift2)[0, 1] ** 2),
                               "shift2_piores100": float(shift2[top].mean()), "shift2_demais": float(shift2[rest].mean())}
json.dump(res, open("reports_extra.json", "w"), indent=1, ensure_ascii=False); print(json.dumps(res, indent=1, ensure_ascii=False))

plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(1, 3, figsize=(11, 3.1))
x = np.arange(7)
for o, (k, c) in enumerate([("treino", "#718096"), ("validação", "#dd6b20"), ("teste", "#2b6cb0")]):
    ax[0].bar(x + (o - 1) * .27, res["deslocamento"][k]["media"], .27, color=c, label=k)
ax[0].set_xticks(x, VARS, fontsize=7); ax[0].axhline(0, color="k", lw=.6); ax[0].set_ylabel("média (em σ do treino)"); ax[0].legend(fontsize=7, frameon=False); ax[0].set_title("(a) deslocamento entre partições", fontsize=9)
ax[1].scatter(shift2, w, s=5, alpha=.35, color="#2b6cb0"); ax[1].scatter(shift2[top], w[top], s=7, color="#c53030", label="100 piores janelas")
ax[1].set_xlabel("deslocamento de nível² (horizonte − entrada)"); ax[1].set_ylabel("MSE da janela (baseline)"); ax[1].legend(fontsize=7, frameon=False)
ax[1].set_title(f"(b) erro × deslocamento (Spearman {rho.statistic:.2f})", fontsize=9)
f = [dec["baseline"]["frac_nivel"], dec["modificado"]["frac_nivel"]]
g = [res["decomposicao_piores_4pct"]["piores100"]["baseline"], res["decomposicao_piores_4pct"]["demais"]["baseline"]]
ax[2].bar(["todas", "100 piores", "demais"], [f[0], g[0], g[1]], color=["#718096", "#c53030", "#2b6cb0"])
for i, v in enumerate([f[0], g[0], g[1]]): ax[2].text(i, v + .01, f"{v:.0%}", ha="center", fontsize=8)
ax[2].set_ylim(0, 1); ax[2].set_ylabel("fração do MSE que é erro de nível"); ax[2].set_title("(c) nível × forma (baseline)", fontsize=9)
fig.tight_layout(); fig.savefig(f"{FIG}/cp02_diagnostico_regime.png", dpi=200)
