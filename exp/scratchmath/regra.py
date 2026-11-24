"""Pipeline determinística do Atlas (recorte por vãos, SymPy) + Regra das correções típicas.

Implementa o checklist determinístico descrito no Slide 2 e na Emenda 3 de exp/exp.md:
dada uma passagem quebrada (linha_anterior -> linha_atual), testa em ordem:
  1. troca_sinal   (passou termo de lado sem trocar o sinal)
  2. distributiva  (esqueceu de multiplicar todos os termos nos parênteses ou errou sinal)
  3. divisao       (errou ao isolar x dividindo pelo coeficiente)
  4. conta         (errou soma/subtração/multiplicação de constantes ou coeficientes)
  5. outro         (nenhum dos 4 acima explica a linha do aluno -> abstém / chama professor)
"""
import re
from typing import Optional, Tuple

from sympy import Add, Eq, Mul, Symbol, expand, parse_expr, solveset
from sympy.parsing.sympy_parser import (
    implicit_multiplication_application,
    rationalize,
    standard_transformations,
)

from categorias import MAPA_REGRA_PARA_SCRATCHMATH

X = Symbol("x")
TR = standard_transformations + (implicit_multiplication_application, rationalize)

PISTAS_FIXAS = {
    "troca_sinal": "Revise a passagem para a linha {k}: observe o termo que mudou de lado da igualdade e confira se o sinal foi invertido.",
    "distributiva": "Revise a passagem para a linha {k}: ao eliminar os parênteses, confira se o fator de fora multiplicou todos os termos de dentro.",
    "divisao": "Revise a passagem para a linha {k}: confira qual número deve dividir qual ao isolar a incógnita.",
    "conta": "Revise a passagem para a linha {k}: refaça com calma as operações numéricas entre os termos.",
    "outro": "Revise a passagem para a linha {k}: compare com a linha anterior passo a passo; se a dúvida continuar, chame o professor.",
}


def recortar_por_vaos(img):
    """Separa uma foto em faixas horizontais pelos vãos de tinta (mesma lógica do Atlas)."""
    cinza = img.convert("L")
    w, h = cinza.size
    # Para imagens grandes (> 1200 px de largura), reduz proporcionalmente para projeção rápida
    escala = 1.0
    if w > 1200:
        escala = 1200.0 / w
        cinza_p = cinza.resize((int(w * escala), int(h * escala)))
    else:
        cinza_p = cinza
    wp, hp = cinza_p.size
    px = cinza_p.load()
    tinta = [sum(1 for x in range(wp) if px[x, y] < 140) for y in range(hp)]
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
        faixas.append((ini, hp - 1))
    faixas = [(a, b) for a, b in faixas if b - a >= 12]
    recortes = []
    for a, b in faixas:
        y0 = max(0, int(a / escala) - 10)
        y1 = min(h, int(b / escala) + 10)
        recortes.append(img.crop((0, y0, w, y1)))
    return recortes


def _normalizar_latex(s: str) -> str:
    """Converte construções LaTeX comuns (frações, porcentagens, delimitadores) para sintaxe SymPy."""
    s = s.replace("\\left", "").replace("\\right", "")
    s = s.replace("\\times", "*").replace("\\cdot", "*").replace("\\div", "/")
    s = s.replace("\\%", "%").replace("\\,", " ").replace("\\;", " ")
    # Converte \frac{a}{b} (até 3 níveis aninhados) em ((a)/(b))
    for _ in range(3):
        novo = re.sub(r"\\frac\s*\{([^{}]+)\}\s*\{([^{}]+)\}", r"((\1)/(\2))", s)
        if novo == s:
            break
        s = novo
    # Converte porcentagens simples (ex.: 80% -> (80/100))
    s = re.sub(r"(\d+(?:\.\d+)?)\s*%", r"(\1/100)", s)
    s = s.replace("{", "(").replace("}", ")")
    return s


