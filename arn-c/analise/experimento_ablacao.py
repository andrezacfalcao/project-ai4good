"""Ablação local: o mesmo estímulo (as 20 aberturas do Trabalhista preservadas) em 4 condições x 3 sementes.
Uso (da pasta arn-c): python3 analise/experimento_ablacao.py  -> analise/dados/ablacao.json
Requer Ollama com qwen2.5:1.5b e qwen2.5:0.5b."""
import json, glob, re, time, unicodedata, urllib.request
from pathlib import Path
ARN = Path(__file__).resolve().parent.parent
R = [json.load(open(f)) for f in sorted(glob.glob(str(ARN / "resultados/ultima_execucao/rodadas/*.json")))]
CFG = json.load(open(ARN / "configuracao.json"))
SYS = (ARN / "prompts/liberal_qwen.md").read_text()
SCHEMA = {"type": "object", "properties": {"risco": {"type": "string"}, "pergunta": {"type": "string"}},
          "required": ["risco", "pergunta"], "additionalProperties": False}
COND = {  # nome: (modelo, usa papel e schema JSON, temperatura)
    "A_projeto_1.5B": ("qwen2.5:1.5b", True, 0.3),
    "B_sem_papel_1.5B": ("qwen2.5:1.5b", False, 0.3),
    "C_projeto_1.5B_T0.8": ("qwen2.5:1.5b", True, 0.8),
    "D_projeto_0.5B": ("qwen2.5:0.5b", True, 0.3),
}
SEEDS = (101, 102, 103)
norm = lambda s: re.sub(r"[^a-z0-9 ]", " ", unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower())
def grams(s, n=6):
    t = norm(s).split(); return {tuple(t[i:i+n]) for i in range(max(0, len(t)-n+1))}
PT = set("de a o que e do da em um para com nao uma os no se na por mais as dos como mas ao ele das seu sua ou quando muito nos ja eu tambem so pelo pela ate isso ela entre depois sem mesmo aos seus quem nas me esse eles voce essa num nem suas meu minha numa pelos elas qual lhe deles essas esses pelas este dele tu te voces vos lhes meus minhas".split())
def call(model, system, user, temp, seed, schema):
    body = {"model": model, "stream": False, "keep_alive": "15m",
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "options": {"temperature": temp, "seed": seed, "num_predict": 150, "num_ctx": 1024, "repeat_penalty": 1.15}}
    if schema: body["format"] = SCHEMA
    t = time.time()
    req = urllib.request.Request("http://localhost:11434/api/chat", json.dumps(body).encode(), {"Content-Type": "application/json"})
    for tent in range(3):  # a GPU pode estar ocupada: tenta de novo antes de falhar
        try: out = json.load(urllib.request.urlopen(req, timeout=600))["message"]["content"]; break
        except TimeoutError:
            if tent == 2: raise
    return out, time.time() - t
rows = []
for name, (model, role, temp) in COND.items():
    for seed in SEEDS:
        for r, top in zip(R, CFG["topics"]):
            user = (f"Estamos debatendo {top['title']}. {top['challenge']}\nO trabalhista defendeu: {r['opening']}\n"
                    "Qual custo para contratar, incentivo econômico adverso ou problema de financiamento de mercado você identifica?")
            out, lat = call(model, SYS if role else "Você é um assistente útil. Responda em português.", user, temp, seed, role)
            fmt, text = True, out
            if role:
                try:
                    j = json.loads(out); text = f"{j['risco']} {j['pergunta']}"
                except Exception: fmt = False
            toks = norm(text).split(); g, gi = grams(text), grams(user)
            rows.append(dict(cond=name, seed=seed, round=r["round"], text=out, latency=lat, fmt=fmt, words=len(text.split()),
                             anchor=any(a in norm(text) for a in top["anchors"]),
                             copy=len(g & gi) / len(g) if g else 0.0, pt=sum(w in PT for w in toks) / max(1, len(toks))))
    print(name, "ok", flush=True)
    json.dump(rows, open(Path(__file__).parent / "dados/ablacao.json", "w"), ensure_ascii=False, indent=1)
