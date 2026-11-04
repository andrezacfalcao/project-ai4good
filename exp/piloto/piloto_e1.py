"""Piloto do E1: o Atlas aponta a quebra e o tipo do erro sem entregar a resposta?

Roda as condições do pré-registro (exp.md, § 2) sobre as 60 resoluções de gerar_dados.py e imprime a
tabela das métricas com intervalo de 95% por bootstrap. Nada aqui foi ajustado olhando o resultado.

Rodar a partir da raiz, com o Ollama ativo e qwen2.5:0.5b, 1.5b e 3b instalados:
  HF_HUB_OFFLINE=1 tec/.venv/bin/python -I exp/piloto/piloto_e1.py
Saída: exp/piloto/resultados/e1.md (a tabela) e e1_casos.jsonl (cada caso, cada condição).
"""
import json
import random
import re
import time
import urllib.request
from pathlib import Path

from PIL import Image
from sympy import Eq, Symbol, solveset
from sympy.parsing.sympy_parser import implicit_multiplication_application, parse_expr, standard_transformations
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "dados"
RES = AQUI / "resultados"
OLLAMA = "http://localhost:11434"
CATEGORIAS = ["troca_sinal", "conta", "distributiva", "divisao", "outro"]
TIPOS_ERRO = ["troca_sinal", "conta", "distributiva", "divisao"]
SEMENTE, REAMOSTRAS = 2026, 2000
TR = standard_transformations + (implicit_multiplication_application,)
X = Symbol("x")

# Prompt do tec (tec/ler_caderno.py), com a lista fixa de categorias que o flx pede.
PROMPT_ATLAS = (
    'Responda APENAS JSON: {"categoria_erro": str, "dica_aluno": str}. '
    "O aluno errou na passagem indicada pelo SymPy. A categoria_erro é uma destas: "
    "troca_sinal (passou um termo para o outro lado sem inverter o sinal), "
    "conta (errou uma soma, subtração ou multiplicação), "
    "distributiva (não multiplicou todos os termos dentro dos parênteses), "
    "divisao (errou ao isolar o x dividindo pelo coeficiente), outro (nenhuma dessas). "
    "Nomeie o tipo de erro para o Atlas da turma e explique ao aluno o que revisar nessa linha, SEM dar o valor de x.\n"
)
# Prompt do tec sem nenhuma mudança: categoria livre (ablação "sem a lista fixa").
PROMPT_TEC = (
    'Responda APENAS JSON: {"categoria_erro": str, "dica_aluno": str}. '
    "O aluno errou na passagem indicada pelo SymPy (ex: passou termo para o outro lado sem inverter o sinal). "
    "Nomeie o tipo de erro para o Atlas da turma e explique ao aluno o que revisar nessa linha, SEM dar o valor de x.\n"
)
# Ablação "sem o SymPy": o Qwen acha a linha sozinho.
PROMPT_SEM_SYMPY = (
    'Responda APENAS JSON: {"linha_erro": int, "categoria_erro": str, "dica_aluno": str}. '
    "Estas são as linhas da resolução de uma equação feita por um aluno, numeradas a partir de 1. "
    "linha_erro é a primeira linha que não é equivalente à anterior, ou 0 se não há erro. "
    "A categoria_erro é uma destas: troca_sinal, conta, distributiva, divisao, outro. "
    "Explique ao aluno o que revisar nessa linha, SEM dar o valor de x.\n"
)
ESQUEMA = {"type": "object", "properties": {"categoria_erro": {"type": "string", "enum": CATEGORIAS},
                                            "dica_aluno": {"type": "string"}},
           "required": ["categoria_erro", "dica_aluno"]}
ESQUEMA_SEM_SYMPY = {"type": "object", "properties": {"linha_erro": {"type": "integer"},
                                                      "categoria_erro": {"type": "string", "enum": CATEGORIAS},
                                                      "dica_aluno": {"type": "string"}},
                     "required": ["linha_erro", "categoria_erro", "dica_aluno"]}
