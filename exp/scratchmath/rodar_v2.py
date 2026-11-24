"""Experimento Ciclo V2 — Escopo (57 equações 1º grau) + 4 OCRs no Passo 1 + Tradução PT-BR (241 folhas).

Fases:
  1) Comparação de OCR no Passo 1 (`N = 57` equações do 1º grau):
       - Pix2Text (dedicado, CPU)
       - Qwen2.5-VL 3B (transcritor literal puro)
       - Qwen2.5-VL 7B (transcritor literal puro)
     (Comparados contra TrOCR-printed de V1 = 0/57.)
  2) Pipeline Atlas V2 no escopo (`N = 57`, usando o melhor OCR + texto em PT-BR):
       - V2_A1_regra (SymPy + Regra das correções típicas)
       - V2_A2_atlas_qwen25_1.5b (pós-OCR+SymPy)
       - V2_A3_atlas_gemma2_2b (pós-OCR+SymPy)
       - V2_A4_atlas_qwen25_7b (pós-OCR+SymPy)
       - V2_B1_ocr_pt_qwen25_1.5b (Passo 3 em PT-BR + transcrição OCR)
       - V2_B2_ocr_pt_gemma2_2b (Passo 3 em PT-BR + transcrição OCR)
       - V2_B3_ocr_pt_qwen25_7b (Passo 3 em PT-BR + transcrição OCR)
  3) Benchmark Completo em PT-BR (`N = 241`, comparando V1 chinês vs V2 PT-BR e artigo):
       - V2_FULL_B1_pt_qwen25_1.5b
       - V2_FULL_B2_pt_gemma2_2b
       - V2_FULL_C2_visao_pt_qwen25vl_7b (lendo a foto real + PT-BR)
"""
import argparse
import base64
import io
import json
from pathlib import Path
import re
import time
import urllib.error
import urllib.request

from PIL import Image

from categorias import CATEGORIAS_SCRATCHMATH, CODIGOS_VALIDOS
from regra import diagnosticar_sympy, parse_equacao, raizes, rodar_regra_completa

AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "dados"
RES = AQUI / "resultados_v2"
OLLAMA = "http://localhost:11434"

LISTA_CATS_PROMPT = "\n".join(
    f"- {c['codigo']} ({c['pt']}): {c['descricao']}"
    for c in CATEGORIAS_SCRATCHMATH
)

ESQUEMA_OCR = {
    "type": "object",
    "properties": {
        "linhas": {
            "type": "array",
            "items": {"type": "string"},
        }
    },
    "required": ["linhas"],
}

ESQUEMA_SAIDA = {
    "type": "object",
    "properties": {
        "categoria_erro": {"type": "string", "enum": CODIGOS_VALIDOS},
        "explicacao_erro": {"type": "string"},
        "dica_aluno": {"type": "string"},
    },
    "required": ["categoria_erro", "explicacao_erro", "dica_aluno"],
}


def carregar_jsonl(path: Path):
    if not path.exists():
        return []
    return [json.loads(l) for l in path.open("r", encoding="utf-8") if l.strip()]


def carregar_checkpoint(path: Path):
    return {r["idx"]: r for r in carregar_jsonl(path)}


def anexar_jsonl(path: Path, obj: dict):
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def imagem_para_b64(img_path: Path, max_lado=1280) -> str:
    img = Image.open(img_path).convert("RGB")
    w, h = img.size
    maior = max(w, h)
    if maior > max_lado:
        escala = max_lado / maior
        img = img.resize((int(w * escala), int(h * escala)), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=88)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def extrair_equacao_enunciado(q: str):
    """Tenta extrair a equação em x do enunciado (ex.: $4x - 3(20 - x) = 6x - 7(9 - x)$)."""
    for bloco in re.findall(r"\$([^$]+)\$", q):
        if "=" in bloco and "x" in bloco.lower():
            if parse_equacao(bloco) is not None:
                return bloco.strip()
    return None


def montar_resposta_aluno_como_eq(student_answer: str):
    s = (student_answer or "").strip().replace("$", "")
    if not s or "," in s or '"' in s or "或" in s:
        return None
    cand = s if "=" in s else f"x = {s}"
    if parse_equacao(cand) is not None:
        return cand
    return None


