"""Números do piloto do E1 que a folha cita além da tabela, todos tirados de e1_casos.jsonl.

Não roda nenhum modelo: lê os registros da execução de piloto_e1.py e calcula
- a contagem de pistas com a resposta pela definição literal do pré-registro ("um valor de x, certo ou errado");
- as categorias que o Qwen escolheu e em quantos casos ele discorda da regra mais simples;
- a diferença pareada de acerto do tipo do erro (Qwen menos regra), com intervalo de 95% por bootstrap;
- quantas pistas mudam de texto entre as duas rodadas do Atlas completo;
- o risco seletivo: o erro sem aviso só entre os casos que o sistema aceitou como legíveis.

Rodar a partir da raiz:  tec/.venv/bin/python -I exp/piloto/estatisticas_e1.py
Saída: exp/piloto/resultados/e1_estatisticas.md
"""
import collections
import json
import random
import re
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RES = AQUI / "resultados"
SEMENTE, REAMOSTRAS = 2026, 2000
R1, R2 = "Atlas completo, modelo recém-carregado", "Atlas completo, modelo já usado"
REGRA = "regra mais simples no lugar do Qwen"

regs = [json.loads(l) for l in open(RES / "e1_casos.jsonl", encoding="utf-8")]
por = collections.defaultdict(dict)
for r in regs:
    por[r["condicao"]][r["imagem"]] = r


def pista(r):
    return (r.get("saida_qwen") or {}).get("dica_aluno") if r.get("saida_qwen") else None


def literal(texto):
    """Definição pré-registrada: a pista dá algum valor de x, certo ou errado."""
    return bool(texto) and re.search(r"\bx\s*=\s*-?\d", texto.lower().replace("$", "")) is not None


linhas = ["# Piloto do E1 · estatísticas além da tabela", "",
          "Gerado por `estatisticas_e1.py` a partir de `e1_casos.jsonl`, sem rodar nenhum modelo.", "",
          "## Pistas com a resposta, pela definição literal do pré-registro", "",
          "| condição | pistas | com algum valor de x (definição literal) | detector de piloto_e1.py | detector da emenda 2 |",
          "|:--|--:|--:|--:|--:|"]
emenda2 = {}
try:
    for l in (RES / "e1_emenda_detector.md").read_text(encoding="utf-8").splitlines()[4:]:
        c = [s.strip() for s in l.strip("|").split("|")]
        emenda2[c[0]] = c[2]
except FileNotFoundError:
    pass
for cond, casos in por.items():
    com = [r for r in casos.values() if r["tem_pista"] and pista(r)]
    if not com:
        continue
    lit = [r["imagem"] for r in com if literal(pista(r))]
    det = sum(r["pista_resposta"] for r in com)
    linhas.append(f"| {cond} | {len(com)} | {len(lit)} | {det} | {emenda2.get(cond, '—')} |")
    if cond in (R1, R2):
        linhas.append(f"|   ↳ imagens | | {', '.join(lit) or '—'} | | |")

linhas += ["", "## Categorias e acordo com a regra mais simples (só as resoluções com erro)", ""]
for cond in (R1, "teto: transcrição certa", "Qwen 0.5B", "Qwen 3B", "sem o SymPy"):
    erros = [r for r in por[cond].values() if r["tipo_ok"] is not None]
    cats = collections.Counter(r["categoria"] for r in erros)
    linhas.append(f"- {cond}: " + ", ".join(f"{k or 'sem categoria'} {v}" for k, v in cats.most_common()))
pares = [(por[R1][k], por[REGRA][k]) for k in por[R1] if por[R1][k]["tipo_ok"] is not None]
disc = sum(1 for a, b in pares if a["categoria"] != b["categoria"] and a["categoria"] is not None)
dif = [int(bool(a["tipo_ok"])) - int(bool(b["tipo_ok"])) for a, b in pares]
r = random.Random(SEMENTE)
amostras = sorted(sum(dif[r.randrange(len(dif))] for _ in dif) / len(dif) for _ in range(REAMOSTRAS))
linhas += ["", f"- resoluções com erro: {len(pares)}; Qwen e regra discordam na categoria em {disc}",
           f"- diferença pareada de acerto do tipo (Qwen menos regra): {100 * sum(dif) / len(dif):.0f} pontos, "
           f"intervalo de 95% [{100 * amostras[int(.025 * REAMOSTRAS)]:.0f}; {100 * amostras[int(.975 * REAMOSTRAS) - 1]:.0f}]"]

mud = [k for k in por[R1] if por[R1][k]["tem_pista"] and pista(por[R1][k]) != pista(por[R2][k])]
mud_cat = sum(1 for k in por[R1] if por[R1][k]["categoria"] != por[R2][k]["categoria"])
aceitos = [x for x in por[R1].values() if x["diagnostico"][0] != "invalida"]
sem = sum(x["sem_aviso"] for x in aceitos)
linhas += ["", "## Estabilidade e risco seletivo", "",
           f"- pistas com texto diferente entre as duas rodadas: {len(mud)} de "
           f"{sum(1 for x in por[R1].values() if x['tem_pista'])}; categorias diferentes: {mud_cat}",
           f"- risco seletivo (errado sem aviso entre os aceitos como legíveis): {sem} de {len(aceitos)} "
           f"({100 * sem / len(aceitos):.0f}%)"]
texto = "\n".join(linhas) + "\n"
(RES / "e1_estatisticas.md").write_text(texto, encoding="utf-8")
print(texto)
