"""Etapa 5: calcula todas as métricas contra o GT real do songdj/ScratchMath (middle)
e gera `resultados/relatorio.md` + `resultados/metricas.json`.

Métricas:
  - Cobertura do OCR + SymPy (quebra / sem_quebra / ilegivel)
  - ECC: acurácia exata (geral e condicional), IC 95% por bootstrap (2000 reamostras, semente 2026),
    F1 macro nas 7 classes, diferença pareada vs Regra e vs Majority Baseline (46.9%)
  - Vazamento de resposta final na `dica_aluno`
  - Tempo médio por folha
  - ECE (opcional via --juiz-local ministral-3:8b): taxa de explicações coerentes com o GT dos professores
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import random
import re
import time
import urllib.error
import urllib.request

from categorias import CATEGORIAS_SCRATCHMATH, CODIGOS_VALIDOS, POR_CODIGO

AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "dados"
RES = AQUI / "resultados"
OLLAMA = "http://localhost:11434"
SEMENTE, REAMOSTRAS = 2026, 2000

CONDICOES_ORDEM = [
    ("A1_regra", "A1 · Atlas + Regra (TrOCR+SymPy+Checklist)"),
    ("A2_atlas_qwen25_1.5b", "A2 · Atlas + Qwen2.5 1.5B (pós-TrOCR+SymPy)"),
    ("A3_atlas_gemma2_2b", "A3 · Atlas + Gemma2 2B (pós-TrOCR+SymPy)"),
    ("B1_texto_qwen25_1.5b", "B1 · Passo 3 isolado: Qwen2.5 1.5B (enunciado+solução)"),
    ("B2_texto_gemma2_2b", "B2 · Passo 3 isolado: Gemma2 2B (enunciado+solução)"),
    ("C1_visao_qwen25vl_3b", "C1 · Multimodal local: Qwen2.5-VL 3B (foto direto)"),
]


def carregar_jsonl(path: Path):
    itens = []
    if not path.exists():
        return itens
    with path.open("r", encoding="utf-8") as f:
        for linha in f:
            if linha.strip():
                itens.append(json.loads(linha))
    return itens


def bootstrap_ic(valores, semente=SEMENTE, n_boot=REAMOSTRAS):
    if not valores:
        return 0.0, 0.0, 0.0
    rng = random.Random(semente)
    n = len(valores)
    media = sum(valores) / n
    amostras = sorted(
        sum(valores[rng.randrange(n)] for _ in range(n)) / n
        for _ in range(n_boot)
    )
    lo = amostras[int(0.025 * n_boot)]
    hi = amostras[int(0.975 * n_boot)]
    return media, lo, hi


def f1_macro(y_true, y_pred, classes=CODIGOS_VALIDOS):
    f1s = []
    por_classe = {}
    for c in classes:
        tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == c and yp == c)
        fp = sum(1 for yt, yp in zip(y_true, y_pred) if yt != c and yp == c)
        fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == c and yp != c)
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
        f1s.append(f1)
        suporte = tp + fn
        por_classe[c] = {"tp": tp, "fp": fp, "fn": fn, "suporte": suporte, "prec": prec, "rec": rec, "f1": f1}
    return sum(f1s) / len(classes), por_classe


def _extrair_formas_resposta(ans: str):
    """Extrai variantes normalizadas da resposta final (ex.: \\frac{1}{2}, 0.5 -> {'1/2', '0.5', '0,5'})."""
    if not ans:
        return set()
    s = ans.replace("$", "").replace("\\left", "").replace("\\right", "")
    # Converte \frac{a}{b} em a/b
    s = re.sub(r"\\frac\s*\{\{?([^{}]+)\}?\}?\s*\{\{?([^{}]+)\}?\}?", r"\1/\2", s)
    s = s.replace("{", "").replace("}", "").replace(" ", "")
    partes = re.split(r"[,;或、]", s)
    formas = set()
    for p in partes:
        p = p.strip()
        if not p:
            continue
        formas.add(p.lower())
        if "." in p:
            formas.add(p.replace(".", ",").lower())
    # Remove tokens muito curtos e genéricos (1 dígito isolado como '1' ou '0' gera muito falso positivo em texto)
    return {f for f in formas if len(f) >= 2 or "/" in f or "-" in f}


def detectar_vazamento_resposta(dica: str, reg: dict) -> bool:
    """Heurística conservadora: verifica se a dica menciona a resposta certa sem que ela já seja a do aluno."""
    if not dica or not dica.strip():
        return False
    texto = dica.lower().replace("$", "")
    texto_sem_esp = re.sub(r"\s+", "", texto)
    formas_certas = _extrair_formas_resposta(reg["answer"])
    formas_aluno = _extrair_formas_resposta(reg["student_answer"])
    exclusivas = formas_certas - formas_aluno
    for forma in exclusivas:
        # Procura como token isolado ou após '=' / 'é ' / 'seria ' / 'vale '
        padrao = r"(?<![0-9a-zA-Z/])" + re.escape(forma) + r"(?![0-9a-zA-Z/])"
        if re.search(padrao, texto) or f"={forma}" in texto_sem_esp:
            return True
    # Também verifica explicitamente "x = <resposta>" para respostas curtas de 1 dígito
    ans_curta = re.sub(r"[\s$]", "", reg["answer"]).lower()
    if len(ans_curta) == 1 and ans_curta.isdigit() and ans_curta != re.sub(r"[\s$]", "", reg["student_answer"]).lower():
        if re.search(rf"\bx\s*=\s*{re.escape(ans_curta)}\b", texto):
            return True
    return False


ESQUEMA_JUIZ = {
    "type": "object",
    "properties": {
        "explicacao_correta": {"type": "boolean"},
        "justificativa": {"type": "string"},
    },
    "required": ["explicacao_correta", "justificativa"],
}


def julgar_ece_local(modelo_juiz: str, nome_cond: str, preds_por_idx: dict, gt_por_idx: dict):
    """Avalia ECE (explicacao_erro vs error_explanation GT) via juiz local no Ollama, com checkpoint."""
    out_path = RES / f"juiz_ece_{nome_cond}.jsonl"
    feitos = {r["idx"]: r for r in carregar_jsonl(out_path)}
    pendentes = [idx for idx in sorted(preds_por_idx) if idx not in feitos]
    if pendentes:
        print(f"[Juiz ECE {modelo_juiz}] julgando {nome_cond}: {len(pendentes)} casos...")
        t0 = time.perf_counter()
        for n, idx in enumerate(pendentes, 1):
            p = preds_por_idx[idx]
            gt = gt_por_idx[idx]
            exp_pred = (p.get("explicacao_erro") or "").strip()
            # Se absteve / sem explicação válida, conta como incorreta automaticamente
            if not p.get("categoria_scratchmath") or not exp_pred:
                rec = {"idx": idx, "explicacao_correta": False, "justificativa": "sem diagnóstico emitido"}
            else:
                prompt = (
                    "Você é um avaliador rigoroso de diagnóstico de erros em matemática (protocolo ScratchMath ECE).\n"
                    "Compare a EXPLICACAO_CANDIDATA (em português) com a EXPLICACAO_REFERENCIA escrita por professores (em chinês).\n"
                    "Responda `explicacao_correta: true` SOMENTE se a candidata identificar corretamente o mesmo erro principal "
                    "(ou a mesma etapa/causa matemática central) descrita pela referência dos professores. "
                    "Se for genérica demais, apontar outro erro ou inventar uma causa falsa, responda `false`.\n"
                    "Em `justificativa`, escreva no máximo 1 frase curta (até 18 palavras).\n\n"
                    f"Questão: {gt['question']}\n"
                    f"Resposta certa: {gt['answer']} | Resposta aluno: {gt['student_answer']}\n"
                    f"EXPLICACAO_REFERENCIA (GT): {gt['error_explanation']}\n"
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--juiz-local", type=str, default=None, help="Ex.: ministral-3:8b para rodar avaliação ECE")
    args = parser.parse_args()

    gt_lista = carregar_jsonl(DADOS / "middle.jsonl")
    gt_por_idx = {r["idx"]: r for r in gt_lista}

    # Descobre quais condições existem e o conjunto comum de índices avaliados
    dados_cond = {}
    for cod, _ in CONDICOES_ORDEM:
        p = RES / f"{cod}.jsonl"
        if p.exists():
            dados_cond[cod] = {r["idx"]: r for r in carregar_jsonl(p)}

    if not dados_cond:
        raise SystemExit("Nenhum resultado encontrado em exp/scratchmath/resultados/")

    idxs = sorted(set.intersection(*(set(d.keys()) for d in dados_cond.values())))
    n = len(idxs)
    y_true = [gt_por_idx[i]["error_category_codigo"] for i in idxs]

    # Baseline majoritário real no conjunto avaliado
    maj_cod, maj_cnt = Counter(y_true).most_common(1)[0]
    maj_hits = [1 if yt == maj_cod else 0 for yt in y_true]
    maj_acc, maj_lo, maj_hi = bootstrap_ic(maj_hits)
    maj_f1, _ = f1_macro(y_true, [maj_cod] * n)

    # Estatísticas de OCR+SymPy (de A1_regra)
    ocr_stats = Counter()
    regra_atlas_stats = Counter()
    if "A1_regra" in dados_cond:
        for i in idxs:
            ocr_stats[dados_cond["A1_regra"][i]["status_sympy"]] += 1
            regra_atlas_stats[dados_cond["A1_regra"][i]["categoria_atlas"]] += 1

    resumo = {}
    ece_resumo = {}
    for cod, rotulo in CONDICOES_ORDEM:
        if cod not in dados_cond:
            continue
        preds_map = dados_cond[cod]
        y_pred = [preds_map[i].get("categoria_scratchmath") for i in idxs]
        hits = [1 if yp == yt else 0 for yt, yp in zip(y_true, y_pred)]
        acc, lo, hi = bootstrap_ic(hits)
        respondidos = [i for i in idxs if preds_map[i].get("categoria_scratchmath") is not None]
        cobertura = len(respondidos) / n
        acc_cond = (
            sum(1 for i in respondidos if preds_map[i]["categoria_scratchmath"] == gt_por_idx[i]["error_category_codigo"])
            / len(respondidos)
            if respondidos
            else 0.0
        )
        f1m, por_classe = f1_macro(y_true, y_pred)
        tempos = [preds_map[i].get("tempo_s", 0.0) for i in idxs]
        tempo_medio = sum(tempos) / len(tempos) if tempos else 0.0

        com_dica = [i for i in idxs if (preds_map[i].get("dica_aluno") or "").strip()]
        vazamentos = [i for i in com_dica if detectar_vazamento_resposta(preds_map[i]["dica_aluno"], gt_por_idx[i])]

        dist_pred = Counter(yp or "sem_resposta" for yp in y_pred)
        resumo[cod] = {
            "rotulo": rotulo,
            "n": n,
            "acertos": sum(hits),
            "acc": acc,
            "ic95": [lo, hi],
            "cobertura": cobertura,
            "n_respondidos": len(respondidos),
            "acc_cond": acc_cond,
            "f1_macro": f1m,
            "por_classe": por_classe,
            "tempo_medio_s": tempo_medio,
            "com_dica": len(com_dica),
            "vazamentos": len(vazamentos),
            "vazamentos_idxs": vazamentos[:10],
            "dist_pred": dict(dist_pred),
            "hits": hits,
        }

        if args.juiz_local:
            julg = julgar_ece_local(args.juiz_local, cod, {i: preds_map[i] for i in idxs}, gt_por_idx)
            ece_hits = [1 if julg[i]["explicacao_correta"] else 0 for i in idxs]
            ece_acc, ece_lo, ece_hi = bootstrap_ic(ece_hits)
            ece_resumo[cod] = {"acc": ece_acc, "ic95": [ece_lo, ece_hi], "acertos": sum(ece_hits)}

    # Comparações pareadas (bootstrap da diferença)
    comparacoes = []
    pares = [
        ("A2_atlas_qwen25_1.5b", "A1_regra"),
        ("A3_atlas_gemma2_2b", "A1_regra"),
        ("B1_texto_qwen25_1.5b", "A1_regra"),
        ("B2_texto_gemma2_2b", "A1_regra"),
        ("B1_texto_qwen25_1.5b", "B2_texto_gemma2_2b"),
        ("C1_visao_qwen25vl_3b", "B1_texto_qwen25_1.5b"),
        ("C1_visao_qwen25vl_3b", "B2_texto_gemma2_2b"),
    ]
    for a, b in pares:
        if a in resumo and b in resumo:
            dif = [ha - hb for ha, hb in zip(resumo[a]["hits"], resumo[b]["hits"])]
            m, lo, hi = bootstrap_ic(dif)
            comparacoes.append({"a": a, "b": b, "dif_pp": 100 * m, "ic95_pp": [100 * lo, 100 * hi]})

    # Monta relatório Markdown
    linhas = [
        f"# Resultados — Benchmark Atlas do Erro no `songdj/ScratchMath` (`middle`, N = {n})",
        "",
        "Avaliação sobre rascunhos manuscritos reais do 7º ao 9º ano com Ground Truth anotado por professores "
        "(Song et al., AIED 2026 / `arXiv:2603.24961`), **sem tradução prévia do dataset** "
        "(dicionário fixo das 7 categorias oficiais + prompts em PT-BR com saída JSON Schema fechada, `temperature=0`).",
        "",
        "## 1. Cobertura da pipeline determinística (TrOCR + SymPy) nas fotos reais",
        "",
        f"- **Total de folhas avaliadas:** {n}",
        f"- **`quebra` detectada pelo SymPy:** {ocr_stats['quebra']} ({100 * ocr_stats['quebra'] / n:.1f}%)",
        f"- **`sem_quebra` (equivalência mantida):** {ocr_stats['sem_quebra']} ({100 * ocr_stats['sem_quebra'] / n:.1f}%)",
        f"- **`ilegivel` (OCR ou parser SymPy falhou):** {ocr_stats['ilegivel']} ({100 * ocr_stats['ilegivel'] / n:.1f}%)",
        f"- **Distribuição interna da Regra (checklist Atlas):** {dict(regra_atlas_stats)}",
        "",
        "## 2. Tabela principal — Classificação do tipo de erro (ECC, 7 classes) e segurança pedagógica",
        "",
    ]

    col_ece = f" | ECE (juiz `{args.juiz_local}`)" if args.juiz_local else ""
    sep_ece = " |---:" if args.juiz_local else ""
    linhas += [
        f"| Condição | Cobertura | ECC Geral [IC 95%] | ECC Condicional | F1 Macro | Pista vaza resposta | Tempo médio (s){col_ece} |",
        f"|:---|---:|---:|---:|---:|---:|---:{sep_ece}|",
        f"| *Baseline majoritário (sempre `{maj_cod}`)* | 100.0% | **{100 * maj_acc:.1f}%** [{100 * maj_lo:.1f}–{100 * maj_hi:.1f}%] | {100 * maj_acc:.1f}% | {maj_f1:.3f} | — | —{' | —' if args.juiz_local else ''} |",
    ]
    for cod, _ in CONDICOES_ORDEM:
        if cod not in resumo:
            continue
        r = resumo[cod]
        vaz_str = f"{r['vazamentos']}/{r['com_dica']} ({100 * r['vazamentos'] / r['com_dica']:.1f}%)" if r["com_dica"] else "0/0"
        ece_cell = ""
        if args.juiz_local and cod in ece_resumo:
            er = ece_resumo[cod]
            ece_cell = f" | {100 * er['acc']:.1f}% [{100 * er['ic95'][0]:.1f}–{100 * er['ic95'][1]:.1f}%]"
        linhas.append(
            f"| {r['rotulo']} | {r['n_respondidos']}/{n} ({100 * r['cobertura']:.1f}%) | "
            f"**{100 * r['acc']:.1f}%** [{100 * r['ic95'][0]:.1f}–{100 * r['ic95'][1]:.1f}%] | "
            f"{100 * r['acc_cond']:.1f}% | {r['f1_macro']:.3f} | {vaz_str} | {r['tempo_medio_s']:.2f}{ece_cell} |"
        )

    linhas += [
        "",
        "### Referência publicada no artigo (Song et al., AIED 2026 — `middle`, 241 folhas)",
        "",
        "| Modelo / Referência (Artigo) | ECC (7 classes) | ECE (juiz do artigo) |",
        "|:---|---:|---:|",
        "| Professores humanos | 81.5% | 86.2% |",
        "| o4-mini (melhor do artigo) | 47.3% | 69.7% |",
        "| Gemma-3 27B | 46.1% | 26.1% |",
        "| Qwen2.5-VL 7B | 11.6% | 12.4% |",
        "| Chute aleatório | 12.5% | 0.0% |",
        "",
        "## 3. Diferenças pareadas (ECC Geral, pontos percentuais, IC 95% bootstrap)",
        "",
        "| Comparação (A − B) | Diferença (pp) | IC 95% (pp) |",
        "|:---|---:|---:|",
    ]
    for c in comparacoes:
        linhas.append(f"| `{c['a']}` − `{c['b']}` | {c['dif_pp']:+.1f} | [{c['ic95_pp'][0]:+.1f}, {c['ic95_pp'][1]:+.1f}] |")

    linhas += ["", "## 4. Distribuição das categorias previstas por condição (viés de colapso)", ""]
    cols = CODIGOS_VALIDOS + ["sem_resposta"]
    linhas.append("| Condição | " + " | ".join(f"`{c}`" for c in cols) + " |")
    linhas.append("|:---|" + "|".join(["---:"] * len(cols)) + "|")
    gt_dist = Counter(y_true)
    linhas.append("| **GT real (professores)** | " + " | ".join(str(gt_dist[c]) for c in cols) + " |")
    for cod, _ in CONDICOES_ORDEM:
        if cod not in resumo:
            continue
        dp = resumo[cod]["dist_pred"]
        linhas.append(f"| `{cod}` | " + " | ".join(str(dp.get(c, 0)) for c in cols) + " |")

    linhas += ["", "## 5. F1 por classe nas principais condições", ""]
    conds_f1 = [c for c in ["A1_regra", "B1_texto_qwen25_1.5b", "B2_texto_gemma2_2b", "C1_visao_qwen25vl_3b"] if c in resumo]
    linhas.append("| Categoria GT (suporte) | " + " | ".join(f"`{c}`" for c in conds_f1) + " |")
    linhas.append("|:---|" + "|".join(["---:"] * len(conds_f1)) + "|")
    for c in CODIGOS_VALIDOS:
        sup = gt_dist[c]
        vals = [f"{resumo[cond]['por_classe'][c]['f1']:.2f} ({resumo[cond]['por_classe'][c]['tp']}/{sup})" for cond in conds_f1]
        linhas.append(f"| `{c}` ({sup}) | " + " | ".join(vals) + " |")

    # Salva JSON e Markdown
    metricas_json = {
        "n": n,
        "majority_baseline": {"codigo": maj_cod, "acc": maj_acc, "ic95": [maj_lo, maj_hi], "f1_macro": maj_f1},
        "ocr_sympy_status": dict(ocr_stats),
        "regra_atlas_dist": dict(regra_atlas_stats),
        "condicoes": {k: {kk: vv for kk, vv in v.items() if kk != "hits"} for k, v in resumo.items()},
        "ece_local": ece_resumo,
        "comparacoes": comparacoes,
    }
    (RES / "metricas.json").write_text(json.dumps(metricas_json, ensure_ascii=False, indent=2), encoding="utf-8")
    rel_path = RES / "relatorio.md"
    rel_path.write_text("\n".join(linhas), encoding="utf-8")
    print(f"Relatório salvo em: {rel_path}")
    print("\n".join(linhas[:55]))


if __name__ == "__main__":
    main()
