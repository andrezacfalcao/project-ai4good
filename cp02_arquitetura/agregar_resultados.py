"""Lê logs/*.log e resume MSE/MAE por semente (média ± desvio) contra o valor reportado no artigo."""
import glob, re, statistics as st
PAPER = {"mse": 0.263, "mae": 0.332}   # ModernTCN, ETTh2, horizonte 96 (Tabela 27 do artigo)
def ler(prefixo):
    out = []
    for f in sorted(glob.glob(f"logs/{prefixo}_semente_*.log")):
        t = open(f).read(); m = re.findall(r"mse:([\d.]+), mae:([\d.]+)", t)
        if m: out.append((f.split("_")[-1][:-4], float(m[-1][0]), float(m[-1][1]), len(re.findall(r"^Epoch: \d+ cost", t, re.M))))
    return out
for nome in ("baseline", "modificado"):
    r = ler(nome)
    if not r: continue
    for s, mse, mae, ep in r: print(f"{nome:10s} semente {s}: MSE {mse:.4f}  MAE {mae:.4f}  ({ep} épocas)")
    mse, mae = [x[1] for x in r], [x[2] for x in r]
    sd = lambda v: st.stdev(v) if len(v) > 1 else 0.0
    print(f"{nome:10s} média de {len(r)}: MSE {st.mean(mse):.4f} ± {sd(mse):.4f} | MAE {st.mean(mae):.4f} ± {sd(mae):.4f}\n")
print(f"artigo (reportado): MSE {PAPER['mse']} | MAE {PAPER['mae']}")
