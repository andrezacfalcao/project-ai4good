"""Etapa 1: baixa o split `middle` (7º ao 9º ano, 241 folhas) do dataset songdj/ScratchMath,
salva imagens e metadados estruturados localmente e gera o raio-X inicial do dataset.
"""
from collections import Counter
import json
from pathlib import Path
import re

from datasets import load_dataset

from categorias import POR_ID

AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "dados"
IMAGENS = DADOS / "imagens"


def classificar_tipo_questao(q: str) -> str:
    """Classificação heurística simples do formato da questão (só para raio-X)."""
    if re.search(r"解方程|方程.*解|一元一次", q):
        return "equacao_explicita"
    if "=" in q and re.search(r"[a-zA-Z]", q):
        return "expressao_ou_equacao_com_variavel"
    if re.search(r"角|三角|圆|平行|垂直|面积|周长|图", q):
        return "geometria"
    if re.search(r"计算|求值|化简", q):
        return "calculo_ou_simplificacao"
    return "problema_textual_ou_outro"


def main():
    DADOS.mkdir(parents=True, exist_ok=True)
    IMAGENS.mkdir(parents=True, exist_ok=True)

    print("Baixando songdj/ScratchMath (config='middle', split='train')...")
    ds = load_dataset("songdj/ScratchMath", "middle", split="train")
    print(f"Total baixado: {len(ds)} exemplos")

    registros = []
    larguras, alturas = [], []
    cont_cat = Counter()
    cont_tipo = Counter()
    exemplos_por_cat = {}

    for idx, row in enumerate(ds):
        cat_id = int(row["error_category"])
        cat = POR_ID[cat_id]
        img = row["student_scratchwork"]
        img_nome = f"{idx:03d}_{row['question_id']}.jpg"
        img_path = IMAGENS / img_nome
        if img.mode != "RGB":
            img = img.convert("RGB")
        img.save(img_path, format="JPEG", quality=92)
        w, h = img.size
        larguras.append(w)
        alturas.append(h)

        tipo_q = classificar_tipo_questao(row["question"])
        cont_cat[cat["codigo"]] += 1
        cont_tipo[tipo_q] += 1

        reg = {
            "idx": idx,
            "question_id": row["question_id"],
            "question": row["question"],
            "answer": row["answer"],
            "solution": row["solution"],
            "student_answer": row["student_answer"],
            "image_path": f"dados/imagens/{img_nome}",
            "image_size": [w, h],
            "error_category_id": cat_id,
            "error_category_zh": cat["zh"],
            "error_category_en": cat["en"],
            "error_category_pt": cat["pt"],
            "error_category_codigo": cat["codigo"],
            "error_explanation": row["error_explanation"],
            "tipo_questao_heuristico": tipo_q,
        }
        registros.append(reg)
        if cat["codigo"] not in exemplos_por_cat:
            exemplos_por_cat[cat["codigo"]] = reg

    jsonl_path = DADOS / "middle.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as f:
        for r in registros:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    n = len(registros)
    majoritaria_cod, majoritaria_n = cont_cat.most_common(1)[0]
    linhas = [
        "# Raio-X do dataset `songdj/ScratchMath` (`middle` — 7º ao 9º ano)",
        "",
        f"- **Total de amostras:** {n}",
        f"- **Baseline majoritário (chutar sempre `{majoritaria_cod}`):** {majoritaria_n}/{n} ({100 * majoritaria_n / n:.1f}%)",
        f"- **Resolução das fotos:** largura {min(larguras)}–{max(larguras)} px (mediana {sorted(larguras)[n // 2]}), altura {min(alturas)}–{max(alturas)} px (mediana {sorted(alturas)[n // 2]})",
        "",
        "## Distribuição das 7 categorias (GT dos professores)",
        "",
        "| ID | Código | Chinês | Português | Qtd | % |",
        "|---:|:---|:---|:---|---:|---:|",
    ]
    for cid in sorted(POR_ID):
        c = POR_ID[cid]
        qtd = cont_cat[c["codigo"]]
        linhas.append(f"| {cid} | `{c['codigo']}` | {c['zh']} | {c['pt']} | {qtd} | {100 * qtd / n:.1f}% |")

    linhas += [
        "",
        "## Distribuição heurística de tipos de questão",
        "",
        "| Tipo heurístico | Qtd | % |",
        "|:---|---:|---:|",
    ]
    for tipo, qtd in cont_tipo.most_common():
        linhas.append(f"| `{tipo}` | {qtd} | {100 * qtd / n:.1f}% |")

    linhas += ["", "## Um exemplo real por categoria", ""]
    for cid in sorted(POR_ID):
        c = POR_ID[cid]
        ex = exemplos_por_cat.get(c["codigo"])
        if not ex:
            continue
        q_curta = ex["question"].replace("\n", " ")[:180]
        exp_curta = ex["error_explanation"].replace("\n", " ")[:220]
        linhas += [
            f"### {cid} · `{c['codigo']}` ({c['pt']} / {c['zh']})",
            f"- **Idx / ID:** `{ex['idx']:03d}` / `{ex['question_id']}` ({ex['image_size'][0]}×{ex['image_size'][1]})",
            f"- **Questão:** {q_curta}",
            f"- **Resposta certa:** `{ex['answer']}` | **Resposta aluno:** `{ex['student_answer']}`",
            f"- **Explicação GT:** {exp_curta}",
            "",
        ]

    raiox_path = DADOS / "raiox_dataset.md"
    raiox_path.write_text("\n".join(linhas), encoding="utf-8")
    print(f"Salvo: {jsonl_path}")
    print(f"Salvo: {raiox_path}")


if __name__ == "__main__":
    main()
