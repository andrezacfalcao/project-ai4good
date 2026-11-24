"""Etapa V2.1 + V2.2:
1) Congela o recorte `dados/escopo_1grau.jsonl` (equações do 1º grau do ScratchMath middle).
2) Traduz `question`, `solution` e `error_explanation` das 241 amostras de chinês -> português
   usando `qwen2.5:7b` localmente no Ollama (Opção B, custo zero, com checkpoint em `dados/middle_pt.jsonl`).
"""
import json
from pathlib import Path
import re
import time
import urllib.request

AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "dados"
OLLAMA = "http://localhost:11434"
MODELO_TRAD = "qwen2.5:7b"

ESQUEMA_TRAD = {
    "type": "object",
    "properties": {
        "question_pt": {"type": "string"},
        "solution_pt": {"type": "string"},
        "error_explanation_pt": {"type": "string"},
    },
    "required": ["question_pt", "solution_pt", "error_explanation_pt"],
}


def classificar_subconjunto(reg: dict) -> str:
    q, sol = reg["question"], reg["solution"]
    if re.search(r"一元二次|x\^2|x\^\{2\}|\{x\^2\}", q + sol):
        return "equacao_2grau"
    if re.search(r"方程组", q + sol):
        return "sistema"
    if re.search(r"不等式|≥|≤|\\ge|\\le|<|>", q):
        return "inequacao"
    if re.search(r"解方程|一元一次", q + sol) or ("=" in q and "x" in q.lower()):
        return "equacao_1grau"
    return "outros"


def traduzir_registro(reg: dict) -> dict:
    prompt = (
        "Traduza do chinês para o português do Brasil os três campos de um problema de matemática escolar.\n"
        "REGRAS ESTRITAS:\n"
        "- Mantenha TODAS as expressões matemáticas, números e fórmulas LaTeX ($...$, \\frac{}{}, etc.) 100% intactas.\n"
        "- Traduza apenas o texto em chinês de forma fiel, clara e natural.\n"
        "- Não resolva, não resuma e não altere os números.\n\n"
        f"question: {reg['question']}\n\n"
        f"solution: {reg['solution']}\n\n"
        f"error_explanation: {reg['error_explanation']}\n\n"
        'Responda APENAS JSON válido: {"question_pt": "...", "solution_pt": "...", "error_explanation_pt": "..."}'
    )
    corpo = {
        "model": MODELO_TRAD,
        "stream": False,
        "messages": [{"role": "user", "content": prompt}],
        "format": ESQUEMA_TRAD,
        "options": {"temperature": 0, "num_predict": 700},
    }
    req = urllib.request.Request(
        f"{OLLAMA}/api/chat",
        data=json.dumps(corpo).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        r = json.loads(resp.read().decode("utf-8"))
    parsed = json.loads(r["message"]["content"])
    return {
        "question_pt": parsed.get("question_pt", reg["question"]),
        "solution_pt": parsed.get("solution_pt", reg["solution"]),
        "error_explanation_pt": parsed.get("error_explanation_pt", reg["error_explanation"]),
    }


def main():
    registros = [json.loads(l) for l in (DADOS / "middle.jsonl").open("r", encoding="utf-8") if l.strip()]

    # 1. Congela subconjunto equações do 1º grau
    escopo = []
    for r in registros:
        sub = classificar_subconjunto(r)
        r["subconjunto"] = sub
        if sub == "equacao_1grau":
            escopo.append(r)

    escopo_path = DADOS / "escopo_1grau.jsonl"
    with escopo_path.open("w", encoding="utf-8") as f:
        for r in escopo:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"Salvo escopo 1º grau: {len(escopo)} amostras em {escopo_path}")

    # 2. Tradução local com checkpoint
    pt_path = DADOS / "middle_pt.jsonl"
    feitos = {}
    if pt_path.exists():
        for l in pt_path.open("r", encoding="utf-8"):
            if l.strip():
                obj = json.loads(l)
                feitos[obj["idx"]] = obj

    pendentes = [r for r in registros if r["idx"] not in feitos]
    print(f"Tradução local ({MODELO_TRAD}): {len(feitos)} prontas, {len(pendentes)} pendentes.")
    t0 = time.perf_counter()
    for n, r in enumerate(pendentes, 1):
        try:
            trad = traduzir_registro(r)
            ok = True
        except Exception as e:
            trad = {
                "question_pt": r["question"],
                "solution_pt": r["solution"],
                "error_explanation_pt": r["error_explanation"],
                "erro_trad": str(e),
            }
            ok = False
        reg_pt = {**r, **trad, "trad_ok": ok, "trad_modelo": MODELO_TRAD}
        with pt_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(reg_pt, ensure_ascii=False) + "\n")
        if n % 25 == 0 or n == len(pendentes):
            print(f"  Traduzidos: {n}/{len(pendentes)} ({time.perf_counter() - t0:.1f}s)")

    print("Preparação V2 concluída.")


if __name__ == "__main__":
    main()