def _limpar_equacao(linha: str) -> Optional[Tuple[str, str]]:
    if not linha or "=" not in linha:
        return None
    s = linha.strip()
    s = _normalizar_latex(s)
    s = s.lower()
    s = s.replace("$", "").replace("−", "-").replace("–", "-").replace("—", "-")
    s = s.replace("×", "*").replace("÷", "/").replace("：", "").replace(":", "")
    s = re.sub(r"^(?:解|步骤\d+|linha\s*\d+)\s*", "", s)
    s = re.sub(r"[.,;]+\s*$", "", s)
    if s.count("=") != 1:
        return None
    a, b = s.split("=", 1)
    if not a.strip() or not b.strip():
        return None
    return a.strip(), b.strip()


def parse_equacao(linha: str):
    """Devolve (lhs, rhs) em SymPy ou None se ilegível."""
    partes = _limpar_equacao(linha)
    if not partes:
        return None
    try:
        ea = parse_expr(partes[0], transformations=TR, local_dict={"x": X})
        eb = parse_expr(partes[1], transformations=TR, local_dict={"x": X})
        # Rejeita símbolos inesperados que não sejam x (ex.: 's' lido no lugar de '5')
        if (ea.free_symbols | eb.free_symbols) - {X}:
            return None
        return ea, eb
    except Exception:
        return None


def raizes(linha: str):
    """Resolve a equação linear/algébrica em x; devolve FiniteSet/Set ou None se ilegível."""
    par = parse_equacao(linha)
    if par is None:
        return None
    try:
        return solveset(Eq(par[0], par[1]), X)
    except Exception:
        return None


def diagnosticar_sympy(linhas):
    """Retorna (status, linha_1based, descricao): status in {'quebra', 'sem_quebra', 'ilegivel'}."""
    if not linhas:
        return "ilegivel", 1, "nenhuma linha recortada"
    sols = [raizes(l) for l in linhas]
    for i, s in enumerate(sols):
        if s is None:
            return "ilegivel", i + 1, f"a linha {i + 1} ('{linhas[i]}') não pôde ser lida como equação em x"
        if i > 0 and s != sols[i - 1]:
            return "quebra", i + 1, f"quebra na linha {i + 1}: '{linhas[i - 1]}' -> '{linhas[i]}'"
    return "sem_quebra", None, "equivalência mantida"


def _termos(expr):
    return list(expr.args) if isinstance(expr, Add) else [expr]


def _forma_linear(lhs, rhs):
    """Se lhs - rhs for linear em x (a*x + b = 0), retorna (a, b) com a*x = -b; senão None."""
    diff = expand(lhs - rhs)
    if diff.is_polynomial(X) and diff.as_poly(X).degree() <= 1:
        p = diff.as_poly(X)
        a = p.nth(1)
        b = p.nth(0)
        return a, b
    return None


def _testa_troca_sinal(lhs1, rhs1, sol2) -> bool:
    """Testa se mover 1 termo de um lado (com >= 2 termos) ao outro SEM trocar o sinal reproduz sol2."""
    termos_l = _termos(expand(lhs1))
    termos_r = _termos(expand(rhs1))
    if len(termos_l) >= 2:
        for i, t in enumerate(termos_l):
            if t == 0:
                continue
            novo_l = Add(*(termos_l[:i] + termos_l[i + 1:]))
            novo_r = rhs1 + t  # erro: somou +t no outro lado em vez de subtrair
            try:
                if solveset(Eq(novo_l, novo_r), X) == sol2:
                    return True
            except Exception:
                pass
    if len(termos_r) >= 2:
        for i, t in enumerate(termos_r):
            if t == 0:
                continue
            novo_r = Add(*(termos_r[:i] + termos_r[i + 1:]))
            novo_l = lhs1 + t
            try:
                if solveset(Eq(novo_l, novo_r), X) == sol2:
                    return True
            except Exception:
                pass
    return False


