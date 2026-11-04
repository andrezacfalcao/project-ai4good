"""Piloto do E2, terceira versão: o mesmo teste de protocolo, com os defeitos da segunda corrigidos.

Correções (emenda 5 de exp.md, commitadas antes desta execução):
1. a leitura de "x = 2." dava 2.0, e {2.0} != {2}: resoluções certas viravam erradas e recebiam pista.
   Aqui, o ponto final sai e os decimais são lidos como frações, nas duas condições e no diagnóstico do Atlas;
2. o sorteio usa de fato a lista embaralhada, e cada sessão sai de um participante sorteado;
3. o registro guarda o texto de cada pista, para conferir os vazamentos à mão;
4. conta as pistas dadas a resoluções que já chegavam ao x certo (pista sobre trabalho certo);
5. a persona faz o pré-teste e a prova, para testar a correção automática das duas listas;
6. calcula as métricas do § 3.2 que dá para calcular com uma persona; "indicação errada aceita" não dá,
   porque a persona não contesta.
A persona continua sendo só um teste do protocolo, nunca da ideia.

Rodar a partir da raiz, com o Ollama ativo:  tec/.venv/bin/python -I exp/piloto/piloto_e2_v3.py
Saída: exp/piloto/resultados/e2_v3.md e e2_v3_sessoes.jsonl
"""
import collections
import json
import random
import re
import sys
import time
from pathlib import Path

from sympy import Eq, solveset
from sympy.parsing.sympy_parser import parse_expr, rationalize

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import piloto_e1 as e1  # noqa: E402
from piloto_e2 import ATLAS, ESQUEMA_PERSONA, PERSONA, PROMPT_PERSONA, equacao  # noqa: E402
from piloto_e2_v2 import listas_pareadas, perfil  # noqa: E402

RES = AQUI / "resultados"
SEMENTE = 2026
PARTICIPANTES, POR_CONDICAO, EXERCICIOS = 30, 6, 5
MAX_PISTAS, MAX_ILEGIVEIS_SEGUIDAS, MAX_TENTATIVAS = 3, 2, 8


# ---------- leitura corrigida ----------
def ler(linha):
    if not isinstance(linha, str):
        return ""
    s = linha.split(":")[-1].replace("÷", "/").replace("×", "*")
    s = re.sub(r"\(.*?\)\s*$", "", s)
    return re.sub(r"[.,;]+\s*$", "", s).strip()


def raizes(linha):
    if "=" not in linha:
        return None
    try:
        a, b = linha.lower().replace("$", "").split("=", 1)
        tr = e1.TR + (rationalize,)
        return solveset(Eq(parse_expr(a, transformations=tr), parse_expr(b, transformations=tr)), e1.X)
    except Exception:
        return None


def diagnostico(ls):
    sols = [raizes(l) for l in ls]
    for i, s in enumerate(sols):
        if s is None:
            return "invalida", i + 1
        if i > 0 and s != sols[i - 1]:
            return "quebra", i + 1
    return "sem_quebra", None


def lidas(linhas):
    return [ler(l) for l in (linhas or []) if ler(l)]


def chega_ao_x(linhas, x):
    ls = lidas(linhas)
    return bool(ls) and raizes(ls[-1]) == {x}


def resolveu(linhas, x):
    ls = lidas(linhas)
    return chega_ao_x(linhas, x) and diagnostico(ls)[0] == "sem_quebra"


def pista_literal(texto):
    return bool(texto) and re.search(r"\bx\s*=\s*-?\d", texto.lower().replace("$", "")) is not None


# ---------- persona ----------
def persona(tarefa, historico):
    prompt = PROMPT_PERSONA + f"Equação: {tarefa}."
    if historico:
        prompt += " Você já tentou e recebeu este retorno: " + " | ".join(historico) + " Refaça a resolução."
    saida, _ = e1.qwen(PERSONA, prompt, ESQUEMA_PERSONA)
    linhas = saida.get("linhas") if isinstance(saida.get("linhas"), list) else None
    return linhas, "invalido" in saida or linhas is None


def prova(lista):
    """A persona resolve cada equação uma vez, sem retorno; conta as que chegam ao x certo."""
    return sum(chega_ao_x(persona(eq, [])[0], x) for eq, x in lista)


def sessao(participante, cond, tarefa, x):
    reg = {"participante": participante, "condicao": cond, "tarefa": tarefa, "x": x, "tentativas": [],
           "pistas": [], "professor": False, "json_invalido": 0, "linha_ilegivel": 0, "fim": None}
    historico, t0, ilegiveis, ultimo = [], time.perf_counter(), 0, None
    while len(reg["tentativas"]) < MAX_TENTATIVAS:
        linhas, invalido = persona(tarefa, historico)
        reg["json_invalido"] += invalido
        reg["tentativas"].append(linhas)
        if not linhas:
            continue
        if resolveu(linhas, x):
            reg["fim"] = {None: "resolveu de primeira", "pista": "resolveu depois da pista",
                          "gabarito": "resolveu depois do gabarito", "ilegivel": "resolveu depois de reescrever"}[ultimo]
            break
        ls = lidas(linhas)
        tipo, k = diagnostico(ls) if ls else ("invalida", 1)
        if tipo == "invalida":
            reg["linha_ilegivel"] += 1
            ilegiveis += 1
            if ilegiveis >= MAX_ILEGIVEIS_SEGUIDAS:
                reg["professor"], reg["fim"] = True, "chamou o professor (ilegível)"
                break
            historico.append(f"A linha {k} não pôde ser lida; escreva só a conta, uma por linha.")
            ultimo = "ilegivel"
            continue
        ilegiveis = 0
        if cond == "A":
            if ultimo == "gabarito":
                reg["fim"] = "não resolveu depois do gabarito"
                break
            historico.append(f"O gabarito diz que x = {x}.")
            ultimo = "gabarito"
            continue
        if len(reg["pistas"]) == MAX_PISTAS:
            reg["professor"], reg["fim"] = True, "chamou o professor (3 pistas)"
            break
        texto_diag = f"quebra na linha {k}: '{ls[k - 2]}' -> '{ls[k - 1]}'" if tipo == "quebra" else "equivalencia mantida"
        saida, _ = e1.qwen(ATLAS, e1.PROMPT_ATLAS + f"Passos lidos: {ls} | SymPy: {texto_diag}", e1.ESQUEMA)
        pista = saida.get("dica_aluno", "")
        reg["pistas"].append({"linhas_lidas": ls, "quebra": k, "categoria": saida.get("categoria_erro"), "pista": pista,
                              "com_resposta_literal": pista_literal(pista),
                              "com_resposta_detector": e1.pista_com_resposta(pista, {"linhas": ls, "x_correto": x}),
                              "sobre_resolucao_que_chega_ao_x": chega_ao_x(linhas, x)})
        historico.append(f"O erro está na linha {k}. Dica: {pista}")
        ultimo = "pista"
    reg["fim"] = reg["fim"] or "sem fim"
    reg["tempo"] = time.perf_counter() - t0
    return reg


