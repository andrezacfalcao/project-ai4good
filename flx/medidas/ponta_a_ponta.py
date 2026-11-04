"""Tempo por caderno do caminho inteiro (recorte, TrOCR, SymPy e Qwen), sem contar a carga do OCR.

Repete a logica de tec/ler_caderno.py (commit abf1638) sem altera-lo, so acrescentando cronometros.
Rodar a partir da raiz, com o Ollama ativo:
  HF_HUB_OFFLINE=1 tec/.venv/bin/python -I flx/medidas/ponta_a_ponta.py tec/cadernos/caderno-*.png
"""
import json, sys, time, urllib.request
from PIL import Image
from sympy import Eq, Symbol, solveset
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

TR = standard_transformations + (implicit_multiplication_application,)
PROMPT = (
    'Responda APENAS JSON: {"categoria_erro": str, "dica_aluno": str}. '
    'O aluno errou na passagem indicada pelo SymPy (ex: passou termo para o outro lado sem inverter o sinal). '
    'Nomeie o tipo de erro para o Atlas da turma e explique ao aluno o que revisar nessa linha, SEM dar o valor de x.\n'
)
t0 = time.perf_counter()
processor = TrOCRProcessor.from_pretrained("microsoft/trocr-small-printed")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-small-printed")
print(f"carga do TrOCR: {time.perf_counter()-t0:.2f} s")

def raizes(l):
    if "=" not in l:
        return None
    a, b = l.lower().split("=", 1)
    return solveset(Eq(parse_expr(a, transformations=TR), parse_expr(b, transformations=TR)), Symbol("x"))

for caminho in sys.argv[1:]:
    t = {}
    t["inicio"] = time.perf_counter()
    image = Image.open(caminho).convert("RGB")
    w, h = image.size
    faixas = [image.crop((0, i * (h // 3), w, (i + 1) * (h // 3))) for i in range(3)]
    linhas = processor.batch_decode(model.generate(processor(images=faixas, return_tensors="pt").pixel_values), skip_special_tokens=True)
    t["ocr"] = time.perf_counter()
    sols = [raizes(l) for l in linhas]
    diag = "equivalencia mantida"
    for i in range(len(linhas)):
        if sols[i] is None:
            diag = f"falha de OCR na linha {i+1} ('{linhas[i]}' sem '=')"; break
        if i > 0 and sols[i] != sols[i - 1]:
            diag = f"quebra na linha {i+1}: '{linhas[i-1]}' -> '{linhas[i]}'"; break
    t["sympy"] = time.perf_counter()
    req = urllib.request.Request("http://localhost:11434/api/generate", data=json.dumps({
        "model": "qwen2.5:1.5b", "format": "json", "stream": False, "options": {"temperature": 0},
        "prompt": PROMPT + f"Passos lidos: {linhas} | SymPy: {diag}"}).encode(), headers={"Content-Type": "application/json"})
    json.loads(urllib.request.urlopen(req, timeout=120).read())
    t["qwen"] = time.perf_counter()
    print(f"{caminho}: OCR {t['ocr']-t['inicio']:.2f} s | SymPy {t['sympy']-t['ocr']:.3f} s | Qwen {t['qwen']-t['sympy']:.2f} s | total {t['qwen']-t['inicio']:.2f} s")
