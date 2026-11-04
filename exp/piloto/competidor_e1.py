"""Competidor do E1 (emenda 5): um modelo multimodal aberto lendo a foto direto, nas mesmas 60 resoluções.

O Qwen2.5-VL 7B é um dos modelos abertos que o molde (Song et al., AIED 2026) avalia, e roda sem internet
pelo Ollama. Ele recebe a imagem e devolve, em JSON, a primeira linha errada, a categoria e uma pista; não
passa pelo TrOCR nem pelo SymPy. As métricas são as do Atlas no piloto_e1.py, com o mesmo bootstrap.
Não há limiar novo: a hipótese do E1 já caiu; a pergunta é se o competidor passaria nos limiares pré-registrados.

Rodar a partir da raiz, com o Ollama ativo e o qwen2.5vl:7b instalado:
  tec/.venv/bin/python -I exp/piloto/competidor_e1.py
Saída: exp/piloto/resultados/e1_competidor.md e e1_competidor_casos.jsonl
"""
import base64
import json
import random
import re
import sys
import time
import urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import piloto_e1 as e1  # noqa: E402

MODELO = "qwen2.5vl:7b"
PROMPT = (
    'Responda APENAS JSON: {"linha_erro": int, "categoria_erro": str, "dica_aluno": str}. '
    "A imagem é a resolução de uma equação do 1º grau feita por um aluno, uma passagem por linha, numeradas de cima "
    "para baixo a partir de 1. linha_erro é a primeira linha que não é equivalente à anterior, ou 0 se não há erro. "
    "A categoria_erro é uma destas: troca_sinal (passou um termo para o outro lado sem inverter o sinal), "
    "conta (errou uma soma, subtração ou multiplicação), distributiva (não multiplicou todos os termos dentro dos "
    "parênteses), divisao (errou ao isolar o x dividindo pelo coeficiente), outro (nenhuma dessas). "
    "Explique ao aluno o que revisar nessa linha, SEM dar o valor de x."
)


def perguntar(caminho):
    img = base64.b64encode(Path(caminho).read_bytes()).decode()
    corpo = {"model": MODELO, "stream": False, "options": {"temperature": 0}, "prompt": PROMPT, "images": [img],
             "format": e1.ESQUEMA_SEM_SYMPY}
    req = urllib.request.Request(f"{e1.OLLAMA}/api/generate", data=json.dumps(corpo).encode(),
                                 headers={"Content-Type": "application/json"})
    t = time.perf_counter()
    r = json.loads(urllib.request.urlopen(req, timeout=600).read())
    dt = time.perf_counter() - t
    try:
        return json.loads(r["response"]), dt
    except json.JSONDecodeError:
        return {}, dt


def main():
    casos = json.loads((e1.DADOS / "gabarito.json").read_text(encoding="utf-8"))
    avals, tempos, regs = [], [], []
    e1.descarregar(MODELO)
    for c in casos:
        saida, dt = perguntar(e1.DADOS / c["imagem"])
        n = saida.get("linha_erro")
        tipo_diag, linha_diag = ("sem_quebra", None) if n in (0, None) else ("quebra", n)
        pista = saida.get("dica_aluno") if tipo_diag == "quebra" else None
        a = e1.avaliar(c, c["linhas"], tipo_diag, linha_diag, saida.get("categoria_erro") if tipo_diag == "quebra" else None, pista)
        a["gab_tipo"] = c["tipo"]
        a["linhas_exatas"], a["linhas_total"] = 0, 1  # o competidor não transcreve as linhas
        a["literal"] = bool(pista) and re.search(r"\bx\s*=\s*-?\d", pista.lower().replace("$", "")) is not None
        avals.append(a)
        tempos.append(dt)
        regs.append({"imagem": c["imagem"], "foto": c["foto"], "saida": saida, "tempo": dt, **a})
        print(c["imagem"], tipo_diag, linha_diag, saida.get("categoria_erro"), f"{dt:.1f}s", flush=True)
    linhas = []
    for foto in ("todas", "limpa", "pauta"):
        sel = [i for i, c in enumerate(casos) if foto == "todas" or c["foto"] == foto]
        linhas.append(e1.resumo(f"competidor: {MODELO} lendo a foto", foto, [avals[i] for i in sel],
                                [tempos[i] for i in sel], random.Random(e1.SEMENTE)))
    lit = sum(a["literal"] for a in avals)
    com_pista = sum(1 for a in avals if a["tem_pista"])
    cab = ("| condição | foto | resoluções | linhas lidas exatas | localização exata | acerto do tipo (só as com erro) | "
           "F1 macro do tipo | errado sem aviso | pistas com a resposta | categorias fora da lista | "
           "tempo da foto à pista (s) |\n|:--|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|")
    texto = (f"# Piloto do E1 · competidor {MODELO}\n\nGerada por `competidor_e1.py`; mesmas métricas e mesmo bootstrap "
             f"de `piloto_e1.py` ({e1.REAMOSTRAS} reamostras, semente {e1.SEMENTE}). O competidor não transcreve as "
             "linhas, então a coluna de linhas lidas não se aplica (sai 0%). O tempo inclui a carga do modelo na "
             "primeira imagem.\n\n" + cab + "\n" + "\n".join(linhas) +
             f"\n\nPistas com algum valor de x, pela definição literal do pré-registro: {lit} de {com_pista}.\n")
    (e1.RES / "e1_competidor.md").write_text(texto, encoding="utf-8")
    with open(e1.RES / "e1_competidor_casos.jsonl", "w", encoding="utf-8") as f:
        for g in regs:
            f.write(json.dumps(g, ensure_ascii=False, default=str) + "\n")
    print("\n" + texto)


if __name__ == "__main__":
    main()