def _variantes_distributiva(expr):
    """Gera versões quebradas de distribuição k*(t1 + t2 + ...) -> k*t1 + t2 + ... ou sinal invertido."""
    candidatas = []
    for sub in expr.atoms(Mul):
        soma = [a for a in sub.args if isinstance(a, Add)]
        fatores = [a for a in sub.args if not isinstance(a, Add)]
        if len(soma) == 1 and fatores:
            fator = Mul(*fatores)
            termos = list(soma[0].args)
            if len(termos) >= 2:
                for keep_idx in range(len(termos)):
                    quebrada = fator * termos[keep_idx] + Add(*(t for j, t in enumerate(termos) if j != keep_idx))
                    candidatas.append(expr.xreplace({sub: quebrada}))
                for flip_idx in range(len(termos)):
                    quebrada = Add(*(
                        (-fator * t if j == flip_idx else fator * t)
                        for j, t in enumerate(termos)
                    ))
                    candidatas.append(expr.xreplace({sub: quebrada}))
    return candidatas


def _testa_distributiva(linha1_raw, lhs1, rhs1, sol2) -> bool:
    if "(" not in linha1_raw:
        return False
    partes = _limpar_equacao(linha1_raw)
    if not partes:
        return False
    try:
        # evaluate=False preserva 3*(x + 4) sem auto-distribuir antes da inspeção
        raw_l = parse_expr(partes[0], transformations=TR, local_dict={"x": X}, evaluate=False)
        raw_r = parse_expr(partes[1], transformations=TR, local_dict={"x": X}, evaluate=False)
    except Exception:
        return False
    for cand_l in _variantes_distributiva(raw_l):
        try:
            if solveset(Eq(cand_l, rhs1), X) == sol2:
                return True
        except Exception:
            pass
    for cand_r in _variantes_distributiva(raw_r):
        try:
            if solveset(Eq(lhs1, cand_r), X) == sol2:
                return True
        except Exception:
            pass
    return False


def _testa_divisao(lhs1, rhs1, lhs2, rhs2, sol2) -> bool:
    """Testa erros típicos ao passar de a*x = c para x = ..."""
    # Linha 2 precisa estar na forma isolada (x = val ou val = x)
    if not ((lhs2 == X and X not in rhs2.free_symbols) or (rhs2 == X and X not in lhs2.free_symbols)):
        return False
    lin1 = _forma_linear(lhs1, rhs1)
    if lin1 is None:
        return False
    a, b = lin1  # a*x + b = 0 -> a*x = -b
    c = -b
    if a in (0, 1):
        return False
    candidatos_x = [c - a, c + a, c * a, -c / a]
    if c != 0:
        candidatos_x.append(a / c)
        candidatos_x.append(-a / c)
    # Também testa erro de 1 unidade na divisão inteira? Não — isso é erro de conta, não de regra de divisão.
    for val in candidatos_x:
        try:
            if solveset(Eq(X, val), X) == sol2:
                return True
        except Exception:
            pass
    return False


def _testa_conta(lhs1, rhs1, lhs2, rhs2) -> bool:
    """Se ambas são lineares com o mesmo coeficiente de x (ex.: 4x = 20 -> 4x = 16)
    ou mesma estrutura com apenas erro numérico nas constantes/divisão aritmética."""
    lin1 = _forma_linear(lhs1, rhs1)
    lin2 = _forma_linear(lhs2, rhs2)
    if lin1 is None or lin2 is None:
        return False
    a1, b1 = lin1
    a2, b2 = lin2
    # Caso 1: mesmo coeficiente de x (ex.: 2x + 8 = 20 -> 2x = 14, mas NÃO foi troca_sinal pois já testamos antes)
    if a1 != 0 and a1 == a2 and b1 != b2:
        return True
    # Caso 2: linha 2 isolou x (a2 == 1 ou -1) a partir de a1*x = -b1 mas deu outro número (erro na conta da divisão)
    if a1 not in (0, 1, -1) and a2 in (1, -1):
        return True
    return False


