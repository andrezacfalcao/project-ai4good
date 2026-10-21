"""Análise por variável, por passo do horizonte e por janela: baseline oficial vs modificado (5 sementes)."""
import glob, os, sys, json
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, "moderntcn_oficial")
from data_provider.data_loader import Dataset_ETT_hour

SEEDS, VARS = range(2021, 2026), ["HUFL", "HULL", "MUFL", "MULL", "LUFL", "LULL", "OT"]
FIG = "../../overleaf-relatorio/arq_p/figures"; os.makedirs(FIG, exist_ok=True)
ds = Dataset_ETT_hour("data/ETT-small", flag="test", size=[336, 48, 96], features="M", data_path="ETTh2.csv", timeenc=1, freq="h")
N = 2560  # o código oficial testa com drop_last: 5 lotes de 512 das 2.785 janelas
truth = np.stack([ds[i][1][-96:] for i in range(N)])          # [N,96,7], escala padronizada (a do artigo)
dates = pd.read_csv("data/ETT-small/ETTh2.csv")["date"].values[11520:11520 + N]  # início de cada janela prevista
def preds(pasta, tag):
    return np.stack([np.load(glob.glob(f"{pasta}/results/*Exp_s{s}_0/pred.npy")[0]) for s in SEEDS])  # [5,N,96,7]
P = {"baseline": preds("moderntcn_oficial", ""), "modificado": preds("moderntcn_mod", "")}
E = {k: (v - truth[None]) ** 2 for k, v in P.items()}                # erro quadrático [5,N,96,7]

res = {"n_janelas": N}
# 1) por variável
var = {k: E[k].mean(axis=(1, 2)) for k in E}                         # [5,N?]... média por semente e variável
var = {k: E[k].mean(axis=(1, 2)) for k in E}
res["mse_por_variavel"] = {v: {k: [float(var[k][:, j].mean()), float(var[k][:, j].std())] for k in E} for j, v in enumerate(VARS)}
# 2) por passo do horizonte (média de semente/janela/variável)
step = {k: E[k].mean(axis=(0, 1, 3)) for k in E}
res["mse_passo_1_24_48_72_96"] = {k: [float(step[k][i]) for i in (0, 23, 47, 71, 95)] for k in E}
# 3) por janela, média das sementes: quem erra menos?
w = {k: E[k].mean(axis=(0, 2, 3)) for k in E}
d = w["modificado"] - w["baseline"]
res["janelas_mod_melhor_pct"] = float((d < 0).mean() * 100)
rng = np.random.default_rng(0); b = [d[rng.integers(0, len(d), len(d))].mean() for _ in range(2000)]
res["dif_mse_mod_menos_base"] = [float(d.mean()), float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]
# 4) janelas mais difíceis (maior erro do baseline) e onde a modificação mais ajuda/atrapalha
top = np.argsort(w["baseline"])[::-1][:100]
res["mse_100_piores_janelas"] = {k: float(w[k][top].mean()) for k in w}
res["mse_demais_janelas"] = {k: float(np.delete(w[k], top).mean()) for k in w}
idx = {"mais_ajuda": int(np.argmin(d)), "mais_atrapalha": int(np.argmax(d)), "pior_baseline": int(top[0])}
res["janelas_exemplo"] = {n: {"indice": i, "inicio": str(dates[i]), "mse_baseline": float(w["baseline"][i]), "mse_modificado": float(w["modificado"][i])} for n, i in idx.items()}
json.dump(res, open("reports_analise.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps(res, indent=1, ensure_ascii=False))

# figuras
fig, ax = plt.subplots(figsize=(7, 3.2)); x = np.arange(7)
for o, k in enumerate(E):
    ax.bar(x + (o - .5) * .38, var[k].mean(0), .38, yerr=var[k].std(0), label=k, capsize=2)
ax.set_xticks(x, VARS); ax.set_ylabel("MSE (teste, 5 sementes)"); ax.legend(); fig.tight_layout(); fig.savefig(f"{FIG}/cp02_mse_por_variavel.png", dpi=200)
fig, axs = plt.subplots(1, 3, figsize=(11, 3.1))
for a, (n, i) in zip(axs, idx.items()):
    a.plot(truth[i, :, 6], "k", lw=1.6, label="real")
    for k, c in (("baseline", "tab:blue"), ("modificado", "tab:red")): a.plot(P[k][:, i, :, 6].mean(0), c, lw=1.2, label=k)
    a.set_title(f"{n.replace('_', ' ')}\n{str(dates[i])[:10]}", fontsize=9); a.set_xlabel("passo (h)")
axs[0].set_ylabel("OT (padronizado)"); axs[0].legend(fontsize=7); fig.tight_layout(); fig.savefig(f"{FIG}/cp02_janelas_exemplo.png", dpi=200)
