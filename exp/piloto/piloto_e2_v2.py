"""Piloto do E2, segunda versão: o mesmo teste de protocolo, com os defeitos da primeira corrigidos.

Correções (emenda 4 de exp.md, definidas antes desta execução):
1. a leitura das linhas é a mesma nas duas condições: aproveita a conta depois de ":" e aceita "÷" e "×";
2. as linhas ilegíveis são contadas nas duas condições;
3. duas leituras ilegíveis seguidas chamam o professor, e as leituras ilegíveis não gastam as pistas;
4. "resolveu depois da pista" fica separado de "resolveu depois de reescrever";
5. o pré-teste e a prova são listas pareadas: mesmo coeficiente e mesmo sinal, números diferentes.
A persona continua sendo só um teste do protocolo, nunca da ideia.

Rodar a partir da raiz, com o Ollama ativo:  tec/.venv/bin/python -I exp/piloto/piloto_e2_v2.py
Saída: exp/piloto/resultados/e2_v2.md e e2_v2_sessoes.jsonl
"""
import collections
import json
import random
import re
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import piloto_e1 as e1  # noqa: E402
from piloto_e2 import ATLAS, ESQUEMA_PERSONA, PARTICIPANTES, PERSONA, PROMPT_PERSONA, equacao  # noqa: E402

RES = AQUI / "resultados"
SEMENTE = 2026
PERSONAS_POR_CONDICAO, EXERCICIOS = 6, 5
MAX_PISTAS, MAX_ILEGIVEIS_SEGUIDAS, MAX_TENTATIVAS = 3, 2, 8


def ler(linha):
    """A mesma leitura nas duas condições: a conta depois de ':' e os símbolos de divisão e multiplicação."""
    if not isinstance(linha, str):
        return ""
    s = linha.split(":")[-1].replace("÷", "/").replace("×", "*")
    return re.sub(r"\(.*?\)\s*$", "", s).strip()


def lidas(linhas):
    return [ler(l) for l in linhas if ler(l)]


def resolveu(linhas, x):
    ls = lidas(linhas)
    return bool(ls) and e1.raizes(ls[-1]) == {x} and e1.diagnostico(ls)[0] == "sem_quebra"


def persona(tarefa, historico):
    prompt = PROMPT_PERSONA + f"Equação: {tarefa}."
    if historico:
        prompt += " Você já tentou e recebeu este retorno: " + " | ".join(historico) + " Refaça a resolução."
    saida, _ = e1.qwen(PERSONA, prompt, ESQUEMA_PERSONA)
    linhas = saida.get("linhas") if isinstance(saida.get("linhas"), list) else None
    return linhas, "invalido" in saida or linhas is None


def sessao(cond, tarefa, x):
    reg = {"condicao": cond, "tarefa": tarefa, "tentativas": [], "pistas": 0, "professor": False,
           "json_invalido": 0, "linha_ilegivel": 0, "pistas_com_resposta": 0, "fim": None}
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
        tipo, k = e1.diagnostico(ls) if ls else ("invalida", 1)
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
        if cond == "A":  # gabarito do livro: só o resultado final, uma vez
            if ultimo == "gabarito":
                reg["fim"] = "não resolveu depois do gabarito"
                break
            historico.append(f"O gabarito diz que x = {x}.")
            ultimo = "gabarito"
            continue
        if reg["pistas"] == MAX_PISTAS:
            reg["professor"], reg["fim"] = True, "chamou o professor (3 pistas)"
            break
        saida, _ = e1.qwen(ATLAS, e1.PROMPT_ATLAS + f"Passos lidos: {ls} | SymPy: {e1.texto_diag(tipo, k, ls)}",
                           e1.ESQUEMA)
        pista = saida.get("dica_aluno", "")
        reg["pistas"] += 1
        reg["pistas_com_resposta"] += e1.pista_com_resposta(pista, {"linhas": ls, "x_correto": x})
        historico.append(f"O erro está na linha {k}. Dica: {pista}")
        ultimo = "pista"
    reg["fim"] = reg["fim"] or "sem fim"
    reg["tempo"] = time.perf_counter() - t0
    return reg


