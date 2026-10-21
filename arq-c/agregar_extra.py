"""Resume os experimentos extras (ablação γ0=1 e ETTh1) e gera a tabela LaTeX do artigo (sections/tab_extra.tex)."""
import glob, re, statistics as st, json
OUT = "../../overleaf-relatorio/arq_p/sections/tab_extra.tex"
def ler(padrao):
    r = {}
    for f in sorted(glob.glob(padrao)):
        m = re.findall(r"mse:([\d.]+), mae:([\d.]+)", open(f).read())
        if m: r[int(re.search(r"_s?(\d{4})\.log", f).group(1))] = (float(m[-1][0]), float(m[-1][1]))
    return r
G = {"ETTh2 baseline": ler("logs/baseline_semente_*.log"), "ETTh2 modificado (ReZero, $\\gamma_0{=}0$)": ler("logs/modificado_semente_*.log"),
     "ETTh2 modificado sem ReZero ($\\gamma_0{=}1$)": ler("logs/extra_ETTh2_gamma1_s*.log"),
     "ETTh1 baseline": ler("logs/extra_ETTh1_baseline_s*.log"), "ETTh1 modificado (ReZero)": ler("logs/extra_ETTh1_modificado_s*.log")}
S3 = (2021, 2022, 2023)
def f(v, i):
    x = [t[i] for t in v]; sd = st.stdev(x) if len(x) > 1 else 0.0
    return f"${st.mean(x):.4f} \\pm {sd:.4f}$".replace(".", "{,}")
rows, js = [], {}
for k, d in G.items():
    v = [d[s] for s in S3 if s in d]            # mesmas sementes 2021-2023 em todas as linhas
    js[k] = {"n": len(v), "mse": [t[0] for t in v], "mae": [t[1] for t in v]}
    rows.append(f"{k} & {len(v)} & {f(v,0) if v else '---'} & {f(v,1) if v else '---'} \\\\")
paper = {"ETTh2": (0.263, 0.332), "ETTh1": (0.368, 0.394)}
tab = ("\\begin{tabular}{lccc}\n\\toprule\nConfiguração (sementes 2021--2023) & $n$ & MSE & MAE \\\\\n\\midrule\n" + "\n".join(rows[:3]) +
       f"\n\\midrule\n" + "\n".join(rows[3:]) + "\n\\bottomrule\n\\end{tabular}\n")
open(OUT, "w").write(tab); json.dump(js, open("reports_extra_treinos.json", "w"), indent=1, ensure_ascii=False); print(tab); print(json.dumps(js, indent=1))