PISTA_REGRA = "Revise a passagem para a linha {k}: compare com a linha anterior e veja o que aconteceu com cada termo."


# ---------- passo 3: separar a foto em linhas, pelos vãos (regra) ----------
def separar_linhas(img):
    cinza = img.convert("L")
    w, h = cinza.size
    px = cinza.load()
    tinta = [sum(1 for x in range(w) if px[x, y] < 110) for y in range(h)]  # a pauta azul fica acima de 110
    faixas, ini, vazio = [], None, 0
    for y, n in enumerate(tinta):
        if n > 2:
            ini = y if ini is None else ini
            vazio = 0
        elif ini is not None:
            vazio += 1
            if vazio > 8:
                faixas.append((ini, y - vazio))
                ini, vazio = None, 0
    if ini is not None:
        faixas.append((ini, h - 1))
    faixas = [(a, b) for a, b in faixas if b - a >= 14]
    return [img.crop((0, max(0, a - 10), w, min(h, b + 10))) for a, b in faixas]


# ---------- passo 6: SymPy (regra), como em tec/ler_caderno.py ----------
def raizes(linha):
    if "=" not in linha:
        return None
    try:
        a, b = linha.lower().replace("$", "").split("=", 1)
        return solveset(Eq(parse_expr(a, transformations=TR), parse_expr(b, transformations=TR)), X)
    except Exception:
        return None


def diagnostico(linhas):
    sols = [raizes(l) for l in linhas]
    for i, s in enumerate(sols):
        if s is None:
            return "invalida", i + 1
        if i > 0 and s != sols[i - 1]:
            return "quebra", i + 1
    return "sem_quebra", None


def texto_diag(tipo, i, linhas):
    if tipo == "quebra":
        return f"quebra na linha {i}: '{linhas[i - 2]}' -> '{linhas[i - 1]}'"
    return "equivalencia mantida"


# ---------- passo 7: Qwen (IA) ----------
def qwen(modelo, prompt, esquema):
    corpo = {"model": modelo, "stream": False, "options": {"temperature": 0}, "prompt": prompt,
             "format": esquema if esquema else "json"}
    req = urllib.request.Request(f"{OLLAMA}/api/generate", data=json.dumps(corpo).encode(),
                                 headers={"Content-Type": "application/json"})
    t = time.perf_counter()
    r = json.loads(urllib.request.urlopen(req, timeout=180).read())
    dt = time.perf_counter() - t
    try:
        return json.loads(r["response"]), dt
    except json.JSONDecodeError:
        return {"invalido": r["response"]}, dt


def descarregar(modelo):
    corpo = json.dumps({"model": modelo, "keep_alive": 0}).encode()
    urllib.request.urlopen(urllib.request.Request(f"{OLLAMA}/api/generate", data=corpo), timeout=60).read()
    for _ in range(60):
        ps = json.loads(urllib.request.urlopen(f"{OLLAMA}/api/ps", timeout=10).read())
        if not any(m["name"] == modelo for m in ps.get("models", [])):
            return
        time.sleep(0.5)


# ---------- métricas ----------
def norm(s):
    return re.sub(r"\s+", "", s.lower())


def pista_com_resposta(pista, caso):
    """A pista dá um valor de x que o aluno não escreveu, ou uma equação certa e nova (o passo corrigido)."""
    if not pista:
        return False
    texto = pista.lower().replace("$", "")
    escritos = {norm(l) for l in caso["linhas"]}
    valores_do_aluno = {m.group(1) for l in caso["linhas"] for m in re.finditer(r"x\s*=\s*(-?\d+)", l.lower())}
    for m in re.finditer(r"\bx\s*=\s*(-?\d+)", texto):
        if m.group(1) not in valores_do_aluno:
            return True
    for m in re.finditer(r"[0-9x()\s+\-*/]*x[0-9x()\s+\-*/]*=[0-9x()\s+\-*/]+", texto):
        eq = m.group(0).strip()
        s = raizes(eq)
        if s is not None and s == {caso["x_correto"]} and norm(eq) not in escritos:
            return True
    return False


