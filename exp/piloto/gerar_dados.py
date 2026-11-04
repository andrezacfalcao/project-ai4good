"""Gera as 60 resoluções sintéticas do piloto do E1, com o gabarito de cada uma.

Cada resolução é uma equação do 1º grau resolvida em 3 ou 4 linhas, com no máximo um erro injetado.
São 12 por tipo (troca_sinal, conta, distributiva, divisao, sem_erro), metade com fundo limpo e
metade com pauta azul e inclinação, em três fontes manuscritas de licença aberta (OFL).

Rodar a partir da raiz do repositório:  tec/.venv/bin/python -I exp/piloto/gerar_dados.py
Saída: exp/piloto/dados/imagens/*.png e exp/piloto/dados/gabarito.json
"""
import json
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = Path(__file__).resolve().parent
SAIDA = AQUI / "dados"
FONTES = ["PatrickHand-Regular.ttf", "Caveat.ttf", "Kalam-Regular.ttf"]
TIPOS = ["troca_sinal", "conta", "distributiva", "divisao", "sem_erro"]
POR_TIPO = 12
SEMENTE = 2026


def termo(a):
    return "x" if a == 1 else f"{a}x"


def sinal(b):
    return f"+ {b}" if b >= 0 else f"- {-b}"


def resolucao(tipo, r):
    """Devolve (linhas escritas, linha do erro com base 1 ou None, x correto, linha corrigida)."""
    while True:
        a, x = r.randint(2, 6), r.randint(1, 9)
        if tipo == "distributiva":
            b = r.randint(1, 6)
            c = a * (x + b)
            certas = [f"{a}(x + {b}) = {c}", f"{a}x + {a * b} = {c}", f"{termo(a)} = {c - a * b}", f"x = {x}"]
            ax = c - b  # o aluno esquece de multiplicar o b
            if ax % a or ax == c - a * b:
                continue
            linhas = [certas[0], f"{a}x + {b} = {c}", f"{termo(a)} = {ax}", f"x = {ax // a}"]
            return linhas, 2, x, certas[1]
        b = r.choice([n for n in range(-9, 10) if n not in (0,)])
        c = a * x + b
        certas = [f"{termo(a)} {sinal(b)} = {c}", f"{termo(a)} = {c - b}", f"x = {x}"]
        if tipo == "sem_erro":
            return certas, None, x, None
        if tipo == "troca_sinal":
            ax = c + b  # o termo muda de lado sem trocar o sinal
            if ax % a or ax == 0:
                continue
            return [certas[0], f"{termo(a)} = {ax}", f"x = {ax // a}"], 2, x, certas[1]
        if tipo == "conta":
            d = r.choice([-2, -1, 1, 2]) * a  # erro de conta que ainda dá divisão exata
            ax = c - b + d
            if ax == 0:
                continue
            return [certas[0], f"{termo(a)} = {ax}", f"x = {ax // a}"], 2, x, certas[1]
        if tipo == "divisao":
            errado = c - b - a  # subtrai o coeficiente em vez de dividir
            if errado == x:
                continue
            return [certas[0], certas[1], f"x = {errado}"], 3, x, certas[2]


def desenhar(linhas, fonte, pauta, r):
    w, passo, topo = 560, 96, 30
    h = topo * 2 + passo * len(linhas)
    img = Image.new("RGB", (w, h), (250, 249, 245))
    d = ImageDraw.Draw(img)
    if pauta:
        for y in range(topo + 70, h, 48):
            d.line([(0, y), (w, y)], fill=(160, 190, 235), width=2)
    f = ImageFont.truetype(str(AQUI / "fontes" / fonte), 56 if fonte == "Caveat.ttf" else 46)
    for i, l in enumerate(linhas):
        d.text((40 + r.randint(-8, 8), topo + i * passo + r.randint(-6, 6)), l, font=f, fill=(25, 25, 30))
    if pauta:
        img = img.rotate(r.uniform(2.0, 4.0) * r.choice([-1, 1]), expand=False, fillcolor=(250, 249, 245))
    return img.filter(ImageFilter.GaussianBlur(0.4))


def main():
    r = random.Random(SEMENTE)
    (SAIDA / "imagens").mkdir(parents=True, exist_ok=True)
    casos = []
    for tipo in TIPOS:
        for k in range(POR_TIPO):
            linhas, linha_erro, x, corrigida = resolucao(tipo, r)
            pauta = k % 2 == 1
            fonte = FONTES[k % 3]
            nome = f"{tipo}-{k + 1:02d}.png"
            desenhar(linhas, fonte, pauta, r).save(SAIDA / "imagens" / nome)
            casos.append({"imagem": f"imagens/{nome}", "tipo": tipo, "linhas": linhas, "linha_erro": linha_erro,
                          "x_correto": x, "linha_corrigida": corrigida, "foto": "pauta" if pauta else "limpa",
                          "fonte": fonte})
    (SAIDA / "gabarito.json").write_text(json.dumps(casos, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(casos)} resoluções em {SAIDA}")


if __name__ == "__main__":
    main()
