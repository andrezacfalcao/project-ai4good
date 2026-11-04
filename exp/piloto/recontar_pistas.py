"""Emenda 2 do E1: recontagem de "pista com a resposta" com o detector corrigido.

O detector de piloto_e1.py comparava o valor de x da pista só com o caderno real. Quando o OCR leu um
valor diferente (ex.: "X=4" no lugar de "x = 9") e a pista apenas repetiu o que foi lido, ele marcava
vazamento à toa. Aqui, um valor ou uma equação que já aparece nas linhas lidas pelo sistema também não
conta como resposta. Nada roda de novo: a recontagem usa os registros de e1_casos.jsonl, e a tabela
original (e1.md) fica como saiu.

Rodar a partir da raiz:  tec/.venv/bin/python -I exp/piloto/recontar_pistas.py
"""
import json
import re
import sys
from collections import OrderedDict
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import piloto_e1 as e1  # noqa: E402

casos = {c["imagem"]: c for c in json.loads((AQUI / "dados" / "gabarito.json").read_text(encoding="utf-8"))}
regs = [json.loads(l) for l in open(AQUI / "resultados" / "e1_casos.jsonl", encoding="utf-8")]


def com_resposta(pista, caso, lidas):
    if not pista:
        return False
    texto = pista.lower().replace("$", "")
    vistas = list(caso["linhas"]) + list(lidas)
    escritos = {e1.norm(l) for l in vistas}
    valores = {m.group(1) for l in vistas for m in re.finditer(r"x\s*=\s*(-?\d+)", l.lower())}
    if any(m.group(1) not in valores for m in re.finditer(r"\bx\s*=\s*(-?\d+)", texto)):
        return True
    for m in re.finditer(r"[0-9x()\s+\-*/]*x[0-9x()\s+\-*/]*=[0-9x()\s+\-*/]+", texto):
        eq = m.group(0).strip()
        s = e1.raizes(eq)
        if s is not None and s == {caso["x_correto"]} and e1.norm(eq) not in escritos:
            return True
    return False


por_cond = OrderedDict()
for r in regs:
    if not r["tem_pista"]:
        continue
    pista = (r["saida_qwen"] or {}).get("dica_aluno") if r["saida_qwen"] else None
    if pista is None and r["condicao"].startswith("regra"):
        pista = e1.PISTA_REGRA.format(k=r["diagnostico"][1])
    antes, depois, n = por_cond.get(r["condicao"], (0, 0, 0))
    novo = com_resposta(pista, casos[r["imagem"]], r["linhas_lidas"])
    por_cond[r["condicao"]] = (antes + r["pista_resposta"], depois + novo, n + 1)

linhas = ["| condição | pistas com a resposta, detector original (e1.md) | detector corrigido |", "|:--|--:|--:|"]
for c, (a, d, n) in por_cond.items():
    linhas.append(f"| {c} | {a} de {n} | {d} de {n} |")
texto = "# Piloto do E1 · emenda 2: detector de pista com a resposta\n\n" + "\n".join(linhas) + "\n"
(AQUI / "resultados" / "e1_emenda_detector.md").write_text(texto, encoding="utf-8")
print(texto)
