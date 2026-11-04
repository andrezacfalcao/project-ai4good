"""Tempo do SymPy (passo 6) e da contagem do atlas, sobre as linhas que o TrOCR leu no tec.

Rodar a partir da raiz: tec/.venv/bin/python -I flx/medidas/tempo_regras.py
"""
import collections, random, statistics, time
from sympy import Eq, Symbol, solveset
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

TR = standard_transformations + (implicit_multiplication_application,)

def raizes(l):  # mesma funcao de tec/ler_caderno.py
    if "=" not in l:
        return None
    a, b = l.lower().split("=", 1)
    return solveset(Eq(parse_expr(a, transformations=TR), parse_expr(b, transformations=TR)), Symbol("x"))

# linhas exatamente como o TrOCR as leu no tec (tec/resultados/adaptado.stdout.txt)
cadernos = [['2X + 4 =10', '2X = 10 + 4', 'X=7'], ['3X-6=9', '3X= 9 - 6', 'X=1'], ['4X+8-20', '4X=20+8', '* * *']]
raizes('2x=4')  # aquecimento
ts = []
for _ in range(20):
    for c in cadernos:
        t = time.perf_counter()
        for l in c:
            try:
                raizes(l)
            except Exception:
                pass
        ts.append(time.perf_counter() - t)
print(f"SymPy por caderno (3 linhas): mediana {statistics.median(ts)*1000:.1f} ms, max {max(ts)*1000:.1f} ms, n={len(ts)}")

# atlas: 120 entradas por mes (a escala do flx), contadas por exercicio e categoria
random.seed(0)
cats = ["troca_sinal", "distributiva", "aritmetica", "outro"]
entradas = [(f"ex{random.randint(1, 10)}", random.choice(cats)) for _ in range(120)]
ta = []
for _ in range(100):
    t = time.perf_counter()
    collections.Counter(entradas).most_common(5)
    ta.append(time.perf_counter() - t)
print(f"contagem do atlas (120 entradas): mediana {statistics.median(ta)*1e6:.0f} us, n={len(ta)}")
