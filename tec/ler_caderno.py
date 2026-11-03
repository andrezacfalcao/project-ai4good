import json, sys, urllib.request
from PIL import Image
from sympy import Eq, Symbol, solveset
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

# A inferencia TrOCR segue exemplo_oficial.py. A adaptacao e de entrada/saida.
if len(sys.argv) == 1:
    sys.exit("Uso: python ler_caderno.py cadernos/caderno-1.png [outras imagens]")

TR = standard_transformations + (implicit_multiplication_application,)
PROMPT = (
    'Responda APENAS JSON: {"categoria_erro": str, "dica_aluno": str}. '
    'O aluno errou na passagem indicada pelo SymPy (ex: passou termo para o outro lado sem inverter o sinal). '
    'Nomeie o tipo de erro para o Atlas da turma e explique ao aluno o que revisar nessa linha, SEM dar o valor de x.\n'
)

processor = TrOCRProcessor.from_pretrained("microsoft/trocr-small-printed")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-small-printed")


def raizes(linha):
    if "=" not in linha:
        return None
    esq, dir_ = linha.lower().split("=", 1)
    return solveset(Eq(parse_expr(esq, transformations=TR), parse_expr(dir_, transformations=TR)), Symbol("x"))


for caminho in sys.argv[1:]:
    image = Image.open(caminho).convert("RGB")
    w, h = image.size
    faixas = [image.crop((0, i * (h // 3), w, (i + 1) * (h // 3))) for i in range(3)]
    pixel_values = processor(images=faixas, return_tensors="pt").pixel_values
    generated_ids = model.generate(pixel_values)
    linhas = processor.batch_decode(generated_ids, skip_special_tokens=True)

    sols = [raizes(l) for l in linhas]
    diagnostico = "equivalencia mantida"
    for i in range(len(linhas)):
        if sols[i] is None:
            diagnostico = f"falha de OCR na linha {i+1} ('{linhas[i]}' sem '=')"
            break
        if i > 0 and sols[i] != sols[i - 1]:
            diagnostico = f"quebra na linha {i+1}: '{linhas[i-1]}' -> '{linhas[i]}'"
            break

    req = urllib.request.Request(
        "http://localhost:11434/api/generate",
        data=json.dumps({
            "model": "qwen2.5:1.5b", "format": "json", "stream": False,
            "options": {"temperature": 0},
            "prompt": PROMPT + f"Passos lidos: {linhas} | SymPy: {diagnostico}",
        }).encode(),
        headers={"Content-Type": "application/json"},
    )
    dica = json.loads(urllib.request.urlopen(req, timeout=120).read())["response"]
    print(f"[{caminho}]\n  trocr : {linhas}\n  sympy : {diagnostico}\n  qwen  : {dica}")
