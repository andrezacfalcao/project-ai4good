"""O caminho do Atlas do Erro, usado pelo site: recorte, TrOCR, SymPy e Qwen.

Repete a lógica de tec/ler_caderno.py (commit abf1638) sem alterá-lo, e acrescenta duas opções
do fluxograma (flx): recortar as linhas pelos vãos, em vez de três faixas fixas, e pedir ao Qwen uma
categoria de uma lista fixa, em vez de uma categoria livre.
"""
import json
import re
import time
import urllib.error
import urllib.request

from PIL import Image
from sympy import Eq, Symbol, solveset
from sympy.parsing.sympy_parser import (implicit_multiplication_application, parse_expr, rationalize,
                                        standard_transformations)

OLLAMA = "http://localhost:11434"
MODELO_OCR = "microsoft/trocr-small-printed"
TR = standard_transformations + (implicit_multiplication_application,)
X = Symbol("x")
CATEGORIAS = ["troca_sinal", "conta", "distributiva", "divisao", "outro"]

# Prompt de tec/ler_caderno.py, sem mudança: categoria livre.
PROMPT_TEC = (
    'Responda APENAS JSON: {"categoria_erro": str, "dica_aluno": str}. '
    "O aluno errou na passagem indicada pelo SymPy (ex: passou termo para o outro lado sem inverter o sinal). "
    "Nomeie o tipo de erro para o Atlas da turma e explique ao aluno o que revisar nessa linha, SEM dar o valor de x.\n"
)
# O mesmo prompt com a lista fixa de categorias do flx (igual ao do piloto do exp).
PROMPT_LISTA = (
    'Responda APENAS JSON: {"categoria_erro": str, "dica_aluno": str}. '
    "O aluno errou na passagem indicada pelo SymPy. A categoria_erro é uma destas: "
    "troca_sinal (passou um termo para o outro lado sem inverter o sinal), "
    "conta (errou uma soma, subtração ou multiplicação), "
    "distributiva (não multiplicou todos os termos dentro dos parênteses), "
    "divisao (errou ao isolar o x dividindo pelo coeficiente), outro (nenhuma dessas). "
    "Nomeie o tipo de erro para o Atlas da turma e explique ao aluno o que revisar nessa linha, SEM dar o valor de x.\n"
)
ESQUEMA = {"type": "object", "properties": {"categoria_erro": {"type": "string", "enum": CATEGORIAS},
                                            "dica_aluno": {"type": "string"}},
           "required": ["categoria_erro", "dica_aluno"]}


def carregar_ocr():
    from transformers import TrOCRProcessor, VisionEncoderDecoderModel
    return TrOCRProcessor.from_pretrained(MODELO_OCR), VisionEncoderDecoderModel.from_pretrained(MODELO_OCR)


# ---------- passo 3: separar a foto em linhas ----------
def recortar_fixo(img, n=3):
    w, h = img.size
    return [img.crop((0, i * (h // n), w, (i + 1) * (h // n))) for i in range(n)]


def recortar_por_vaos(img):
    cinza = img.convert("L")
    w, h = cinza.size
    px = cinza.load()
    tinta = [sum(1 for x in range(w) if px[x, y] < 110) for y in range(h)]
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


# ---------- passo 4: TrOCR ----------
def transcrever(ocr, faixas):
    if not faixas:
        return []
    processor, model = ocr
    ids = model.generate(processor(images=faixas, return_tensors="pt").pixel_values)
    return processor.batch_decode(ids, skip_special_tokens=True)


# ---------- passo 6: SymPy ----------
def raizes(linha):
    if "=" not in linha:
        return None
    try:
        # um ponto final ("x = 2.") faria o SymPy ler 2.0, e {2.0} != {2}; rational=True lê 2.5 como 5/2
        a, b = re.sub(r"[.,;]+\s*$", "", linha.lower().replace("$", "")).split("=", 1)
        ea, eb = (parse_expr(s, transformations=TR + (rationalize,)) for s in (a, b))
        return solveset(Eq(ea, eb), X)
    except Exception:
        return None


def diagnosticar(linhas):
    """Devolve (tipo, linha com base 1, texto): tipo é 'quebra', 'sem_quebra' ou 'ilegivel'."""
    sols = [raizes(l) for l in linhas]
    for i, s in enumerate(sols):
        if s is None:
            return "ilegivel", i + 1, f"a linha {i + 1} ('{linhas[i]}') não pôde ser lida como equação"
        if i > 0 and s != sols[i - 1]:
            return "quebra", i + 1, f"quebra na linha {i + 1}: '{linhas[i - 1]}' -> '{linhas[i]}'"
    return "sem_quebra", None, "equivalencia mantida"


# ---------- passo 7: Qwen no Ollama ----------
def modelos_instalados():
    try:
        r = json.loads(urllib.request.urlopen(f"{OLLAMA}/api/tags", timeout=3).read())
        return sorted(m["name"] for m in r.get("models", []) if m["name"].startswith("qwen"))
    except (urllib.error.URLError, OSError, ValueError):
        return []


def pedir_pista(modelo, linhas, diag_texto, lista_fixa=True):
    prompt = (PROMPT_LISTA if lista_fixa else PROMPT_TEC) + f"Passos lidos: {linhas} | SymPy: {diag_texto}"
    corpo = {"model": modelo, "stream": False, "options": {"temperature": 0}, "prompt": prompt,
             "format": ESQUEMA if lista_fixa else "json"}
    req = urllib.request.Request(f"{OLLAMA}/api/generate", data=json.dumps(corpo).encode(),
                                 headers={"Content-Type": "application/json"})
    r = json.loads(urllib.request.urlopen(req, timeout=180).read())
    try:
        return json.loads(r["response"])
    except json.JSONDecodeError:
        return {"categoria_erro": None, "dica_aluno": r["response"]}


def pista_da_valor(pista, linhas):
    """Aviso simples: a pista escreve um valor de x que não está nas linhas lidas."""
    if not pista:
        return False
    vistos = {m.group(1) for l in linhas for m in re.finditer(r"x\s*=\s*(-?\d+)", l.lower())}
    return any(m.group(1) not in vistos for m in re.finditer(r"\bx\s*=\s*(-?\d+)", pista.lower().replace("$", "")))


# ---------- o caminho inteiro ----------
def rodar(ocr, img, modelo, recorte="vaos", lista_fixa=True, linhas=None):
    """Roda os passos 3 a 7. Se `linhas` vier preenchida (transcrição conferida), pula o recorte e o OCR."""
    t0 = time.perf_counter()
    faixas = []
    if linhas is None:
        faixas = recortar_por_vaos(img) if recorte == "vaos" else recortar_fixo(img)
        linhas = transcrever(ocr, faixas)
    t_ocr = time.perf_counter() - t0
    tipo, k, texto = diagnosticar(linhas)
    saida = {}
    if tipo == "quebra" and modelo:
        saida = pedir_pista(modelo, linhas, texto, lista_fixa)
    total = time.perf_counter() - t0
    pista = saida.get("dica_aluno")
    return {"faixas": faixas, "linhas": linhas, "diagnostico": tipo, "linha_quebra": k, "diag_texto": texto,
            "categoria": saida.get("categoria_erro"), "pista": pista,
            "pista_da_valor": pista_da_valor(pista, linhas), "t_ocr": t_ocr, "t_total": total}


def abrir(caminho_ou_arquivo):
    return Image.open(caminho_ou_arquivo).convert("RGB")
