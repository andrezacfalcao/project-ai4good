"""Piloto do E2: testa o protocolo com uma persona de IA, nunca a ideia.

A persona (qwen2.5:3b) faz o papel de um aluno que às vezes erra. Ela resolve exercícios nas duas
condições do pré-registro (exp.md, § 3): A, conferir pelo gabarito do livro; B, conferir com o Atlas
(SymPy + Qwen 1.5B, até 3 pistas, depois chama o professor). O que conta é o registro do que quebrou
no protocolo; os acertos da persona não dizem nada sobre alunos de verdade.

Rodar a partir da raiz, com o Ollama ativo:  tec/.venv/bin/python -I exp/piloto/piloto_e2.py
Saída: exp/piloto/resultados/e2.md e e2_sessoes.jsonl
"""
import collections
import json
import random
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import piloto_e1 as e1  # noqa: E402  (mesmas regras, prompt e detector de pista com a resposta)

RES = AQUI / "resultados"
PERSONA = "qwen2.5:3b"
ATLAS = "qwen2.5:1.5b"
SEMENTE = 2026
PARTICIPANTES = 30
PERSONAS_POR_CONDICAO, EXERCICIOS = 6, 5
MAX_PISTAS = 3

PROMPT_PERSONA = (
    'Responda APENAS JSON: {"linhas": [str]}. Você faz o papel de um aluno do 7º ano resolvendo uma equação do '
    "1º grau no caderno, uma passagem por linha, terminando em x = número. Às vezes você erra como um aluno erra: "
    "passa um termo para o outro lado sem trocar o sinal, ou erra uma conta.\n"
)
ESQUEMA_PERSONA = {"type": "object", "properties": {"linhas": {"type": "array", "items": {"type": "string"}}},
                   "required": ["linhas"]}


def equacao(r):
    a, x, b = r.randint(2, 6), r.randint(1, 9), r.choice([n for n in range(-9, 10) if n])
    return f"{a}x {'+' if b > 0 else '-'} {abs(b)} = {a * x + b}", x


def lista(r, n=10):
    return [equacao(r) for _ in range(n)]


def persona(tarefa, historico):
    prompt = PROMPT_PERSONA + f"Equação: {tarefa}."
    if historico:
        prompt += " Você já tentou e recebeu este retorno: " + " | ".join(historico) + " Refaça a resolução."
    saida, dt = e1.qwen(PERSONA, prompt, ESQUEMA_PERSONA)
    linhas = saida.get("linhas") if isinstance(saida.get("linhas"), list) else None
    return linhas, dt, "invalido" in saida or linhas is None


def resolveu(linhas, x):
    return bool(linhas) and e1.raizes(linhas[-1]) == {x} and e1.diagnostico(linhas)[0] == "sem_quebra"


def sessao(cond, tarefa, x):
    reg = {"condicao": cond, "tarefa": tarefa, "tentativas": [], "pistas": 0, "professor": False,
           "json_invalido": 0, "linha_ilegivel": 0, "pistas_com_resposta": 0, "fim": None}
    historico, t0 = [], time.perf_counter()
    for _ in range(MAX_PISTAS + 1):
        linhas, _, invalido = persona(tarefa, historico)
        reg["json_invalido"] += invalido
        reg["tentativas"].append(linhas)
        if not linhas:
            continue
        if resolveu(linhas, x):
            reg["fim"] = "resolveu de primeira" if len(reg["tentativas"]) == 1 else "resolveu depois da pista"
            break
        if cond == "A":  # gabarito do livro: só diz o resultado final
            historico.append(f"O gabarito diz que x = {x}.")
            reg["fim"] = "conferiu o gabarito"
            linhas, _, invalido = persona(tarefa, historico)
            reg["json_invalido"] += invalido
            reg["tentativas"].append(linhas)
            if resolveu(linhas, x):
                reg["fim"] = "resolveu depois do gabarito"
            break
        tipo, k = e1.diagnostico(linhas)
        if tipo == "invalida":
            reg["linha_ilegivel"] += 1
            historico.append(f"A linha {k} não pôde ser lida; reescreva-a.")
            continue
        if reg["pistas"] == MAX_PISTAS:
            reg["professor"] = True
            reg["fim"] = "chamou o professor"
            break
        saida, _ = e1.qwen(ATLAS, e1.PROMPT_ATLAS + f"Passos lidos: {linhas} | SymPy: {e1.texto_diag(tipo, k, linhas)}",
                           e1.ESQUEMA)
        pista = saida.get("dica_aluno", "")
        reg["pistas"] += 1
        reg["pistas_com_resposta"] += e1.pista_com_resposta(pista, {"linhas": linhas, "x_correto": x})
        historico.append(f"O erro está na linha {k}. Dica: {pista}")
    else:
        reg["fim"] = reg["fim"] or "sem fim"
    reg["fim"] = reg["fim"] or ("chamou o professor" if reg["professor"] else "sem fim")
    reg["tempo"] = time.perf_counter() - t0
    return reg