def classificar_por_regra(linha_anterior: str, linha_atual: str) -> str:
    """Classifica uma quebra (linha_anterior -> linha_atual) entre:
    'troca_sinal', 'distributiva', 'divisao', 'conta', ou 'outro'.
    """
    p1 = parse_equacao(linha_anterior)
    p2 = parse_equacao(linha_atual)
    if p1 is None or p2 is None:
        return "outro"
    lhs1, rhs1 = p1
    lhs2, rhs2 = p2
    sol2 = raizes(linha_atual)
    if sol2 is None:
        return "outro"

    # Ordem do checklist: distributiva (quando há parênteses), troca_sinal, divisao, conta
    if _testa_distributiva(linha_anterior, lhs1, rhs1, sol2):
        return "distributiva"
    if _testa_troca_sinal(lhs1, rhs1, sol2):
        return "troca_sinal"
    if _testa_divisao(lhs1, rhs1, lhs2, rhs2, sol2):
        return "divisao"
    if _testa_conta(lhs1, rhs1, lhs2, rhs2):
        return "conta"
    return "outro"


def rodar_regra_completa(linhas):
    """Executa SymPy + regra das correções típicas e retorna dict completo."""
    status, k, texto = diagnosticar_sympy(linhas)
    if status != "quebra":
        return {
            "status_sympy": status,
            "linha_quebra": k,
            "diag_texto": texto,
            "categoria_atlas": "outro",
            "categoria_scratchmath": None,
            "dica_aluno": PISTAS_FIXAS["outro"].format(k=k or 1),
        }
    cat_atlas = classificar_por_regra(linhas[k - 2], linhas[k - 1])
    cat_sm = MAPA_REGRA_PARA_SCRATCHMATH.get(cat_atlas)
    return {
        "status_sympy": status,
        "linha_quebra": k,
        "diag_texto": texto,
        "categoria_atlas": cat_atlas,
        "categoria_scratchmath": cat_sm,
        "dica_aluno": PISTAS_FIXAS[cat_atlas].format(k=k),
    }


if __name__ == "__main__":
    import json
    from pathlib import Path

    # 1. Testes unitários canônicos
    casos_teste = [
        (["2x + 8 = 20", "2x = 28", "x = 14"], "troca_sinal"),
        (["3(x + 4) = 21", "3x + 4 = 21", "3x = 17"], "distributiva"),
        (["4x = 20", "x = 16"], "divisao"),
        (["4x = 20", "x = 80"], "divisao"),
        (["-6x = -3", "x = -1/2"], "divisao"),
        (["4x + 6 = 22", "4x = 18", "x = 9/2"], "conta"),
        (["2x + 3 = 11", "5x = 11"], "outro"),
    ]
    for linhas, esperado in casos_teste:
        res = rodar_regra_completa(linhas)
        ok = "OK" if res["categoria_atlas"] == esperado else f"ERRO (deu {res['categoria_atlas']})"
        print(f"[{ok}] {linhas[:2]} -> esperado={esperado}, obtido={res['categoria_atlas']}")

    # 2. Validação no gabarito do piloto sintético existente (se presente)
    gab_path = Path(__file__).resolve().parent.parent / "piloto" / "dados" / "gabarito.json"
    if gab_path.exists():
        gab = json.loads(gab_path.read_text(encoding="utf-8"))
        erros = [c for c in gab if c["tipo"] != "sem_erro"]
        acertos = 0
        por_tipo = {}
        for c in erros:
            res = rodar_regra_completa(c["linhas"])
            t = c["tipo"]
            por_tipo.setdefault(t, [0, 0])
            por_tipo[t][1] += 1
            if res["categoria_atlas"] == t:
                acertos += 1
                por_tipo[t][0] += 1
        print(f"\nPiloto sintético (transcrição limpa, {len(erros)} casos com erro): {acertos}/{len(erros)} ({100*acertos/len(erros):.1f}%)")
        for t, (a, tot) in sorted(por_tipo.items()):
            print(f"  {t}: {a}/{tot}")
