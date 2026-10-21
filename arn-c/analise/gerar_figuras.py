"""Gera as figuras do artigo (../../overleaf-relatorio/arn_p/figures) e analise/dados/metricas.json.
Uso (da pasta arn-c): ../.venv/bin/python analise/gerar_figuras.py   (ablação: rode antes experimento_ablacao.py)"""
import json, glob, re, difflib, itertools, statistics as st, collections
from datetime import datetime as D
from pathlib import Path
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
ARN = Path(__file__).resolve().parent.parent; OUT = ARN / "../../overleaf-relatorio/arn_p/figures"; OUT.mkdir(parents=True, exist_ok=True)
R = [json.load(open(f)) for f in sorted(glob.glob(str(ARN / "resultados/ultima_execucao/rodadas/*.json")))]
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 150})
BLUE, ORG, GRY, RED, GRN, PUR = "#2b6cb0", "#dd6b20", "#718096", "#c53030", "#2f855a", "#805ad5"
def save(fig, n): fig.savefig(OUT / f"{n}.pdf", bbox_inches="tight"); plt.close(fig)
M, x = {}, np.arange(1, 21)
KS = ("local_opening", "local_reply")

# ---------- fluxo
fig, ax = plt.subplots(figsize=(7.4, 3.3)); ax.axis("off"); ax.set_xlim(-0.5, 10); ax.set_ylim(-0.6, 4.1)
def box(x_, y, w, h, t, c, fs=8):
    ax.add_patch(FancyBboxPatch((x_, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.12", fc=c, ec="none"))
    ax.text(x_ + w/2, y + h/2, t, ha="center", va="center", color="white", fontsize=fs)
def arr(a, b, txt=""):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=9, color="#2d3748", connectionstyle="arc3,rad=0"))
    if txt: ax.text((a[0]+b[0])/2, (a[1]+b[1])/2 + .15, txt, fontsize=6.5, ha="center")
box(0.1, 2.9, 1.9, 0.9, "T1 Trabalhista\n(abertura)\nremoto", BLUE); box(2.5, 2.9, 1.9, 0.9, "T1 Liberal\nrisco + pergunta\nQwen local", ORG)
box(4.9, 2.9, 1.9, 0.9, "T2 Liberal\nnovo foco\nQwen local", ORG); box(7.3, 2.9, 2.5, 0.9, "T2 Trabalhista\n(defesa às falas\nreais do Qwen)", BLUE)
box(7.3, 1.5, 2.5, 0.9, "Juiz (remoto)\nveredito · plano\npendência · memória", GRN)
box(2.5, 1.5, 4.3, 0.9, "Filtros do Liberal\n(até 3 tentativas)\nJSON · eco · similaridade · tema", RED, 7.5)
box(0.1, 1.5, 1.9, 0.9, "Pesquisador\nGoogle Search\n(protocolo 6)", PUR); box(3.6, 0.0, 2.3, 0.8, "Memória curta\n(rodada n → n+1)", GRY)
for a_, b_ in [((2.0, 3.35), (2.5, 3.35)), ((4.4, 3.35), (4.9, 3.35)), ((6.8, 3.35), (7.3, 3.35)), ((8.55, 2.9), (8.55, 2.4)), ((3.45, 2.4), (3.45, 2.9)), ((5.85, 2.4), (5.85, 2.9)), ((1.05, 2.4), (1.05, 2.9))]: arr(a_, b_)
ax.add_patch(FancyArrowPatch((8.55, 1.5), (5.9, 0.4), arrowstyle="-|>", mutation_scale=9, color="#2d3748", connectionstyle="arc3,rad=.15")); ax.text(7.6, .75, "gera", fontsize=6.5)
ax.plot([3.6, -.3, -.3], [.4, .4, 3.35], color="#2d3748", lw=1); arr((-.3, 3.35), (0.1, 3.35)); ax.text(1.5, .5, "injeta", fontsize=6.5)
ax.text(5, -0.35, "20 rodadas · cada rodada = 4 falas + 1 parecer · execução sequencial (cada fala depende da anterior)", ha="center", fontsize=7.5, color="#2d3748")
save(fig, "fig_fluxo")

# ---------- métricas operacionais (latência de parede e contadores do Ollama)
att = {(r["round"], k): len(r[k]["attempts"]) for r in R for k in KS}; acc = {(r["round"], k): r[k]["accepted"] for r in R for k in KS}
lat, reasons, ev, pe, evd, ped, load = [], collections.Counter(), [], [], [], [], []
for r in R:
    for k in KS:
        for a in r[k]["attempts"]:
            lat.append((D.fromisoformat(a["finished"]) - D.fromisoformat(a["started"])).total_seconds())
            rr = a["raw_response"]; ev.append(rr["eval_count"]); pe.append(rr["prompt_eval_count"])
            evd.append(rr["eval_duration"] / 1e9); ped.append(rr["prompt_eval_duration"] / 1e9); load.append(rr["load_duration"] / 1e9)
            for z in a["quality"].get("reasons", []):
                reasons["tema" if "tema" in z else "cópia do prompt" if "45%" in z else "similaridade" if "85%" in z else z[:20]] += 1
M["lat"] = dict(n=len(lat), mean=st.mean(lat), median=st.median(lat), max=max(lat), min=min(lat), sd=st.pstdev(lat), total=sum(lat))
M["tokens"] = dict(prompt_mean=st.mean(pe), prompt_total=sum(pe), gen_mean=st.mean(ev), gen_total=sum(ev), tok_s=sum(ev) / sum(evd), prefill_tok_s=sum(pe) / sum(ped), load_total=sum(load))
M["reasons"] = dict(reasons); M["accepted"] = sum(acc.values()); M["att_total"] = sum(att.values())
M["wall_s"] = (D.fromisoformat(R[-1]["created_at"]) - D.fromisoformat(R[0]["created_at"])).total_seconds()

fig, ax = plt.subplots(1, 2, figsize=(7.4, 2.9), gridspec_kw={"width_ratios": [1.7, 1]}); w = .38
for i, (k, c, l) in enumerate([("local_opening", BLUE, "Turno 1 (abertura)"), ("local_reply", ORG, "Turno 2 (réplica)")]):
    ys = [att[(n, k)] for n in x]; ax[0].bar(x + (i-.5)*w, ys, w, color=c, label=l)
    for n, y in zip(x, ys):
        if not acc[(n, k)]: ax[0].plot(n + (i-.5)*w, y + .15, "x", color=RED, ms=5)
ax[0].set_xticks(x); ax[0].set_xlabel("rodada"); ax[0].set_ylabel("tentativas"); ax[0].set_yticks([1, 2, 3]); ax[0].plot([], [], "x", color=RED, label="reprovado após 3")
ax[0].legend(fontsize=6.5, frameon=False, loc="upper left", ncol=3, bbox_to_anchor=(0, 1.2))
ax[1].hist(lat, bins=12, color=GRY); ax[1].axvline(st.median(lat), color=RED, ls="--", lw=1)
ax[1].text(st.median(lat)+.2, ax[1].get_ylim()[1]*.85, f"mediana\n{st.median(lat):.1f} s", fontsize=7, color=RED)
ax[1].set_xlabel("latência por requisição (s)"); ax[1].set_ylabel("requisições"); fig.tight_layout(); save(fig, "fig_tentativas")

# ---------- evolução da similaridade + mapa de similaridade entre as 40 falas locais
s1 = [r["local_opening"]["quality"]["max_similarity"] for r in R]; s2 = [r["local_reply"]["quality"]["max_similarity"] for r in R]
fig, ax = plt.subplots(figsize=(7.2, 2.5)); ax.plot(x, s1, "-o", color=BLUE, ms=3.5, label="Turno 1"); ax.plot(x, s2, "-s", color=ORG, ms=3.5, label="Turno 2")
ax.axhline(.85, color=RED, ls="--", lw=1); ax.text(1, .86, "limiar de rejeição (0,85)", color=RED, fontsize=7)
ax.axvspan(1, 7.5, color="#edf2f7", zorder=0); ax.text(4.2, .02, "R01–R07", fontsize=6.5, ha="center", color=GRY)
ax.set_ylim(0, 1); ax.set_xticks(x); ax.set_xlabel("rodada"); ax.set_ylabel("similaridade máx. com\nfalas locais anteriores"); ax.legend(frameon=False, fontsize=7, loc="center right")
save(fig, "fig_similaridade"); M["sim_early"] = st.mean(s1[1:7]); M["sim_late"] = st.mean(s1[8:])
resp = [r[k]["response"] for r in R for k in ("local_opening", "local_reply")]   # ordem: R1T1, R1T2, R2T1...
S = np.array([[difflib.SequenceMatcher(None, a, b).ratio() for b in resp] for a in resp])
fig, ax = plt.subplots(figsize=(3.6, 3.2)); im = ax.imshow(S, cmap="Blues", vmin=0, vmax=1)
ax.set_xticks(range(0, 40, 4), [f"{i//2+1}" for i in range(0, 40, 4)], fontsize=6.5); ax.set_yticks(range(0, 40, 4), [f"{i//2+1}" for i in range(0, 40, 4)], fontsize=6.5)
ax.set_xlabel("rodada"); ax.set_ylabel("rodada"); fig.colorbar(im, ax=ax, fraction=.046, label="similaridade"); save(fig, "fig_mapa_similaridade")
off = S[~np.eye(40, dtype=bool)]; M["pares_sim_media"] = float(off.mean())
near = [S[i, j] for i in range(40) for j in range(40) if abs(i - j) in (1, 2) and i != j]; far = [S[i, j] for i in range(40) for j in range(40) if abs(i - j) > 8]
M["sim_vizinhas"] = float(np.mean(near)); M["sim_distantes"] = float(np.mean(far))

# ---------- gabarito: similaridade entre rodadas por componente (tema mascarado)
def mask(t, r): return re.sub(re.escape(r["topic"].lower()), "<T>", t.lower())
def msim(key):
    xs = [mask(key(r), r) for r in R]; return st.mean(difflib.SequenceMatcher(None, a, b).ratio() for a, b in itertools.combinations(xs, 2))
comp = {"Juiz: veredito": lambda r: r["judgment"]["verdict"], "Juiz: plano": lambda r: r["judgment"]["plan_update"], "Juiz: memória": lambda r: r["judgment"]["memory"],
        "Trabalhista: defesa": lambda r: r["defense"][:300], "Trabalhista: abertura": lambda r: re.sub(r"^Considerando.*?\):\s*", "", r["opening"]),
        "Liberal (Qwen): turno 2": lambda r: r["local_reply"]["response"], "Liberal (Qwen): turno 1": lambda r: r["local_opening"]["response"]}
vals = {k: msim(f) for k, f in comp.items()}; M["template_sim"] = vals
fig, ax = plt.subplots(figsize=(5.4, 2.7)); ks = list(vals); ax.barh(ks, [vals[k] for k in ks], color=[GRN]*3 + [BLUE]*2 + [ORG]*2); ax.invert_yaxis()
for i, k in enumerate(ks): ax.text(vals[k]+.01, i, f"{vals[k]:.2f}", va="center", fontsize=8)
ax.set_xlim(0, 1.12); ax.set_xlabel("similaridade média entre pares de rodadas (tema mascarado)"); save(fig, "fig_gabarito")
M["defesa_palavras"] = st.mean(len(r["defense"].split()) for r in R); M["abertura_palavras"] = st.mean(len(r["opening"].split()) for r in R)
M["local_palavras"] = st.mean(len(r[k]["response"].split()) for r in R for k in KS)

# ---------- ablação
ab = ARN / "analise/dados/ablacao.json"
if ab.exists():
    rows = json.load(open(ab)); conds = list(dict.fromkeys(r["cond"] for r in rows)); A = {}
    for c in conds:
        rs = [r for r in rows if r["cond"] == c]; sd = sorted({r["seed"] for r in rs}); div = []
        for s_ in sd:
            tx = [r["text"] for r in rs if r["seed"] == s_]; div.append(st.mean(difflib.SequenceMatcher(None, a, b).ratio() for a, b in itertools.combinations(tx, 2)))
        A[c] = dict(n=len(rs), anchor=st.mean(r["anchor"] for r in rs), copy_mean=st.mean(r["copy"] for r in rs), copy_gt45=st.mean(r["copy"] > .45 for r in rs),
                    fmt=st.mean(r["fmt"] for r in rs), pt=st.mean(r["pt"] for r in rs), words=st.mean(r["words"] for r in rs), lat=st.mean(r["latency"] for r in rs),
                    pair_sim=st.mean(div), anchor_sd=st.pstdev([st.mean(r["anchor"] for r in rs if r["seed"] == s_) for s_ in sd]))
    M["ablacao"] = A
    lab = {"A_projeto_1.5B": "A\n1.5B\nprojeto", "B_sem_papel_1.5B": "B\n1.5B\nsem papel", "C_projeto_1.5B_T0.8": "C\n1.5B\nT=0,8", "D_projeto_0.5B": "D\n0.5B\nprojeto"}
    fig, ax = plt.subplots(1, 3, figsize=(7.4, 2.5))
    for a, (key, ttl) in zip(ax, [("anchor", "cita termo do tema"), ("copy_gt45", "cópia >45% do prompt"), ("pair_sim", "similaridade entre rodadas")]):
        v = [A[c][key] for c in conds]; a.bar(range(len(conds)), v, color=[BLUE, GRY, ORG, RED][:len(conds)])
        for i, y in enumerate(v): a.text(i, y + .01, f"{y:.2f}", ha="center", fontsize=7)
        a.set_xticks(range(len(conds))); a.set_xticklabels([lab[c] for c in conds], fontsize=6.5); a.set_title(ttl, fontsize=8); a.set_ylim(0, max(v)*1.25 + .02)
    fig.tight_layout(); save(fig, "fig_ablacao")

# ---------- tabelas LaTeX geradas (sections/tab_rodadas.tex e tab_ablacao.tex)
SEC = ARN / "../../overleaf-relatorio/arn_p/sections"
CURTO = {5: "Férias, licenças e cuidado", 6: "Plataformas e aplicativos", 9: "Saúde ocupacional", 10: "Proteção social portátil", 14: "IA, automação e emprego",
         15: "Concorrência e barreiras", 17: "Justiça do trabalho", 18: "Encargos sobre a folha", 19: "\\textit{Sandboxes} regulatórios", 20: "Estratégia final consolidada"}
lin = []
for r in R:
    n = r["round"]; t = CURTO.get(n, r["topic"])
    f = lambda k: f"{len(r[k]['attempts'])}" + ("" if r[k]["accepted"] else "$^\\times$")
    lin.append(f"{n:02d} & {t} & {f('local_opening')} & {f('local_reply')} & {r['local_opening']['quality']['max_similarity']:.2f} & {r['local_reply']['quality']['max_similarity']:.2f} \\\\".replace(".", "{,}"))
(SEC / "tab_rodadas.tex").write_text("\\begin{tabular}{rlcccc}\n\\toprule\nR & Tema & Tent. T1 & Tent. T2 & Sim. T1 & Sim. T2 \\\\\n\\midrule\n" + "\n".join(lin) + "\n\\bottomrule\n\\end{tabular}\n")
if "ablacao" in M:
    nm = {"A_projeto_1.5B": "A: projeto, 1.5B, $T{=}0{,}3$", "B_sem_papel_1.5B": "B: sem papel nem JSON, 1.5B", "C_projeto_1.5B_T0.8": "C: projeto, 1.5B, $T{=}0{,}8$", "D_projeto_0.5B": "D: projeto, 0.5B, $T{=}0{,}3$"}
    pc = lambda v: f"{100*v:.0f}\\%"
    lin = [f"{nm[c]} & {pc(a['fmt'])} & {pc(a['anchor'])} & {pc(a['copy_gt45'])} & {a['pair_sim']:.2f} & {a['words']:.0f} \\\\".replace(".", "{,}") for c, a in M["ablacao"].items()]
    (SEC / "tab_ablacao.tex").write_text("\\begin{tabular}{lccccc}\n\\toprule\nCondição & Formato & Tema & Cópia & Sim. & Palavras \\\\\n\\midrule\n" + "\n".join(lin) + "\n\\bottomrule\n\\end{tabular}\n")
json.dump(M, open(ARN / "analise/dados/metricas.json", "w"), ensure_ascii=False, indent=1); print(json.dumps({k: v for k, v in M.items() if k != "ablacao"}, ensure_ascii=False, indent=1))