def main():
    r = random.Random(SEMENTE)
    RES.mkdir(exist_ok=True)
    # 1. sorteio balanceado das condições
    ids = [f"P{i:02d}" for i in range(1, PARTICIPANTES + 1)]
    r.shuffle(ids)
    alocacao = {p: ("A" if i < PARTICIPANTES // 2 else "B") for i, p in enumerate(ids)}
    contagem = collections.Counter(alocacao.values())
    # 2. pré-teste e prova: listas equivalentes, com a mesma distribuição de coeficientes
    pre, prova = lista(random.Random(SEMENTE + 1)), lista(random.Random(SEMENTE + 2))
    def perfil(l):
        return sorted((int(eq.split("x")[0]), eq.split()[1]) for eq, _ in l)
    equivalentes = [e for e, _ in pre] != [e for e, _ in prova]
    # 3. prática com a persona
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
            f"| {nome} | {len(s)} | {fins.get('resolveu de primeira', 0)} | "
            f"{fins.get('resolveu depois do gabarito', 0) + fins.get('resolveu depois da pista', 0)} | "
            f"{sum(g['professor'] for g in s)} | {sum(g['pistas'] for g in s) / len(s):.2f} | "
            f"{sum(g['json_invalido'] for g in s)} | {sum(g['linha_ilegivel'] for g in s)} | "
            f"{sum(g['pistas_com_resposta'] for g in s)} de {sum(g['pistas'] for g in s)} | "
            f"{fins.get('sem fim', 0)} | {sum(g['tempo'] for g in s) / len(s):.1f} |")
    texto = (
        "# Piloto do E2 · protocolo com persona de IA\n\n"
        "Gerada por `piloto_e2.py`. A persona é um modelo de linguagem: os números abaixo testam o protocolo, "
        "não dizem nada sobre alunos.\n\n"
        f"- sorteio de {PARTICIPANTES} participantes: {contagem['A']} em A e {contagem['B']} em B\n"
        f"- pré-teste e prova: 10 equações cada, sorteadas da mesma forma; listas diferentes entre si: {equivalentes}; "
        f"mesmo perfil de coeficientes e sinais: {perfil(pre) == perfil(prova)}\n\n"
        "| condição | exercícios | resolvidos de primeira | resolvidos depois do retorno (gabarito ou pista) | chamadas ao professor | "
        "pistas por exercício | JSON inválido da persona | linhas que o SymPy não lê | pistas com a resposta | "
        "sessões sem fim | tempo por exercício (s) |\n|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|\n"
        + "\n".join(linhas_tab) + "\n")
    (RES / "e2.md").write_text(texto, encoding="utf-8")
    with open(RES / "e2_sessoes.jsonl", "w", encoding="utf-8") as f:
        for g in regs:
            f.write(json.dumps(g, ensure_ascii=False) + "\n")
    print("\n" + texto)


if __name__ == "__main__":
    main()
