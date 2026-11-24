"""Etapas 3 e 4: executa o benchmark completo do Atlas sobre songdj/ScratchMath (middle, 241 folhas).

Condições executadas (todas com temperature=0 e JSON Schema fechado nas 7 categorias oficiais):
  - Etapa OCR+SymPy (1x por imagem): recorte por vãos + microsoft/trocr-small-printed + SymPy
    -> produz automaticamente `A1_regra` (Atlas completo com Regra das correções típicas)
  - Camada A (Atlas ponta a ponta — só classifica quando SymPy acha quebra):
      * `A2_atlas_qwen25_1.5b`
      * `A3_atlas_gemma2_2b`
  - Camada B (Contexto do artigo + texto OCR — isola o Passo 3 sem o gargalo do SymPy):
      * `B1_texto_qwen25_1.5b`
      * `B2_texto_gemma2_2b`
  - Camada C (Multimodal local — lê a foto direto + contexto do artigo, estilo Song et al.):
      * `C1_visao_qwen3_vl_4b`

Suporta --limite N (smoke test) e retomada automática por checkpoint em resultados/*.jsonl.
"""
import argparse
import base64
import io
import json
from pathlib import Path
import time
import urllib.error
import urllib.request

from PIL import Image
import torch
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

from categorias import CATEGORIAS_SCRATCHMATH, CODIGOS_VALIDOS
from regra import recortar_por_vaos, rodar_regra_completa

AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "dados"
RES = AQUI / "resultados"
OLLAMA = "http://localhost:11434"
MODELO_OCR = "microsoft/trocr-small-printed"

LISTA_CATS_PROMPT = "\n".join(
    f"- {c['codigo']} ({c['pt']} / {c['zh']}): {c['descricao']}"
    for c in CATEGORIAS_SCRATCHMATH
)

ESQUEMA_SAIDA = {
    "type": "object",
    "properties": {
        "categoria_erro": {"type": "string", "enum": CODIGOS_VALIDOS},
        "explicacao_erro": {"type": "string"},
        "dica_aluno": {"type": "string"},
    },
    "required": ["categoria_erro", "explicacao_erro", "dica_aluno"],
}


def montar_prompt_atlas(reg, linhas_ocr, diag_texto):
    return (
        "Você é um tutor diagnóstico de matemática do ensino fundamental II (7º ao 9º ano).\n"
        "O sistema leu o caderno manuscrito do aluno com OCR e o verificador algébrico SymPy apontou uma quebra.\n"
        "Classifique a causa principal do erro em EXATAMENTE UMA das 7 categorias abaixo, explique brevemente o erro "
        "(explicacao_erro) e escreva uma dica curta em português para o aluno revisar sozinho SEM revelar a resposta final (dica_aluno).\n\n"
        f"Categorias válidas:\n{LISTA_CATS_PROMPT}\n\n"
        f"Passos lidos pelo OCR: {linhas_ocr}\n"
        f"Diagnóstico SymPy: {diag_texto}\n"
        f"Enunciado da questão: {reg['question']}\n"
        f"Resposta final do aluno: {reg['student_answer']}\n\n"
        'Responda APENAS JSON válido: {"categoria_erro": "...", "explicacao_erro": "...", "dica_aluno": "..."}'
    )


def montar_prompt_contexto(reg, com_imagem=False):
    origem = (
        "Analise a foto do rascunho manuscrito do aluno junto com o enunciado, a solução correta e a resposta final do aluno."
        if com_imagem
        else "Analise o enunciado, a solução correta e a resposta final do aluno (sem ver o rascunho manuscrito)."
    )
    return (
        "Você é um professor de matemática do 7º ao 9º ano avaliando um erro real de aluno (benchmark ScratchMath).\n"
        f"{origem}\n"
        "Classifique a causa principal do erro em EXATAMENTE UMA das 7 categorias abaixo.\n"
        "Escreva:\n"
        "1) categoria_erro: um dos 7 códigos exatos.\n"
        "2) explicacao_erro: explicação curta em português de onde e por que o aluno errou (para o professor).\n"
        "3) dica_aluno: pista pedagógica curta em português que ajude o aluno a encontrar o erro SEM dar a resposta final.\n\n"
        f"Categorias válidas:\n{LISTA_CATS_PROMPT}\n\n"
        f"Enunciado: {reg['question']}\n"
        f"Resposta correta: {reg['answer']}\n"
        f"Solução de referência: {reg['solution']}\n"
        f"Resposta final do aluno: {reg['student_answer']}\n\n"
        'Responda APENAS JSON válido: {"categoria_erro": "...", "explicacao_erro": "...", "dica_aluno": "..."}'
    )