def listas_pareadas(r, n=10):
    pre, prova = [], []
    for _ in range(n):
        a, b = r.randint(2, 6), r.choice([m for m in range(-9, 10) if m])
        x1, x2 = r.sample(range(1, 10), 2)
        sinal = "+" if b > 0 else "-"
        b2 = (abs(b) % 9 + 1) * (1 if b > 0 else -1)
        pre.append((f"{a}x {sinal} {abs(b)} = {a * x1 + b}", x1))
        prova.append((f"{a}x {sinal} {abs(b2)} = {a * x2 + b2}", x2))
    return pre, prova


def perfil(lst):
    return [(int(eq.split("x")[0]), eq.split()[1]) for eq, _ in lst]


def main():
    r = random.Random(SEMENTE)
    RES.mkdir(exist_ok=True)
    ids = [f"P{i:02d}" for i in range(1, PARTICIPANTES + 1)]
    r.shuffle(ids)
    contagem = collections.Counter("A" if i < PARTICIPANTES // 2 else "B" for i in range(PARTICIPANTES))
    pre, prova = listas_pareadas(random.Random(SEMENTE + 1))
    regs = []
    for cond in ("A", "B"):
        for p in range(PERSONAS_POR_CONDICAO):
            rr = random.Random(SEMENTE + 100 * (cond == "B") + p)
            for _ in range(EXERCICIOS):
                tarefa, x = equacao(rr)
                regs.append(sessao(cond, tarefa, x))
                print(cond, regs[-1]["fim"], regs[-1]["pistas"], flush=True)
    linhas_tab = []
    for cond, nome in (("A", "A · gabarito do livro"), ("B", "B · Atlas")):
        s = [g for g in regs if g["condicao"] == cond]
        fins = collections.Counter(g["fim"] for g in s)
        linhas_tab.append(
            f"| {nome} | {len(s)} | {fins.get('resolveu de primeira', 0)} | {fins.get('resolveu depois da pista', 0)} | "
            f"{fins.get('resolveu depois do gabarito', 0)} | {fins.get('resolveu depois de reescrever', 0)} | "
            f"{fins.get('chamou o professor (3 pistas)', 0)} | {fins.get('chamou o professor (ilegível)', 0)} | "
            f"{sum(g['pistas'] for g in s) / len(s):.2f} | {sum(g['json_invalido'] for g in s)} | "
            f"{sum(g['linha_ilegivel'] for g in s)} | {sum(g['pistas_com_resposta'] for g in s)} de {sum(g['pistas'] for g in s)} | "
            f"{fins.get('sem fim', 0) + fins.get('não resolveu depois do gabarito', 0)} |")
    texto = (
        "# Piloto do E2 · segunda versão do protocolo, com persona de IA\n\n"
        "Gerada por `piloto_e2_v2.py`. A persona é um modelo de linguagem: os números abaixo testam o protocolo, "
        "não dizem nada sobre alunos.\n\n"
        f"- sorteio de {PARTICIPANTES} participantes: {contagem['A']} em A e {contagem['B']} em B\n"
        f"- pré-teste e prova pareados: mesmo perfil de coeficientes e sinais: {perfil(pre) == perfil(prova)}; "
        f"nenhuma equação repetida: {not set(e for e, _ in pre) & set(e for e, _ in prova)}\n\n"
        "| condição | exercícios | resolvidos de primeira | depois da pista | depois do gabarito | depois de reescrever | "
        "professor: 3 pistas | professor: 2 leituras ilegíveis | pistas por exercício | JSON inválido da persona | "
        "linhas que o SymPy não lê | pistas com a resposta | terminou sem resolver |\n"
        "|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|\n" + "\n".join(linhas_tab) + "\n")
    (RES / "e2_v2.md").write_text(texto, encoding="utf-8")
    with open(RES / "e2_v2_sessoes.jsonl", "w", encoding="utf-8") as f:
        for g in regs:
            f.write(json.dumps(g, ensure_ascii=False) + "\n")
    print("\n" + texto)


if __name__ == "__main__":
    main()