def avaliar_linhas_com_sympy(linhas_raw, reg):
    """Avalia linhas transcritas de duas formas:
    - `so_rascunho`: só as equações válidas extraídas da foto (puro).
    - `completo`: [eq_enunciado?] + linhas válidas da foto + [x = student_answer?].
    """
    linhas_limpas = [l.strip() for l in linhas_raw if isinstance(l, str) and l.strip()]
    linhas_validas = [l for l in linhas_limpas if parse_equacao(l) is not None]

    # 1. Puro (só o que o OCR leu)
    res_puro = rodar_regra_completa(linhas_limpas)

    # 2. Com filtragem de linhas parseáveis + âncoras do enunciado e resposta final do aluno
    seq = []
    eq0 = extrair_equacao_enunciado(reg["question"])
    if eq0:
        seq.append(eq0)
    for lv in linhas_validas:
        if not seq or lv != seq[-1]:
            seq.append(lv)
    eq_fim = montar_resposta_aluno_como_eq(reg["student_answer"])
    if eq_fim and (not seq or raizes(eq_fim) != raizes(seq[-1])):
        seq.append(eq_fim)

    res_ancorado = rodar_regra_completa(seq) if len(seq) >= 2 else {
        "status_sympy": "ilegivel",
        "linha_quebra": 1,
        "diag_texto": "menos de 2 equações legíveis",
        "categoria_atlas": "outro",
        "categoria_scratchmath": None,
        "dica_aluno": "",
    }
    return {
        "linhas_ocr": linhas_limpas,
        "n_linhas_ocr": len(linhas_limpas),
        "n_linhas_validas_sympy": len(linhas_validas),
        "puro": res_puro,
        "ancorado": res_ancorado,
        "seq_ancorada": seq,
    }


