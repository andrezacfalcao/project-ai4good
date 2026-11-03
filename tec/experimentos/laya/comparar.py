"""Experimento exploratorio: classificacao das mesmas transicoes em LAYA e Qwen.

O campo esperado nunca e enviado aos modelos. Nao executa OCR nem gera pistas.
"""
import argparse
import importlib.metadata
import json
import platform
import statistics
import time
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from exemplo_oficial import MODEL, REVISION, carregar, exemplo

HERE = Path(__file__).resolve().parent
CRITERIOS = {
    "troca_sinal": "Um termo foi passado para o outro lado da igualdade mantendo indevidamente o sinal original.",
    "distributiva": "Ao remover parenteses, o fator externo nao foi multiplicado por todos os termos.",
    "aritmetica": "Uma soma, subtracao, multiplicacao ou divisao numerica foi calculada incorretamente.",
    "sem_erro": "As duas igualdades sao passos algebricos corretos e equivalentes.",
    "leitura_invalida": "Os simbolos estao ilegíveis ou falta uma igualdade valida; nao e possivel julgar a conta.",
}
QUESTIONS = {"categoria": {
    "type": "choice",
    "instructions": "Classifique a passagem entre as duas linhas da resolucao matematica do estudante. Escolha uma unica categoria.",
    "criteria": CRITERIOS,
}}


def texto(caso):
    return f"Linha anterior: {caso['anterior']}\nLinha seguinte: {caso['seguinte']}"


def contexto_sympy(caso):
    from sympy import Eq, Symbol, solveset
    from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
    tr = standard_transformations + (implicit_multiplication_application,)
    if any("=" not in caso[k] for k in ("anterior", "seguinte")):
        return "Verificador: leitura invalida; falta uma igualdade legivel."
    solutions = []
    for k in ("anterior", "seguinte"):
        left, right = caso[k].lower().split("=", 1)
        solutions.append(solveset(Eq(parse_expr(left, transformations=tr), parse_expr(right, transformations=tr)), Symbol("x")))
    if solutions[0] == solutions[1]:
        return "Verificador SymPy: equivalencia mantida nesta passagem."
    return "Verificador SymPy: quebra de equivalencia nesta passagem."


def qwen(state):
    prompt = QUESTIONS["categoria"]["instructions"] + "\nCategorias: " + json.dumps(CRITERIOS, ensure_ascii=False)
    prompt += "\nRetorne apenas o JSON com categoria.\n" + state
    payload = {
        "model": "qwen2.5:1.5b", "stream": False,
        "format": {"type": "object", "properties": {"categoria": {"type": "string", "enum": list(CRITERIOS)}}, "required": ["categoria"]},
        "options": {"temperature": 0, "num_predict": 64},
        "prompt": prompt,
    }
    req = urllib.request.Request("http://localhost:11434/api/generate", data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as response:
        raw = json.load(response)
    return json.loads(raw["response"])["categoria"], raw


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sem-qwen", action="store_true")
    parser.add_argument("--contexto-sympy", action="store_true")
    args = parser.parse_args()
    resultados = HERE / "resultados"
    if args.contexto_sympy:
        resultados = resultados / "com_sympy"
    resultados.mkdir(exist_ok=True, parents=True)
    casos = json.loads((HERE / "casos.json").read_text())
    def entrada(caso):
        return texto(caso) + ("\n" + contexto_sympy(caso) if args.contexto_sympy else "")
    inicio = time.perf_counter()
    agent = carregar()
    carga_s = time.perf_counter() - inicio
    print(f"LAYA carregado em {carga_s:.2f} s (inclui download se necessario)", flush=True)
    oficial = exemplo(agent)
    (resultados / "exemplo_oficial.json").write_text(json.dumps(oficial, ensure_ascii=False, indent=2) + "\n")
    # Aquecimento separado, descartado das estatisticas de classificacao.
    agent.predict(entrada(casos[0]), QUESTIONS)
    if not args.sem_qwen:
        qwen(entrada(casos[0]))
    rows = []
    for caso in casos:
        t0 = time.perf_counter()
        raw = agent.predict(entrada(caso), QUESTIONS)
        dt = (time.perf_counter() - t0) * 1000
        answer = raw["answers"]["categoria"]
        row = {"id": caso["id"], "entrada": entrada(caso), "esperado": caso["esperado"], "laya": {"categoria": answer["choice"], "ms": dt, "raw": raw}}
        print(f"{caso['id']}: LAYA={answer['choice']} | esperado={caso['esperado']} | {dt:.1f} ms", flush=True)
        if not args.sem_qwen:
            t0 = time.perf_counter()
            category, raw_qwen = qwen(entrada(caso))
            row["qwen"] = {"categoria": category, "ms": (time.perf_counter() - t0) * 1000, "raw": raw_qwen}
            print(f"  Qwen={category}", flush=True)
        rows.append(row)
        # Salva cada resultado obtido; uma falha posterior nao apaga os anteriores.
        (resultados / "casos_observados.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n")
    summary = {}
    for model in ("laya",) if args.sem_qwen else ("laya", "qwen"):
        summary[model] = {
            "acertos": sum(r[model]["categoria"] == r["esperado"] for r in rows),
            "total": len(rows),
            "mediana_ms": statistics.median(r[model]["ms"] for r in rows),
            "categorias_validas": all(r[model]["categoria"] in CRITERIOS for r in rows),
        }
    meta = {
        "executado_em": datetime.now(ZoneInfo("America/Recife")).isoformat(),
        "python": platform.python_version(), "plataforma": platform.platform(),
        "laya_versao": importlib.metadata.version("laya"),
        "laya_fonte_commit": "462c2644e654add83516e53c7a65909f8072d529",
        "laya_modelo": MODEL, "laya_revisao": REVISION, "laya_device": str(agent.device),
        "laya_carga_s": carga_s,
        "contexto_sympy": args.contexto_sympy,
        "pacotes": {p: importlib.metadata.version(p) for p in ("torch", "transformers", "huggingface-hub", "numpy")},
        "nota": "Dez casos sinteticos, uma chamada medida por caso, sem tuning. LAYA em CPU; Qwen via Ollama com runtime proprio. Tempos nao estabelecem superioridade entre modelos.",
        "resumo": summary,
    }
    if not args.sem_qwen:
        with urllib.request.urlopen("http://localhost:11434/api/ps", timeout=10) as response:
            meta["ollama_ps"] = json.load(response)
    (resultados / "resumo.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