def avaliar(caso, linhas_lidas, tipo_diag, linha_diag, categoria, pista):
    gab_erro = caso["linha_erro"]
    if gab_erro is None:
        loc_ok = tipo_diag == "sem_quebra"
    else:
        loc_ok = tipo_diag == "quebra" and linha_diag == gab_erro
    tipo_ok = None if gab_erro is None else (categoria == caso["tipo"])
    sem_aviso = tipo_diag != "invalida" and (not loc_ok or (gab_erro is not None and not tipo_ok))
    exatas = sum(1 for i, l in enumerate(caso["linhas"]) if i < len(linhas_lidas) and norm(linhas_lidas[i]) == norm(l))
    return {"loc_ok": loc_ok, "tipo_ok": tipo_ok, "sem_aviso": sem_aviso, "linhas_exatas": exatas,
            "linhas_total": len(caso["linhas"]), "pista_resposta": pista_com_resposta(pista, caso),
            "tem_pista": bool(pista), "categoria": categoria, "fora_da_lista": categoria not in CATEGORIAS + [None]}


def taxa(vals):
    return sum(vals) / len(vals) if vals else float("nan")


def ic(vals, r):
    if not vals:
        return (float("nan"), float("nan"))
    amostras = sorted(taxa([vals[r.randrange(len(vals))] for _ in vals]) for _ in range(REAMOSTRAS))
    return amostras[int(0.025 * REAMOSTRAS)], amostras[int(0.975 * REAMOSTRAS) - 1]


def f1_macro(regs):
    f1s = []
    for c in TIPOS_ERRO:
        vp = sum(1 for g, p in regs if g == c and p == c)
        fp = sum(1 for g, p in regs if g != c and p == c)
        fn = sum(1 for g, p in regs if g == c and p != c)
        f1s.append(0.0 if vp == 0 else 2 * vp / (2 * vp + fp + fn))
    return sum(f1s) / len(f1s)


def resumo(nome, foto, avals, tempos, r):
    def pct(v):
        a, b = ic(v, r)
        return f"{100 * taxa(v):.0f}% [{100 * a:.0f}%–{100 * b:.0f}%]"
    erros = [a for a in avals if a["tipo_ok"] is not None]
    linhas = sum(a["linhas_exatas"] for a in avals) / sum(a["linhas_total"] for a in avals)
    pistas = [a["pista_resposta"] for a in avals if a["tem_pista"]]
    fora = sum(1 for a in avals if a["fora_da_lista"])
    tempo = f"{sum(tempos) / len(tempos):.2f}" if tempos else "—"
    return (f"| {nome} | {foto} | {len(avals)} | {100 * linhas:.0f}% | {pct([a['loc_ok'] for a in avals])} | "
            f"{pct([a['tipo_ok'] for a in erros])} | {f1_macro([(a['gab_tipo'], a['categoria']) for a in erros]):.2f} | "
            f"{pct([a['sem_aviso'] for a in avals])} | {sum(pistas)} de {len(pistas)} | {fora} | {tempo} |")