def chamar_ollama_json(modelo: str, prompt: str, esquema: dict, imagem_b64: str = None, num_predict=380, timeout=180):
    msg = {"role": "user", "content": prompt}
    if imagem_b64:
        msg["images"] = [imagem_b64]
    corpo = {
        "model": modelo,
        "stream": False,
        "messages": [msg],
        "format": esquema,
        "options": {"temperature": 0, "num_predict": num_predict},
    }
    req = urllib.request.Request(
        f"{OLLAMA}/api/chat",
        data=json.dumps(corpo).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            r = json.loads(resp.read().decode("utf-8"))
        dt = time.perf_counter() - t0
        conteudo = r.get("message", {}).get("content", "")
        try:
            return True, json.loads(conteudo), conteudo, round(dt, 3), None
        except json.JSONDecodeError:
            return False, {}, conteudo, round(dt, 3), "json_invalido"
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return False, {}, "", round(time.perf_counter() - t0, 3), str(e)


# ================= FASE 1: BENCHMARK DE OCRs NO PASSO 1 (N = 57) =================

def extrair_linhas_pix2text(texto: str):
    """Extrai linhas/equações com '=' da saída Markdown/LaTeX do Pix2Text, limpando ambientes matrix/aligned."""
    if not texto:
        return []
    bruto = texto.replace("$$", "\n").replace("\\\\", "\n")
    bruto = re.sub(r"\\begin\{[a-zA-Z*]+\}(?:\{[^{}]*\})?", "", bruto)
    bruto = re.sub(r"\\end\{[a-zA-Z*]+\}", "", bruto)
    bruto = bruto.replace("&", " ")
    candidatas = []
    for parte in bruto.splitlines():
        parte = parte.strip().strip("$").strip()
        if not parte:
            continue
        # Junta dígitos separados por espaço único típico de LaTeX OCR (ex.: "6 0" -> "60")
        parte = re.sub(r"(?<=\d)\s+(?=\d)", "", parte)
        if "=" in parte:
            candidatas.append(parte)
    return candidatas


def rodar_ocr_pix2text(escopo):
    out_path = RES / "OCR_pix2text.jsonl"
    feitos = carregar_checkpoint(out_path)
    pendentes = [r for r in escopo if r["idx"] not in feitos]
    if not pendentes:
        print(f"[OCR_pix2text] já concluído ({len(feitos)} casos).")
        return feitos

    print(f"[OCR_pix2text] carregando Pix2Text (CPU) para {len(pendentes)} imagens...")
    from pix2text import Pix2Text
    p2t = Pix2Text.from_config(device="cpu")

    t_ini = time.perf_counter()
    for n, reg in enumerate(pendentes, 1):
        img_path = str(AQUI / reg["image_path"])
        t0 = time.perf_counter()
        try:
            bruto = p2t.recognize_text_formula(img_path, return_text=True)
            erro = None
        except Exception as e:
            bruto = ""
            erro = str(e)
        dt = round(time.perf_counter() - t0, 3)
        linhas = extrair_linhas_pix2text(bruto)
        aval = avaliar_linhas_com_sympy(linhas, reg)
        item = {
            "idx": reg["idx"],
            "question_id": reg["question_id"],
            "gt_codigo": reg["error_category_codigo"],
            "ocr_modelo": "pix2text",
            "bruto_ocr": bruto,
            "erro_ocr": erro,
            "tempo_ocr_s": dt,
            **aval,
        }
        anexar_jsonl(out_path, item)
        feitos[reg["idx"]] = item
        if n % 10 == 0 or n == len(pendentes):
            print(f"  OCR_pix2text: {n}/{len(pendentes)} ({time.perf_counter() - t_ini:.1f}s)")
    return feitos


def rodar_ocr_vlm(nome_arq: str, modelo: str, escopo):
    out_path = RES / f"{nome_arq}.jsonl"
    feitos = carregar_checkpoint(out_path)
    pendentes = [r for r in escopo if r["idx"] not in feitos]
    if not pendentes:
        print(f"[{nome_arq}] já concluído ({len(feitos)} casos).")
        return feitos

    prompt_ocr = (
        "Você é um motor de OCR matemático literal.\n"
        "Transcreva SOMENTE as equações manuscritas que o aluno escreveu nesta imagem, na ordem de cima para baixo.\n"
        "REGRAS ESTRITAS:\n"
        "- NÃO corrija nenhum erro do aluno! Copie exatamente o que está escrito na imagem.\n"
        "- Escreva cada linha como uma equação limpa usando sintaxe simples ou LaTeX (ex.: '4x - 60 + 3x = 6x - 63 + 7x', '-6x = -3', 'x = -1/2').\n"
        "- Ignore rabiscos soltos e anotações sem sinal de igual.\n"
        '- Responda APENAS JSON: {"linhas": ["equacao_1", "equacao_2", ...]}'
    )

    print(f"[{nome_arq}] rodando {modelo} como transcritor puro em {len(pendentes)} imagens...")
    t_ini = time.perf_counter()
    for n, reg in enumerate(pendentes, 1):
        b64 = imagem_para_b64(AQUI / reg["image_path"], max_lado=1280)
        ok, parsed, bruto, dt, err = chamar_ollama_json(modelo, prompt_ocr, ESQUEMA_OCR, imagem_b64=b64, num_predict=350)
        linhas = parsed.get("linhas", []) if ok and isinstance(parsed.get("linhas"), list) else []
        aval = avaliar_linhas_com_sympy(linhas, reg)
        item = {
            "idx": reg["idx"],
            "question_id": reg["question_id"],
            "gt_codigo": reg["error_category_codigo"],
            "ocr_modelo": modelo,
            "bruto_ocr": bruto,
            "erro_ocr": err,
            "tempo_ocr_s": dt,
            **aval,
        }
        anexar_jsonl(out_path, item)
        feitos[reg["idx"]] = item
        if n % 10 == 0 or n == len(pendentes):
            print(f"  {nome_arq}: {n}/{len(pendentes)} ({time.perf_counter() - t_ini:.1f}s)")
    return feitos


# ================= FASES 2 & 3: PASSO 3 EM PT-BR (N=57 E N=241) =================

def montar_prompt_v2(reg_pt, modo: str, ocr_item=None):
    q = reg_pt["question_pt"]
    sol = reg_pt["solution_pt"]
    ans = reg_pt["answer"]
    stu = reg_pt["student_answer"]

    if modo == "atlas_sympy":
        anc = ocr_item["ancorado"]
        return (
            "Você é um tutor diagnóstico de matemática do 7º ao 9º ano.\n"
            "O OCR transcreveu o rascunho manuscrito do aluno e o verificador algébrico SymPy apontou a linha da quebra.\n"
            "Classifique a causa principal do erro em EXATAMENTE UMA das 7 categorias abaixo.\n"
            "Escreva explicacao_erro (para o professor, em português) e dica_aluno (pista curta para o aluno SEM revelar a resposta final).\n\n"
            f"Categorias válidas:\n{LISTA_CATS_PROMPT}\n\n"
            f"Enunciado: {q}\n"
            f"Passos transcritos do rascunho: {ocr_item['seq_ancorada']}\n"
            f"Diagnóstico SymPy: {anc['diag_texto']}\n"
            f"Resposta final do aluno: {stu}\n\n"
            'Responda APENAS JSON válido: {"categoria_erro": "...", "explicacao_erro": "...", "dica_aluno": "..."}'
        )

    bloco_ocr = ""
    if modo == "contexto_ocr" and ocr_item is not None:
        bloco_ocr = f"Passos transcritos do rascunho manuscrito: {ocr_item['linhas_ocr']}\n"
        if ocr_item["ancorado"]["status_sympy"] == "quebra":
            bloco_ocr += f"Quebra apontada pelo SymPy: {ocr_item['ancorado']['diag_texto']}\n"

    origem = (
        "Analise a foto real do rascunho manuscrito do aluno junto com o enunciado, a solução correta e a resposta final."
        if modo == "visao_pt"
        else (
            "Analise o enunciado, a solução correta, a resposta final do aluno e os passos transcritos do rascunho manuscrito."
            if modo == "contexto_ocr"
            else "Analise o enunciado em português, a solução correta e a resposta final do aluno."
        )
    )
    return (
        "Você é um professor de matemática do 7º ao 9º ano avaliando um erro real de aluno (benchmark ScratchMath).\n"
        f"{origem}\n"
        "Classifique a causa principal do erro em EXATAMENTE UMA das 7 categorias abaixo.\n"
        "Atenção: não chute sempre a mesma categoria — diferencie erro de cálculo, erro de transcrição/cópia, "
        "erro de atenção/detalhe (ex.: esqueceu um sinal), lacuna de conhecimento/regra, compreensão do enunciado, estratégia ou raciocínio.\n"
        "Escreva:\n"
        "1) categoria_erro: um dos 7 códigos exatos.\n"
        "2) explicacao_erro: explicação curta em português do erro principal (para o professor).\n"
        "3) dica_aluno: pista pedagógica curta em português para o aluno revisar sozinho SEM revelar a resposta final.\n\n"
        f"Categorias válidas:\n{LISTA_CATS_PROMPT}\n\n"
        f"Enunciado: {q}\n"
        f"Resposta correta: {ans}\n"
        f"Solução de referência: {sol}\n"
        f"Resposta final do aluno: {stu}\n"
        f"{bloco_ocr}\n"
        'Responda APENAS JSON válido: {"categoria_erro": "...", "explicacao_erro": "...", "dica_aluno": "..."}'
    )


def rodar_condicao_v2(nome_cond: str, modelo: str, modo: str, registros_pt, ocr_map=None):
    out_path = RES / f"{nome_cond}.jsonl"
    feitos = carregar_checkpoint(out_path)
    pendentes = [r for r in registros_pt if r["idx"] not in feitos]
    if not pendentes:
        print(f"[{nome_cond}] já concluído ({len(feitos)} casos).")
        return

    print(f"[{nome_cond}] rodando {modelo} (modo={modo}) em {len(pendentes)} casos...")
    t_ini = time.perf_counter()
    for n, reg in enumerate(pendentes, 1):
        ocr_item = ocr_map[reg["idx"]] if ocr_map else None

        if modo == "regra_ocr":
            anc = ocr_item["ancorado"]
            item = {
                "idx": reg["idx"],
                "question_id": reg["question_id"],
                "gt_codigo": reg["error_category_codigo"],
                "status_sympy": anc["status_sympy"],
                "chamou_llm": False,
                "categoria_atlas": anc["categoria_atlas"],
                "categoria_scratchmath": anc["categoria_scratchmath"],
                "explicacao_erro": f"{anc['diag_texto']} (regra: {anc['categoria_atlas']})",
                "dica_aluno": anc["dica_aluno"],
                "tempo_s": ocr_item["tempo_ocr_s"],
            }
            anexar_jsonl(out_path, item)
            continue

        if modo == "atlas_sympy":
            anc = ocr_item["ancorado"]
            if anc["status_sympy"] != "quebra":
                item = {
                    "idx": reg["idx"],
                    "question_id": reg["question_id"],
                    "gt_codigo": reg["error_category_codigo"],
                    "status_sympy": anc["status_sympy"],
                    "chamou_llm": False,
                    "categoria_scratchmath": None,
                    "explicacao_erro": anc["diag_texto"],
                    "dica_aluno": "",
                    "tempo_s": ocr_item["tempo_ocr_s"],
                }
                anexar_jsonl(out_path, item)
                continue

        prompt = montar_prompt_v2(reg, modo, ocr_item)
        b64 = imagem_para_b64(AQUI / reg["image_path"], max_lado=1024) if modo == "visao_pt" else None
        ok, parsed, bruto, dt, err = chamar_ollama_json(modelo, prompt, ESQUEMA_SAIDA, imagem_b64=b64, num_predict=360)
        cat = parsed.get("categoria_erro") if ok else None
        if cat not in CODIGOS_VALIDOS:
            cat = None
        item = {
            "idx": reg["idx"],
            "question_id": reg["question_id"],
            "gt_codigo": reg["error_category_codigo"],
            "chamou_llm": True,
            "ok": ok,
            "categoria_scratchmath": cat,
            "explicacao_erro": parsed.get("explicacao_erro", "") if ok else "",
            "dica_aluno": parsed.get("dica_aluno", "") if ok else "",
            "bruto": bruto,
            "erro": err,
            "tempo_s": dt,
        }
        anexar_jsonl(out_path, item)
        if n % 20 == 0 or n == len(pendentes):
            print(f"  {nome_cond}: {n}/{len(pendentes)} ({time.perf_counter() - t_ini:.1f}s)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fase", choices=["ocr", "escopo", "full", "todas"], default="todas")
    args = parser.parse_args()

    RES.mkdir(parents=True, exist_ok=True)
    middle_pt = carregar_jsonl(DADOS / "middle_pt.jsonl")
    if len(middle_pt) < 241:
        raise SystemExit(f"middle_pt.jsonl tem apenas {len(middle_pt)}/241 linhas. Conclua preparar_v2.py primeiro.")
    pt_por_idx = {r["idx"]: r for r in middle_pt}
    escopo_idxs = [r["idx"] for r in carregar_jsonl(DADOS / "escopo_1grau.jsonl")]
    escopo_pt = [pt_por_idx[i] for i in escopo_idxs]
    print(f"Carregados {len(middle_pt)} casos PT-BR | Escopo 1º grau: {len(escopo_pt)} casos.")

    ocr_map_melhor = None
    if args.fase in ("ocr", "escopo", "todas"):
        ocr_p2t = rodar_ocr_pix2text(escopo_pt)
        ocr_3b = rodar_ocr_vlm("OCR_qwen25vl_3b", "qwen2.5vl:3b", escopo_pt)
        ocr_7b = rodar_ocr_vlm("OCR_qwen25vl_7b", "qwen2.5vl:7b", escopo_pt)

        # Escolhe automaticamente o OCR com maior número de quebras válidas no SymPy ancorado
        candidatos = [
            ("OCR_qwen25vl_7b", ocr_7b),
            ("OCR_qwen25vl_3b", ocr_3b),
            ("OCR_pix2text", ocr_p2t),
        ]
        melhor_nome, ocr_map_melhor = max(
            candidatos,
            key=lambda kv: sum(1 for v in kv[1].values() if v["ancorado"]["status_sympy"] == "quebra"),
        )
        q_melhor = sum(1 for v in ocr_map_melhor.values() if v["ancorado"]["status_sympy"] == "quebra")
        print(f">>> OCR vencedor para Fase 2: {melhor_nome} ({q_melhor}/{len(escopo_pt)} quebras SymPy)")
        (RES / "ocr_vencedor.txt").write_text(melhor_nome, encoding="utf-8")

    if args.fase in ("escopo", "todas"):
        # Fase 2: Pipeline Atlas V2 no escopo de 57 equações do 1º grau
        rodar_condicao_v2("V2_A1_regra", None, "regra_ocr", escopo_pt, ocr_map_melhor)
        rodar_condicao_v2("V2_A2_atlas_qwen25_1.5b", "qwen2.5:1.5b", "atlas_sympy", escopo_pt, ocr_map_melhor)
        rodar_condicao_v2("V2_A3_atlas_gemma2_2b", "gemma2:2b", "atlas_sympy", escopo_pt, ocr_map_melhor)
        rodar_condicao_v2("V2_A4_atlas_qwen25_7b", "qwen2.5:7b", "atlas_sympy", escopo_pt, ocr_map_melhor)
        rodar_condicao_v2("V2_B1_ocr_pt_qwen25_1.5b", "qwen2.5:1.5b", "contexto_ocr", escopo_pt, ocr_map_melhor)
        rodar_condicao_v2("V2_B2_ocr_pt_gemma2_2b", "gemma2:2b", "contexto_ocr", escopo_pt, ocr_map_melhor)
        rodar_condicao_v2("V2_B3_ocr_pt_qwen25_7b", "qwen2.5:7b", "contexto_ocr", escopo_pt, ocr_map_melhor)

    if args.fase in ("full", "todas"):
        # Fase 3: Benchmark completo em PT-BR (241 folhas)
        rodar_condicao_v2("V2_FULL_B1_pt_qwen25_1.5b", "qwen2.5:1.5b", "contexto_pt", middle_pt)
        rodar_condicao_v2("V2_FULL_B2_pt_gemma2_2b", "gemma2:2b", "contexto_pt", middle_pt)
        rodar_condicao_v2("V2_FULL_C2_visao_pt_qwen25vl_7b", "qwen2.5vl:7b", "visao_pt", middle_pt)

    print("Ciclo V2 concluído.")


if __name__ == "__main__":
    main()