def carregar_middle(limite=None):
    registros = []
    with (DADOS / "middle.jsonl").open("r", encoding="utf-8") as f:
        for linha in f:
            if linha.strip():
                registros.append(json.loads(linha))
    return registros[:limite] if limite else registros


def carregar_checkpoint(path: Path):
    feitos = {}
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            for linha in f:
                if linha.strip():
                    obj = json.loads(linha)
                    feitos[obj["idx"]] = obj
    return feitos


def anexar_jsonl(path: Path, obj: dict):
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def imagem_para_b64(img_path: Path, max_lado=1024) -> str:
    img = Image.open(img_path).convert("RGB")
    w, h = img.size
    maior = max(w, h)
    if maior > max_lado:
        escala = max_lado / maior
        img = img.resize((int(w * escala), int(h * escala)), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def chamar_ollama(modelo: str, prompt: str, imagem_b64: str = None, timeout=180):
    msg = {"role": "user", "content": prompt}
    if imagem_b64:
        msg["images"] = [imagem_b64]
    num_pred = 380
    corpo = {
        "model": modelo,
        "stream": False,
        "messages": [msg],
        "format": ESQUEMA_SAIDA,
        "options": {"temperature": 0, "num_predict": num_pred},
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
            parsed = json.loads(conteudo)
            cat = parsed.get("categoria_erro")
            if cat not in CODIGOS_VALIDOS:
                cat = None
            return {
                "ok": True,
                "categoria_scratchmath": cat,
                "explicacao_erro": parsed.get("explicacao_erro", ""),
                "dica_aluno": parsed.get("dica_aluno", ""),
                "bruto": conteudo,
                "tempo_s": round(dt, 3),
            }
        except json.JSONDecodeError:
            return {
                "ok": False,
                "categoria_scratchmath": None,
                "explicacao_erro": "",
                "dica_aluno": "",
                "bruto": conteudo,
                "erro": "json_invalido",
                "tempo_s": round(dt, 3),
            }
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        dt = time.perf_counter() - t0
        return {
            "ok": False,
            "categoria_scratchmath": None,
            "explicacao_erro": "",
            "dica_aluno": "",
            "bruto": "",
            "erro": str(e),
            "tempo_s": round(dt, 3),
        }


def rodar_ocr_e_regra(registros):
    """Roda TrOCR + SymPy + Regra 1x por imagem (com checkpoint)."""
    out_path = RES / "A1_regra.jsonl"
    feitos = carregar_checkpoint(out_path)
    pendentes = [r for r in registros if r["idx"] not in feitos]
    if not pendentes:
        print(f"[A1_regra / OCR+SymPy] já concluído ({len(feitos)} casos).")
        return feitos

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[A1_regra / OCR+SymPy] carregando {MODELO_OCR} em {device} para {len(pendentes)} imagens...")
    processor = TrOCRProcessor.from_pretrained(MODELO_OCR)
    model = VisionEncoderDecoderModel.from_pretrained(MODELO_OCR).to(device)
    model.eval()

    t_ini = time.perf_counter()
    for n, reg in enumerate(pendentes, 1):
        img_path = AQUI / reg["image_path"]
        img = Image.open(img_path).convert("RGB")
        t0 = time.perf_counter()
        faixas = recortar_por_vaos(img)
        # Limita a 15 faixas por imagem para evitar explosão em rascunhos muito fragmentados
        faixas_ocr = faixas[:15]
        if faixas_ocr:
            pixel_values = processor(images=faixas_ocr, return_tensors="pt").pixel_values.to(device)
            with torch.no_grad():
                ids = model.generate(pixel_values, max_new_tokens=48)
            linhas = processor.batch_decode(ids, skip_special_tokens=True)
        else:
            linhas = []
        t_ocr = time.perf_counter() - t0

        t1 = time.perf_counter()
        res_regra = rodar_regra_completa(linhas)
        t_regra = time.perf_counter() - t1

        item = {
            "idx": reg["idx"],
            "question_id": reg["question_id"],
            "gt_codigo": reg["error_category_codigo"],
            "n_faixas_total": len(faixas),
            "linhas_ocr": linhas,
            "status_sympy": res_regra["status_sympy"],
            "linha_quebra": res_regra["linha_quebra"],
            "diag_texto": res_regra["diag_texto"],
            "categoria_atlas": res_regra["categoria_atlas"],
            "categoria_scratchmath": res_regra["categoria_scratchmath"],
            "explicacao_erro": f"{res_regra['diag_texto']} (regra: {res_regra['categoria_atlas']})",
            "dica_aluno": res_regra["dica_aluno"],
            "t_ocr_s": round(t_ocr, 3),
            "tempo_s": round(t_ocr + t_regra, 3),
        }
        anexar_jsonl(out_path, item)
        feitos[reg["idx"]] = item
        if n % 25 == 0 or n == len(pendentes):
            dt_tot = time.perf_counter() - t_ini
            print(f"  OCR+Regra: {n}/{len(pendentes)} ({dt_tot:.1f}s)")

    # Libera memória da GPU antes de rodar Ollama
    del model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    return feitos


def rodar_condicao_llm(nome_cond: str, modelo: str, modo: str, registros, ocr_map):
    """modo in {'atlas', 'contexto', 'visao'}."""
    out_path = RES / f"{nome_cond}.jsonl"
    feitos = carregar_checkpoint(out_path)
    pendentes = [r for r in registros if r["idx"] not in feitos]
    if not pendentes:
        print(f"[{nome_cond}] já concluído ({len(feitos)} casos).")
        return

    print(f"[{nome_cond}] rodando {modelo} (modo={modo}) em {len(pendentes)} casos...")
    t_ini = time.perf_counter()
    for n, reg in enumerate(pendentes, 1):
        ocr = ocr_map[reg["idx"]]
        if modo == "atlas":
            # Na pipeline Atlas, o passo 3 só roda se o SymPy apontar quebra
            if ocr["status_sympy"] != "quebra":
                item = {
                    "idx": reg["idx"],
                    "question_id": reg["question_id"],
                    "gt_codigo": reg["error_category_codigo"],
                    "status_sympy": ocr["status_sympy"],
                    "chamou_llm": False,
                    "categoria_scratchmath": None,
                    "explicacao_erro": ocr["diag_texto"],
                    "dica_aluno": "",
                    "tempo_s": ocr["t_ocr_s"],
                }
                anexar_jsonl(out_path, item)
                continue
            prompt = montar_prompt_atlas(reg, ocr["linhas_ocr"], ocr["diag_texto"])
            resp = chamar_ollama(modelo, prompt)
            item = {
                "idx": reg["idx"],
                "question_id": reg["question_id"],
                "gt_codigo": reg["error_category_codigo"],
                "status_sympy": ocr["status_sympy"],
                "chamou_llm": True,
                **resp,
                "tempo_total_com_ocr_s": round(ocr["t_ocr_s"] + resp["tempo_s"], 3),
            }
        elif modo == "contexto":
            prompt = montar_prompt_contexto(reg, com_imagem=False)
            resp = chamar_ollama(modelo, prompt)
            item = {
                "idx": reg["idx"],
                "question_id": reg["question_id"],
                "gt_codigo": reg["error_category_codigo"],
                "chamou_llm": True,
                **resp,
            }
        elif modo == "visao":
            prompt = montar_prompt_contexto(reg, com_imagem=True)
            b64 = imagem_para_b64(AQUI / reg["image_path"], max_lado=1024)
            resp = chamar_ollama(modelo, prompt, imagem_b64=b64)
            item = {
                "idx": reg["idx"],
                "question_id": reg["question_id"],
                "gt_codigo": reg["error_category_codigo"],
                "chamou_llm": True,
                **resp,
            }
        else:
            raise ValueError(f"Modo desconhecido: {modo}")

        anexar_jsonl(out_path, item)
        if n % 20 == 0 or n == len(pendentes):
            dt_tot = time.perf_counter() - t_ini
            print(f"  {nome_cond}: {n}/{len(pendentes)} ({dt_tot:.1f}s)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limite", type=int, default=None, help="Limita ao primeiro N casos (smoke test)")
    parser.add_argument("--sem-visao", action="store_true", help="Pula C1_visao_qwen3_vl_4b")
    args = parser.parse_args()

    RES.mkdir(parents=True, exist_ok=True)
    registros = carregar_middle(args.limite)
    print(f"Carregados {len(registros)} casos de middle.jsonl")

    # 1. OCR + SymPy + Regra (Camada A1)
    ocr_map = rodar_ocr_e_regra(registros)

    # 2. Camada A — Atlas completo (Qwen vs Gemma somente onde SymPy detecta quebra)
    rodar_condicao_llm("A2_atlas_qwen25_1.5b", "qwen2.5:1.5b", "atlas", registros, ocr_map)
    rodar_condicao_llm("A3_atlas_gemma2_2b", "gemma2:2b", "atlas", registros, ocr_map)

    # 3. Camada B — Passo 3 isolado (contexto completo do artigo + texto OCR)
    rodar_condicao_llm("B1_texto_qwen25_1.5b", "qwen2.5:1.5b", "contexto", registros, ocr_map)
    rodar_condicao_llm("B2_texto_gemma2_2b", "gemma2:2b", "contexto", registros, ocr_map)

    # 4. Camada C — Multimodal local lendo a foto real direto
    if not args.sem_visao:
        rodar_condicao_llm("C1_visao_qwen25vl_3b", "qwen2.5vl:3b", "visao", registros, ocr_map)

    print("Execução concluída.")


if __name__ == "__main__":
    main()
