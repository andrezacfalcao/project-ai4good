"""Tokens e tempo de uma chamada do Qwen com o prompt de tec/ler_caderno.py.

Rodar a partir da raiz, com o Ollama ativo: python3 -I flx/medidas/tokens_qwen.py
"""
import json, urllib.request, statistics
# mesmo PROMPT de tec/ler_caderno.py (commit abf1638)
PROMPT = (
    'Responda APENAS JSON: {"categoria_erro": str, "dica_aluno": str}. '
    'O aluno errou na passagem indicada pelo SymPy (ex: passou termo para o outro lado sem inverter o sinal). '
    'Nomeie o tipo de erro para o Atlas da turma e explique ao aluno o que revisar nessa linha, SEM dar o valor de x.\n'
)
casos = [(['2X + 4 =10', '2X = 10 + 4', 'X=7'], "quebra na linha 2: '2X + 4 =10' -> '2X = 10 + 4'"),
         (['3X-6=9', '3X= 9 - 6', 'X=1'], "quebra na linha 2: '3X-6=9' -> '3X= 9 - 6'"),
         (['4X+8-20', '4X=20+8', '* * *'], "falha de OCR na linha 1 ('4X+8-20' sem '=')")]
ent, sai, ms = [], [], []
for linhas, diag in casos:
    req = urllib.request.Request("http://localhost:11434/api/generate", data=json.dumps({
        "model": "qwen2.5:1.5b", "format": "json", "stream": False, "options": {"temperature": 0},
        "prompt": PROMPT + f"Passos lidos: {linhas} | SymPy: {diag}"}).encode(), headers={"Content-Type": "application/json"})
    r = json.loads(urllib.request.urlopen(req, timeout=120).read())
    ent.append(r["prompt_eval_count"]); sai.append(r["eval_count"]); ms.append(r["total_duration"]/1e6)
print("tokens de entrada:", ent, "saida:", sai, "ms por chamada:", [round(x) for x in ms])
