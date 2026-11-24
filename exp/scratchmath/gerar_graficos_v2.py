"""Gera gráficos limpos em alta resolução (300 DPI) na paleta exata da apresentação
do Atlas do Erro (#F8F7F3, #1E2B4A, #2F6FB5, #1F6E44, #B9283A, #7D5200).
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

AQUI = Path(__file__).resolve().parent
OUT = AQUI / "resultados_v2" / "figuras"
OUT.mkdir(parents=True, exist_ok=True)

BG = "#F8F7F3"
NAVY = "#1E2B4A"
AZUL = "#2F6FB5"
VERDE = "#1F6E44"
VERM = "#B9283A"
AMBAR = "#7D5200"
CINZA = "#5B6475"
GRADE = "#D8DDE6"

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.edgecolor"] = GRADE
plt.rcParams["axes.linewidth"] = 0.8


def gerar_grafico_ocr(m2: dict):
    ocr = m2["ocr"]
    itens = [
        ("TrOCR-printed\n(antes · Ciclo 1)", 100 * ocr["TrOCR-printed (V1)"]["quebra_ancorado"] / 57, VERM, "0/57"),
        ("Pix2Text\n(CPU · sem GPU)", 100 * ocr["Pix2Text (CPU, dedicado)"]["quebra_ancorado"] / 57, AMBAR, "25/57"),
        ("Qwen2.5-VL 7B\n(só transcrevendo)", 100 * ocr["Qwen2.5-VL 7B (VLM-OCR)"]["quebra_ancorado"] / 57, AZUL, "27/57"),
        ("Qwen2.5-VL 3B\n(só transcrevendo)", 100 * ocr["Qwen2.5-VL 3B (VLM-OCR)"]["quebra_ancorado"] / 57, VERDE, "28/57"),
    ]
    labels = [x[0] for x in itens]
    vals = [x[1] for x in itens]
    cores = [x[2] for x in itens]
    fracs = [x[3] for x in itens]

    fig, ax = plt.subplots(figsize=(5.4, 3.0), dpi=300)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    ys = range(len(labels))
    bars = ax.barh(ys, vals, color=cores, height=0.56, edgecolor="none")
    ax.set_yticks(list(ys))
    ax.set_yticklabels(labels, fontsize=9.2, color=NAVY, fontweight="bold")
    ax.set_xlim(0, 74)
    ax.set_xlabel("% das 57 equações do 1º grau em que o SymPy achou a quebra", fontsize=8.5, color=CINZA, labelpad=6)
    ax.xaxis.grid(True, linestyle="--", alpha=0.6, color=GRADE)
    ax.set_axisbelow(True)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.tick_params(axis="x", labelsize=8.5, colors=CINZA)
    ax.tick_params(axis="y", length=0)

    for bar, v, frac in zip(bars, vals, fracs):
        txt = f" {v:.1f}% ({frac})".replace(".", ",")
        ax.text(v + 1.0, bar.get_y() + bar.get_height() / 2, txt,
                va="center", ha="left", fontsize=9.2, fontweight="bold", color=NAVY)

    plt.tight_layout(pad=0.6)
    path = OUT / "grafico_ocr.png"
    fig.savefig(path, dpi=300, facecolor=BG)
    plt.close(fig)
    print(f"Salvo: {path}")


def gerar_grafico_ciclo2(m2: dict):
    esc = m2["escopo"]["condicoes"]
    maj = 100 * m2["escopo"]["majority"]["acc"]

    itens = [
        ("Atlas V2 + Gemma2 2B\n(pós-SymPy)", 100 * esc["V2_A3_atlas_gemma2_2b"]["acc"], VERM),
        ("Atlas V2 + Qwen2.5 1.5B\n(pós-SymPy)", 100 * esc["V2_A2_atlas_qwen25_1.5b"]["acc"], VERM),
        ("Atlas V2 + Regra\n(sem IA no Passo 3)", 100 * esc["V2_A1_regra"]["acc"], AMBAR),
        ("Atlas V2 + Qwen2.5 7B\n(pós-SymPy · 5× maior)", 100 * esc["V2_A4_atlas_qwen25_7b"]["acc"], AZUL),
        ("Qwen2.5-VL 7B\n(foto direto + PT-BR)", 100 * esc["V2_FULL_C2_visao_pt_qwen25vl_7b"]["acc"], "#4A78B8"),
        ("OCR 3B → Qwen2.5 7B\n(separando leitura e texto)", 100 * esc["V2_B3_ocr_pt_qwen25_7b"]["acc"], VERDE),
    ]
    labels = [x[0] for x in itens]
    vals = [x[1] for x in itens]
    cores = [x[2] for x in itens]

    fig, ax = plt.subplots(figsize=(5.5, 3.15), dpi=300)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    ys = range(len(labels))
    bars = ax.barh(ys, vals, color=cores, height=0.58, edgecolor="none")
    ax.axvline(maj, color=VERM, linestyle="--", linewidth=1.4, alpha=0.85)
    ax.text(maj - 1.2, len(labels) - 0.35, f"Chute ({maj:.1f}%)".replace(".", ","),
            color=VERM, fontsize=8.3, fontweight="bold", ha="right", va="bottom",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="#F7DEE0", edgecolor="none"))

    ax.set_yticks(list(ys))
    ax.set_yticklabels(labels, fontsize=8.5, color=NAVY, fontweight="bold")
    ax.set_xlim(0, 68)
    ax.set_ylim(-0.6, len(labels) - 0.1)
    ax.set_xlabel("Acerto exato na classificação das 7 categorias (N = 57)", fontsize=8.3, color=CINZA, labelpad=5)
    ax.xaxis.grid(True, linestyle="--", alpha=0.5, color=GRADE)
    ax.set_axisbelow(True)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.tick_params(axis="x", labelsize=8.3, colors=CINZA)
    ax.tick_params(axis="y", length=0)

    for bar, v in zip(bars, vals):
        txt = f" {v:.1f}%".replace(".", ",")
        ax.text(v + 0.9, bar.get_y() + bar.get_height() / 2, txt,
                va="center", ha="left", fontsize=8.8, fontweight="bold", color=NAVY)

    plt.tight_layout(pad=0.6)
    path = OUT / "grafico_ciclo2.png"
    fig.savefig(path, dpi=300, facecolor=BG)
    plt.close(fig)
    print(f"Salvo: {path}")


def main():
    m2 = json.loads((AQUI / "resultados_v2" / "metricas_v2.json").read_text(encoding="utf-8"))
    gerar_grafico_ocr(m2)
    gerar_grafico_ciclo2(m2)


if __name__ == "__main__":
    main()
