"""Avaliação completa do Ciclo V2:
  1) Tabela de comparação dos 4 OCRs no Passo 1 (TrOCR-printed × Pix2Text × Qwen2.5-VL 3B × Qwen2.5-VL 7B) em N = 57
  2) Tabela Atlas V2 no escopo nativo (N = 57 equações 1º grau): Regra × Qwen 1.5B × Gemma2 2B × Qwen 7B
  3) Tabela Benchmark Completo em PT-BR (N = 241): V1 (chinês) vs V2 (PT-BR) + Qwen2.5-VL 7B vs artigo
  4) Opcional: avaliação ECE local via --juiz-local qwen2.5:7b

Salva `resultados_v2/relatorio_v2.md` e `resultados_v2/metricas_v2.json`.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import time
import urllib.request

from avaliar import (
    ESQUEMA_JUIZ,
    bootstrap_ic,
    carregar_jsonl,
    detectar_vazamento_resposta,
    f1_macro,
)
from categorias import CODIGOS_VALIDOS

AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "dados"
RES_V1 = AQUI / "resultados"
RES = AQUI / "resultados_v2"
OLLAMA = "http://localhost:11434"


def julgar_ece_v2(modelo_juiz: str, nome_cond: str, preds_por_idx: dict, gt_por_idx: dict):
    out_path = RES / f"juiz_ece_{nome_cond}.jsonl"
    feitos = {r["idx"]: r for r in carregar_jsonl(out_path)}
    pendentes = [i for i in sorted(preds_por_idx) if i not in feitos]
    if pendentes:
        print(f"[Juiz ECE V2 {modelo_juiz}] {nome_cond}: {len(pendentes)} casos...")
        t0 = time.perf_counter()
        for n, idx in enumerate(pendentes, 1):
            p = preds_por_idx[idx]
            gt = gt_por_idx[idx]
            exp_pred = (p.get("explicacao_erro") or "").strip()
            if not p.get("categoria_scratchmath") or not exp_pred:
                rec = {"idx": idx, "explicacao_correta": False, "justificativa": "sem diagnóstico emitido"}
            else:
                exp_ref = gt.get("error_explanation_pt") or gt["error_explanation"]
                prompt = (
                    "Você é um avaliador rigoroso de diagnóstico de erros em matemática (protocolo ScratchMath ECE).\n"
                    "Compare a EXPLICACAO_CANDIDATA com a EXPLICACAO_REFERENCIA dos professores (ambas em português).\n"
                    "Responda `explicacao_correta: true` SOMENTE se a candidata identificar corretamente o mesmo erro principal "
                    "(ou a mesma etapa/causa matemática central) descrita pela referência. "
                    "Se for genérica demais, apontar outro erro ou inventar causa falsa, responda `false`.\n"
                    "Em `justificativa`, escreva no máximo 1 frase curta (até 18 palavras).\n\n"
                    f"Questão: {gt.get('question_pt') or gt['question']}\n"
                    f"Resposta certa: {gt['answer']} | Resposta aluno: {gt['student_answer']}\n"
                    f"EXPLICACAO_REFERENCIA (GT): {exp_ref}\n"
                    f"EXPLICACAO_CANDIDATA: {exp_pred}\n\n"
                    'Responda APENAS JSON curto: {"explicacao_correta": true/false, "justificativa": "..."}'
                )
                corpo = {
                    "model": modelo_juiz,
                    "stream": False,
                    "messages": [{"role": "user", "content": prompt}],
                    "format": ESQUEMA_JUIZ,
                    "options": {"temperature": 0, "num_predict": 160},
                }
                req = urllib.request.Request(
                    f"{OLLAMA}/api/chat",
                    data=json.dumps(corpo).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                )
                try:
                    with urllib.request.urlopen(req, timeout=180) as resp:
                        r = json.loads(resp.read().decode("utf-8"))
                    parsed = json.loads(r.get("message", {}).get("content", "{}"))
                    rec = {
                        "idx": idx,
                        "explicacao_correta": bool(parsed.get("explicacao_correta", False)),
                        "justificativa": str(parsed.get("justificativa", "")),
                    }
                except Exception as e:
                    rec = {"idx": idx, "explicacao_correta": False, "justificativa": f"erro_juiz: {e}"}
            with out_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            feitos[idx] = rec
            if n % 30 == 0 or n == len(pendentes):
                print(f"  Juiz {nome_cond}: {n}/{len(pendentes)} ({time.perf_counter() - t0:.1f}s)")
    return feitos


def avaliar_bloco(conds_meta, idxs, gt_por_idx, juiz_local=None):
    y_true = [gt_por_idx[i]["error_category_codigo"] for i in idxs]
    n = len(idxs)
    maj_cod, _ = Counter(y_true).most_common(1)[0]
    maj_hits = [1 if yt == maj_cod else 0 for yt in y_true]
    maj_acc, maj_lo, maj_hi = bootstrap_ic(maj_hits)
    maj_f1, _ = f1_macro(y_true, [maj_cod] * n)

    res_out = {}
    for cod, rotulo, base_dir in conds_meta:
        p = base_dir / f"{cod}.jsonl"
        if not p.exists():
            continue
        preds_map = {r["idx"]: r for r in carregar_jsonl(p)}
        if not all(i in preds_map for i in idxs):
            continue
        y_pred = [preds_map[i].get("categoria_scratchmath") for i in idxs]
        hits = [1 if yp == yt else 0 for yt, yp in zip(y_true, y_pred)]
        acc, lo, hi = bootstrap_ic(hits)
        resp_idxs = [i for i in idxs if preds_map[i].get("categoria_scratchmath") is not None]
        acc_cond = (
            sum(1 for i in resp_idxs if preds_map[i]["categoria_scratchmath"] == gt_por_idx[i]["error_category_codigo"])
            / len(resp_idxs)
            if resp_idxs
            else 0.0
        )
        f1m, _ = f1_macro(y_true, y_pred)
        com_dica = [i for i in idxs if (preds_map[i].get("dica_aluno") or "").strip()]
        vaz = [i for i in com_dica if detectar_vazamento_resposta(preds_map[i]["dica_aluno"], gt_por_idx[i])]
        tempos = [preds_map[i].get("tempo_s", 0.0) for i in idxs]
        dist = Counter(yp or "sem_resposta" for yp in y_pred)

        ece_info = None
        if juiz_local and base_dir == RES:
            julg = julgar_ece_v2(juiz_local, cod, {i: preds_map[i] for i in idxs}, gt_por_idx)
            ece_hits = [1 if julg[i]["explicacao_correta"] else 0 for i in idxs]
            ea, elo, ehi = bootstrap_ic(ece_hits)
            ece_info = {"acc": ea, "ic95": [elo, ehi], "acertos": sum(ece_hits)}

        res_out[cod] = {
            "rotulo": rotulo,
            "n": n,
            "acertos": sum(hits),
            "acc": acc,
            "ic95": [lo, hi],
            "n_respondidos": len(resp_idxs),
            "cobertura": len(resp_idxs) / n,
            "acc_cond": acc_cond,
            "f1_macro": f1m,
            "com_dica": len(com_dica),
            "vazamentos": len(vaz),
            "tempo_medio_s": sum(tempos) / len(tempos) if tempos else 0.0,
            "dist_pred": dict(dist),
            "ece": ece_info,
        }
    return {
        "n": n,
        "majority": {"codigo": maj_cod, "acc": maj_acc, "ic95": [maj_lo, maj_hi], "f1_macro": maj_f1},
        "condicoes": res_out,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--juiz-local", type=str, default=None)
    args = parser.parse_args()

    gt_lista = carregar_jsonl(DADOS / "middle_pt.jsonl")
    if not gt_lista:
        gt_lista = carregar_jsonl(DADOS / "middle.jsonl")
    gt_por_idx = {r["idx"]: r for r in gt_lista}
    escopo_idxs = [r["idx"] for r in carregar_jsonl(DADOS / "escopo_1grau.jsonl")]
    full_idxs = sorted(gt_por_idx.keys())

    # 1. Tabela de OCRs no Passo 1 (N = 57)
    ocr_resumo = {}
    # TrOCR-printed de V1
    v1_a1 = {r["idx"]: r for r in carregar_jsonl(RES_V1 / "A1_regra.jsonl")}
    if v1_a1:
        q_puro = sum(1 for i in escopo_idxs if v1_a1[i]["status_sympy"] == "quebra")
        sq_puro = sum(1 for i in escopo_idxs if v1_a1[i]["status_sympy"] == "sem_quebra")
        ocr_resumo["TrOCR-printed (V1)"] = {
            "n": len(escopo_idxs),
            "linhas_validas_media": 0.0,
            "quebra_puro": q_puro,
            "sem_quebra_puro": sq_puro,
            "quebra_ancorado": q_puro,
            "regra_acertos_anc": 0,
            "tempo_medio_s": sum(v1_a1[i]["t_ocr_s"] for i in escopo_idxs) / len(escopo_idxs),
        }

    for cod, nome in [
        ("OCR_pix2text", "Pix2Text (CPU, dedicado)"),
        ("OCR_qwen25vl_3b", "Qwen2.5-VL 3B (VLM-OCR)"),
        ("OCR_qwen25vl_7b", "Qwen2.5-VL 7B (VLM-OCR)"),
    ]:
        rows = {r["idx"]: r for r in carregar_jsonl(RES / f"{cod}.jsonl")}
        if not rows:
            continue
        sub = [rows[i] for i in escopo_idxs if i in rows]
        n_s = len(sub)
        ocr_resumo[nome] = {
            "n": n_s,
            "linhas_validas_media": sum(r["n_linhas_validas_sympy"] for r in sub) / n_s,
            "com_alguma_eq_valida": sum(1 for r in sub if r["n_linhas_validas_sympy"] >= 1),
            "quebra_puro": sum(1 for r in sub if r["puro"]["status_sympy"] == "quebra"),
            "sem_quebra_puro": sum(1 for r in sub if r["puro"]["status_sympy"] == "sem_quebra"),
            "quebra_ancorado": sum(1 for r in sub if r["ancorado"]["status_sympy"] == "quebra"),
            "regra_emitidas_anc": sum(1 for r in sub if r["ancorado"]["categoria_scratchmath"] is not None),
            "regra_acertos_anc": sum(1 for r in sub if r["ancorado"]["categoria_scratchmath"] == r["gt_codigo"]),
            "tempo_medio_s": sum(r["tempo_ocr_s"] for r in sub) / n_s,
        }

    # 2. Bloco Escopo (N = 57)
    conds_escopo = [
        ("V2_A1_regra", "A1 · Atlas V2 + Regra (OCR vencedor + SymPy)", RES),
        ("V2_A2_atlas_qwen25_1.5b", "A2 · Atlas V2 + Qwen2.5 1.5B (pós-SymPy, PT)", RES),
        ("V2_A3_atlas_gemma2_2b", "A3 · Atlas V2 + Gemma2 2B (pós-SymPy, PT)", RES),
        ("V2_A4_atlas_qwen25_7b", "A4 · Atlas V2 + Qwen2.5 7B (pós-SymPy, PT)", RES),
        ("V2_B1_ocr_pt_qwen25_1.5b", "B1 · Qwen2.5 1.5B (PT-BR + transcrição OCR)", RES),
        ("V2_B2_ocr_pt_gemma2_2b", "B2 · Gemma2 2B (PT-BR + transcrição OCR)", RES),
        ("V2_B3_ocr_pt_qwen25_7b", "B3 · Qwen2.5 7B (PT-BR + transcrição OCR)", RES),
        ("V2_FULL_C2_visao_pt_qwen25vl_7b", "C2 · Qwen2.5-VL 7B (foto direto + PT-BR)", RES),
    ]
    bloco_escopo = avaliar_bloco(conds_escopo, escopo_idxs, gt_por_idx, juiz_local=args.juiz_local)

    # 3. Bloco Completo (N = 241): V1 chinês vs V2 PT-BR
    conds_full = [
        ("B1_texto_qwen25_1.5b", "V1 (CH) · Qwen2.5 1.5B", RES_V1),
        ("V2_FULL_B1_pt_qwen25_1.5b", "V2 (PT) · Qwen2.5 1.5B", RES),
        ("B2_texto_gemma2_2b", "V1 (CH) · Gemma2 2B", RES_V1),
        ("V2_FULL_B2_pt_gemma2_2b", "V2 (PT) · Gemma2 2B", RES),
        ("C1_visao_qwen25vl_3b", "V1 (CH) · Qwen2.5-VL 3B (foto)", RES_V1),
        ("V2_FULL_C2_visao_pt_qwen25vl_7b", "V2 (PT) · Qwen2.5-VL 7B (foto)", RES),
    ]
    bloco_full = avaliar_bloco(conds_full, full_idxs, gt_por_idx, juiz_local=args.juiz_local)

    # Monta Markdown
    vencedor_ocr = (RES / "ocr_vencedor.txt").read_text(encoding="utf-8").strip() if (RES / "ocr_vencedor.txt").exists() else "—"
    linhas = [
        "# Resultados V2 — OCR Manuscrito + Escopo 1º Grau (`N = 57`) + Tradução PT-BR (`N = 241`)",
        "",
        f"- **Tradução PT-BR:** 100% local via `qwen2.5:7b` (Opção B), salva em `dados/middle_pt.jsonl`.",
        f"- **OCR vencedor adotado no Atlas V2 (`N = 57`):** `{vencedor_ocr}`.",
        "",
        "## 1. Comparação de OCR no Passo 1 (`N = 57` equações do 1º grau)",
        "",
        "| Modelo de OCR (Passo 1) | Equações válidas/folha | ≥1 eq. válida | SymPy quebra (puro) | SymPy quebra (ancorado) | Regra acertou GT | Tempo médio (s) |",
        "|:---|---:|---:|---:|---:|---:|---:|",
    ]
    for nome, d in ocr_resumo.items():
        n_s = d["n"]
        alguma = f"{d.get('com_alguma_eq_valida', 0)}/{n_s}" if "com_alguma_eq_valida" in d else f"0/{n_s}"
        linhas.append(
            f"| {nome} | {d['linhas_validas_media']:.2f} | {alguma} | "
            f"{d['quebra_puro']}/{n_s} ({100*d['quebra_puro']/n_s:.1f}%) | "
            f"**{d['quebra_ancorado']}/{n_s} ({100*d['quebra_ancorado']/n_s:.1f}%)** | "
            f"{d['regra_acertos_anc']}/{n_s} ({100*d['regra_acertos_anc']/n_s:.1f}%) | {d['tempo_medio_s']:.2f} |"
        )

    def render_tabela(titulo, bloco):
        m = bloco["majority"]
        n_b = bloco["n"]
        tem_ece = any(v["ece"] is not None for v in bloco["condicoes"].values())
        h_ece = f" | ECE (juiz `{args.juiz_local}`)" if tem_ece else ""
        s_ece = " |---:" if tem_ece else ""
        out = [
            "",
            f"## {titulo} (`N = {n_b}`)",
            "",
            f"| Condição | Cobertura | ECC Geral [IC 95%] | ECC Cond. | F1 Macro | Vaza resposta | Tempo (s){h_ece} |",
            f"|:---|---:|---:|---:|---:|---:|---:{s_ece}|",
            f"| *Chute majoritário (`{m['codigo']}`)* | 100.0% | **{100*m['acc']:.1f}%** [{100*m['ic95'][0]:.1f}–{100*m['ic95'][1]:.1f}%] | {100*m['acc']:.1f}% | {m['f1_macro']:.3f} | — | —{' | —' if tem_ece else ''} |",
        ]
        for cod, r in bloco["condicoes"].items():
            vaz = f"{r['vazamentos']}/{r['com_dica']} ({100*r['vazamentos']/r['com_dica']:.1f}%)" if r["com_dica"] else "0/0"
            ec = f" | {100*r['ece']['acc']:.1f}% [{100*r['ece']['ic95'][0]:.1f}–{100*r['ece']['ic95'][1]:.1f}%]" if (tem_ece and r["ece"]) else (" | —" if tem_ece else "")
            out.append(
                f"| {r['rotulo']} | {r['n_respondidos']}/{n_b} ({100*r['cobertura']:.1f}%) | "
                f"**{100*r['acc']:.1f}%** [{100*r['ic95'][0]:.1f}–{100*r['ic95'][1]:.1f}%] | "
                f"{100*r['acc_cond']:.1f}% | {r['f1_macro']:.3f} | {vaz} | {r['tempo_medio_s']:.2f}{ec} |"
            )
        out += ["", "### Distribuição das categorias previstas (colapso de classes)", ""]
        cols = CODIGOS_VALIDOS + ["sem_resposta"]
        out.append("| Condição | " + " | ".join(f"`{c}`" for c in cols) + " |")
        out.append("|:---|" + "|".join(["---:"] * len(cols)) + "|")
        for cod, r in bloco["condicoes"].items():
            out.append(f"| `{cod}` | " + " | ".join(str(r["dist_pred"].get(c, 0)) for c in cols) + " |")
        return out

    linhas += render_tabela("2. Pipeline Atlas V2 no escopo nativo (Equações do 1º grau)", bloco_escopo)
    linhas += render_tabela("3. Benchmark completo: efeito da tradução PT-BR e do Qwen2.5-VL 7B", bloco_full)

    (RES / "metricas_v2.json").write_text(
        json.dumps({"ocr": ocr_resumo, "escopo": bloco_escopo, "full": bloco_full}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    rel_path = RES / "relatorio_v2.md"
    rel_path.write_text("\n".join(linhas), encoding="utf-8")
    print(f"Salvo: {rel_path}")
    print("\n".join(linhas[:55]))


if __name__ == "__main__":
    main()