def main():
    r = random.Random(SEMENTE)
    RES.mkdir(exist_ok=True)
    ids = [f"P{i:02d}" for i in range(1, PARTICIPANTES + 1)]
    r.shuffle(ids)
    alocacao = {p: ("A" if i < PARTICIPANTES // 2 else "B") for i, p in enumerate(ids)}
    contagem = collections.Counter(alocacao.values())
    pre, final = listas_pareadas(random.Random(SEMENTE + 1))
    regs, provas = [], []
    for cond in ("A", "B"):
        sorteados = [p for p in ids if alocacao[p] == cond][:POR_CONDICAO]
        for j, p in enumerate(sorteados):
            rr = random.Random(SEMENTE + 100 * (cond == "B") + j)
            antes = prova(pre)
            for _ in range(EXERCICIOS):
                tarefa, x = equacao(rr)
                regs.append(sessao(p, cond, tarefa, x))
                print(p, cond, regs[-1]["fim"], len(regs[-1]["pistas"]), flush=True)
            depois = prova(final)
            provas.append({"participante": p, "condicao": cond, "pre": antes, "prova": depois})
    tab = []
    for cond, nome in (("A", "A · gabarito do livro"), ("B", "B · Atlas")):
        s = [g for g in regs if g["condicao"] == cond]
        pv = [g for g in provas if g["condicao"] == cond]
        fins = collections.Counter(g["fim"] for g in s)
        ps = [p for g in s for p in g["pistas"]]
        corrigiu = fins.get("resolveu depois da pista", 0) + fins.get("resolveu depois do gabarito", 0)
        tab.append(
            f"| {nome} | {len(pv)} | {sum(g['pre'] for g in pv) / len(pv):.1f} | {sum(g['prova'] for g in pv) / len(pv):.1f} | "
            f"{len(s)} | {fins.get('resolveu de primeira', 0)} | {corrigiu} | {fins.get('resolveu depois de reescrever', 0)} | "
            f"{sum(g['professor'] for g in s)} | {len(ps) / len(s):.2f} | {sum(p['com_resposta_literal'] for p in ps)} de {len(ps)} | "
            f"{sum(p['sobre_resolucao_que_chega_ao_x'] for p in ps)} | {sum(g['linha_ilegivel'] for g in s)} | "
            f"{sum(g['json_invalido'] for g in s)} | {fins.get('sem fim', 0) + fins.get('não resolveu depois do gabarito', 0)} | "
            f"{sum(g['tempo'] for g in s) / len(s):.1f} |")
    texto = (
        "# Piloto do E2 · terceira versão do protocolo, com persona de IA\n\n"
        "Gerada por `piloto_e2_v3.py`. A persona é um modelo de linguagem: os números abaixo testam o protocolo, "
        "não dizem nada sobre alunos. Os acertos no pré-teste e na prova testam a correção automática das listas, "
        "não aprendizagem.\n\n"
        f"- sorteio de {PARTICIPANTES} participantes, a partir da lista embaralhada: {contagem['A']} em A e "
        f"{contagem['B']} em B; sessões rodadas com os {POR_CONDICAO} primeiros sorteados de cada condição\n"
        f"- pré-teste e prova pareados: mesmo perfil de coeficientes e sinais: {perfil(pre) == perfil(final)}\n\n"
        "| condição | participantes | acertos no pré-teste (de 10) | acertos na prova (de 10) | exercícios de prática | "
        "resolvidos de primeira | corrigidos depois do retorno | resolvidos depois de reescrever | chamadas ao professor | "
        "pistas por exercício | pistas com algum valor de x | pistas sobre resolução que já chegava ao x | "
        "linhas que o SymPy não lê | JSON inválido da persona | terminou sem resolver | tempo por exercício (s) |\n"
        "|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|\n" + "\n".join(tab) + "\n\n"
        "A métrica \"indicação errada aceita\" não é calculada: a persona não contesta indicações.\n")
    (RES / "e2_v3.md").write_text(texto, encoding="utf-8")
    with open(RES / "e2_v3_sessoes.jsonl", "w", encoding="utf-8") as f:
        for g in regs:
            f.write(json.dumps(g, ensure_ascii=False) + "\n")
        for g in provas:
            f.write(json.dumps({"tipo": "provas", **g}, ensure_ascii=False) + "\n")
    print("\n" + texto)


if __name__ == "__main__":
    main()