def main():
    casos = json.loads((DADOS / "gabarito.json").read_text(encoding="utf-8"))
    RES.mkdir(exist_ok=True)
    processor = TrOCRProcessor.from_pretrained("microsoft/trocr-small-printed")
    model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-small-printed")

    # passos 3 e 4, uma vez por imagem
    lidas, t_ocr = [], []
    for c in casos:
        t = time.perf_counter()
        faixas = separar_linhas(Image.open(DADOS / c["imagem"]).convert("RGB"))
        if faixas:
            ids = model.generate(processor(images=faixas, return_tensors="pt").pixel_values)
            lidas.append(processor.batch_decode(ids, skip_special_tokens=True))
        else:
            lidas.append([])
        t_ocr.append(time.perf_counter() - t)

    condicoes = [
        ("Atlas completo, modelo recém-carregado", "qwen2.5:1.5b", "ocr", "atlas", True),
        ("Atlas completo, modelo já usado", "qwen2.5:1.5b", "ocr", "atlas", False),
        ("teto: transcrição certa", "qwen2.5:1.5b", "gabarito", "atlas", False),
        ("sem o SymPy", "qwen2.5:1.5b", "ocr", "sem_sympy", False),
        ("regra mais simples no lugar do Qwen", None, "ocr", "regra", False),
        ("Qwen 0.5B", "qwen2.5:0.5b", "ocr", "atlas", False),
        ("Qwen 3B", "qwen2.5:3b", "ocr", "atlas", False),
        ("sem a lista fixa de categorias", "qwen2.5:1.5b", "ocr", "livre", False),
    ]
    tabela, registros = [], []
    for nome, modelo, fonte_linhas, modo, frio in condicoes:
        if frio:
            descarregar(modelo)
        avals, tempos = [], []
        for c, lido, to in zip(casos, lidas, t_ocr):
            linhas = c["linhas"] if fonte_linhas == "gabarito" else lido
            t0 = time.perf_counter()
            tipo_diag, linha_diag = diagnostico(linhas)
            t_sympy = time.perf_counter() - t0
            categoria, pista, saida, t_q = None, None, None, 0.0
            if modo == "sem_sympy":
                numeradas = " | ".join(f"{i + 1}: {l}" for i, l in enumerate(linhas))
                saida, t_q = qwen(modelo, PROMPT_SEM_SYMPY + f"Linhas: {numeradas}", ESQUEMA_SEM_SYMPY)
                n = saida.get("linha_erro")
                tipo_diag, linha_diag = ("sem_quebra", None) if n == 0 else ("quebra", n)
                categoria, pista = saida.get("categoria_erro"), saida.get("dica_aluno")
            elif tipo_diag == "quebra":
                if modo == "regra":
                    categoria, pista = "troca_sinal", PISTA_REGRA.format(k=linha_diag)
                else:
                    prompt = (PROMPT_ATLAS if modo == "atlas" else PROMPT_TEC) + \
                        f"Passos lidos: {linhas} | SymPy: {texto_diag(tipo_diag, linha_diag, linhas)}"
                    saida, t_q = qwen(modelo, prompt, ESQUEMA if modo == "atlas" else None)
                    categoria, pista = saida.get("categoria_erro"), saida.get("dica_aluno")
            a = avaliar(c, linhas, tipo_diag, linha_diag, categoria, pista)
            a["gab_tipo"] = c["tipo"]
            avals.append(a)
            if fonte_linhas == "ocr" and modo == "atlas":
                tempos.append(to + t_sympy + t_q)
            registros.append({"condicao": nome, "imagem": c["imagem"], "foto": c["foto"], "linhas_lidas": linhas,
                              "diagnostico": [tipo_diag, linha_diag], "saida_qwen": saida, **a})
        r = random.Random(SEMENTE)
        tabela.append(resumo(nome, "todas", avals, tempos, r))
        if frio:
            for foto in ("limpa", "pauta"):
                sel = [i for i, c in enumerate(casos) if c["foto"] == foto]
                tabela.append(resumo(nome, foto, [avals[i] for i in sel], [tempos[i] for i in sel], random.Random(SEMENTE)))
        print(tabela[-1], flush=True)

    cab = ("| condição | foto | resoluções | linhas lidas exatas | localização exata | acerto do tipo (só as com erro) | "
           "F1 macro do tipo | errado sem aviso | pistas com a resposta | categorias fora da lista | "
           "tempo da foto à pista (s) |\n|:--|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|")
    texto = ("# Piloto do E1 · tabela\n\nGerada por `piloto_e1.py`; intervalos de 95% por bootstrap sobre as "
             f"resoluções ({REAMOSTRAS} reamostras, semente {SEMENTE}).\n\n" + cab + "\n" + "\n".join(tabela) + "\n")
    (RES / "e1.md").write_text(texto, encoding="utf-8")
    with open(RES / "e1_casos.jsonl", "w", encoding="utf-8") as f:
        for reg in registros:
            f.write(json.dumps(reg, ensure_ascii=False, default=str) + "\n")
    print("\n" + texto)


if __name__ == "__main__":
    main()
