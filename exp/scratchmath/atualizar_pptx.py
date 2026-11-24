"""Gera a apresentação completa e narrativa (10 slides) do Atlas do Erro no ScratchMath,
preservando fielmente a identidade visual e a voz humana dos slides originais da Andreza.

Reutiliza os 7 slides originais in-place (sem deletar parts do ZIP, evitando colisão de slideX.xml)
e adiciona 3 novos slides (slide8..slide10.xml), reordenando no final para a sequência narrativa 1..10.

Uso:
  .venv/bin/python exp/scratchmath/atualizar_pptx.py \
      --entrada <original_backup.pptx> \
      --saida "/Documents/deza/A pipeline do Atlas_ do caderno à pista.pptx"
"""
import argparse
import json
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

AQUI = Path(__file__).resolve().parent
M1_PATH = AQUI / "resultados" / "metricas.json"
M2_PATH = AQUI / "resultados_v2" / "metricas_v2.json"
FIG_DIR = AQUI / "resultados_v2" / "figuras"
IMG_ALUNO = AQUI / "dados" / "imagens" / "000_a0916973ce57681ca8bddd2cae12d15d.jpg"

# Paleta fiel ao deck original
BG_CLARO = RGBColor(0xF8, 0xF7, 0xF3)
NAVY = RGBColor(0x1E, 0x2B, 0x4A)
CARD = RGBColor(0xEC, 0xEF, 0xF5)
AZUL = RGBColor(0x2F, 0x6F, 0xB5)
AZUL_ESC = RGBColor(0x24, 0x54, 0x8F)
AZUL_BADGE = RGBColor(0xDC, 0xE6, 0xF5)
CINZA = RGBColor(0x47, 0x52, 0x66)
CINZA_SUAVE = RGBColor(0x7A, 0x84, 0x96)
CINZA_BADGE = RGBColor(0xE3, 0xE6, 0xEB)
BRANCO = RGBColor(0xFF, 0xFF, 0xFF)
FUNDO_VERM = RGBColor(0xF7, 0xDE, 0xE0)
VERM = RGBColor(0xB9, 0x28, 0x3A)
FUNDO_AMBAR = RGBColor(0xF6, 0xEA, 0xD2)
AMBAR = RGBColor(0x7D, 0x52, 0x00)
FUNDO_VERDE = RGBColor(0xDC, 0xEF, 0xE3)
VERDE = RGBColor(0x1F, 0x6E, 0x44)
TEXTO_ESCURO_BG = RGBColor(0xF5, 0xF2, 0xEA)
SUB_ESCURO_BG = RGBColor(0xC9, 0xD3, 0xE4)
AZUL_CLARO = RGBColor(0x9C, 0xC0, 0xF0)
ROSA_CLARO = RGBColor(0xF0, 0xA8, 0xB0)


def fmt_pct(v: float) -> str:
    return f"{100 * v:.1f}%".replace(".", ",")


def fmt_num(v: float, casas=3) -> str:
    return f"{v:.{casas}f}".replace(".", ",")


def set_notes(slide, texto: str):
    tf = slide.notes_slide.notes_text_frame
    tf.clear()
    tf.paragraphs[0].text = texto


def limpar_slide(slide, cor_bg=BG_CLARO):
    for sh in list(slide.shapes):
        sh._element.getparent().remove(sh._element)
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = cor_bg
    return slide


def novo_slide_limpo(prs, cor_bg=BG_CLARO):
    blank = prs.slide_layouts[6] if len(prs.slide_layouts) > 6 else prs.slide_layouts[0]
    return limpar_slide(prs.slides.add_slide(blank), cor_bg=cor_bg)


def set_shape_text(shape, texto: str, font_name=None, size_pt=None, bold=None, color=None, align=None):
    tf = shape.text_frame
    orig_name, orig_size, orig_bold, orig_color = None, None, None, None
    for p in tf.paragraphs:
        for r in p.runs:
            if r.text.strip():
                orig_name = r.font.name
                orig_size = r.font.size
                orig_bold = r.font.bold
                try:
                    if r.font.color and r.font.color.type == 1:
                        orig_color = r.font.color.rgb
                except Exception:
                    pass
                break
        if orig_name:
            break
    tf.clear()
    tf.word_wrap = True
    for idx, linha in enumerate(texto.split("\n")):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        if align is not None:
            p.alignment = align
        r = p.add_run()
        r.text = linha
        r.font.name = font_name or orig_name or "Inter"
        r.font.size = Pt(size_pt) if size_pt is not None else (orig_size or Pt(9.5))
        r.font.bold = bold if bold is not None else (orig_bold if orig_bold is not None else False)
        if color is not None:
            r.font.color.rgb = color
        elif orig_color is not None:
            r.font.color.rgb = orig_color


def add_rect(slide, x, y, w, h, fill_cor, line_cor=None, radius=False, line_pt=1.0):
    tipo = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    sh = slide.shapes.add_shape(tipo, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill_cor
    if line_cor:
        sh.line.color.rgb = line_cor
        sh.line.width = Pt(line_pt)
    else:
        sh.line.fill.background()
    return sh


def add_textbox(slide, x, y, w, h, texto, font_name="Inter", size_pt=9.5, bold=False, color=NAVY, align=PP_ALIGN.LEFT, line_spacing=None):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.03)
    tf.margin_right = Inches(0.03)
    tf.margin_top = Inches(0.02)
    tf.margin_bottom = Inches(0.02)
    for idx, linha in enumerate(texto.split("\n")):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p.alignment = align
        if line_spacing:
            p.line_spacing = line_spacing
        r = p.add_run()
        r.text = linha
        r.font.name = font_name
        r.font.size = Pt(size_pt)
        r.font.bold = bold
        r.font.color.rgb = color
    return tb


def add_badge(slide, x, y, w, h, texto, fill_cor, txt_cor, size_pt=8.2):
    sh = add_rect(slide, x, y, w, h, fill_cor, radius=True)
    tf = sh.text_frame
    tf.word_wrap = False
    tf.margin_left = Inches(0.04)
    tf.margin_right = Inches(0.04)
    tf.margin_top = Inches(0.01)
    tf.margin_bottom = Inches(0.01)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = texto
    r.font.name = "Inter"
    r.font.size = Pt(size_pt)
    r.font.bold = True
    r.font.color.rgb = txt_cor
    return sh


def style_cell(cell, texto, size_pt=8.6, bold=False, color=NAVY, fill_cor=None, align=PP_ALIGN.LEFT):
    cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    cell.margin_left = Inches(0.08)
    cell.margin_right = Inches(0.08)
    cell.margin_top = Inches(0.04)
    cell.margin_bottom = Inches(0.04)
    if fill_cor is not None:
        cell.fill.solid()
        cell.fill.fore_color.rgb = fill_cor
    tf = cell.text_frame
    tf.clear()
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = texto
    r.font.name = "Inter"
    r.font.size = Pt(size_pt)
    r.font.bold = bold
    r.font.color.rgb = color


def add_rodape(slide, num_slide: int, total: int, escuro=False):
    cor = SUB_ESCURO_BG if escuro else CINZA_SUAVE
    add_textbox(slide, 0.60, 5.26, 5.0, 0.24, "Andreza Falcão · Atlas do Erro · ScratchMath",
                font_name="Inter", size_pt=7.8, bold=False, color=cor)
    add_textbox(slide, 8.40, 5.26, 1.0, 0.24, f"{num_slide} / {total}",
                font_name="Inter", size_pt=7.8, bold=False, color=cor, align=PP_ALIGN.RIGHT)


def reordenar_slides(prs, nova_ordem):
    sldIdLst = prs.slides._sldIdLst
    elementos = [sldIdLst[i] for i in range(len(sldIdLst))]
    for el in elementos:
        sldIdLst.remove(el)
    for idx in nova_ordem:
        sldIdLst.append(elementos[idx])


# ================= CONSTRUÇÃO DOS SLIDES NARRATIVOS =================

def preencher_slide4_metodologia(s):
    """Slide 4: Como eu montei o teste — metodologia em dois ciclos."""
    limpar_slide(s)
    add_textbox(s, 0.60, 0.42, 8.8, 0.40, "Como eu montei o teste: metodologia em dois ciclos",
                font_name="Merriweather", size_pt=19.5, bold=True, color=NAVY)
    add_textbox(s, 0.60, 0.84, 8.8, 0.26,
                "Em vez de inventar folhas, rodei tudo nas 241 folhas reais do ScratchMath (7º ao 9º ano), localmente, sem treinar nada.",
                font_name="Inter", size_pt=9.2, bold=False, color=CINZA)

    # Card Ciclo 1
    add_rect(s, 0.60, 1.22, 4.28, 2.20, CARD)
    add_rect(s, 0.60, 1.22, 4.28, 0.06, AMBAR)
    add_badge(s, 0.76, 1.38, 0.90, 0.24, "CICLO 1", FUNDO_AMBAR, AMBAR, size_pt=8.0)
    add_textbox(s, 1.74, 1.38, 3.00, 0.24, "Testar o Atlas como estava",
                font_name="Merriweather", size_pt=11.0, bold=True, color=NAVY)
    add_textbox(s, 0.76, 1.72, 3.96, 1.64,
                "• 241 folhas originais (em chinês), sem tradução prévia.\n"
                "• Dicionário fixo das 7 categorias + saída em JSON fechado.\n"
                "• Camada A: pipeline inteira (TrOCR-printed → SymPy → Regra/IA).\n"
                "• Camada B: Passo 3 isolado (Qwen2.5 1.5B × Gemma2 2B).\n"
                "• Camada C: Qwen2.5-VL 3B lendo a foto real direto.",
                font_name="Inter", size_pt=8.6, bold=False, color=NAVY, line_spacing=1.18)

    add_textbox(s, 4.89, 2.08, 0.24, 0.40, "→", font_name="Merriweather", size_pt=16, bold=True, color=AZUL, align=PP_ALIGN.CENTER)

    # Card Ciclo 2
    add_rect(s, 5.14, 1.22, 4.26, 2.20, CARD)
    add_rect(s, 5.14, 1.22, 4.26, 0.06, AZUL)
    add_badge(s, 5.30, 1.38, 0.90, 0.24, "CICLO 2", AZUL_BADGE, AZUL_ESC, size_pt=8.0)
    add_textbox(s, 6.28, 1.38, 3.00, 0.24, "Corrigir o que quebrou",
                font_name="Merriweather", size_pt=11.0, bold=True, color=NAVY)
    add_textbox(s, 5.30, 1.72, 3.94, 1.64,
                "• Recorte no escopo do Atlas: 57 equações do 1º grau (de 241).\n"
                "• Tradução local das 241 folhas para português (Qwen2.5 7B).\n"
                "• 3 novos leitores no Passo 1: Pix2Text (CPU), Qwen2.5-VL 3B e 7B.\n"
                "• Passo 3 justo: Regra × Qwen 1.5B × Gemma 2B × Qwen 7B.\n"
                "• Reavaliação nas 241 folhas em português + juiz de explicação.",
                font_name="Inter", size_pt=8.6, bold=False, color=NAVY, line_spacing=1.18)

    # Cartão inferior esquerdo: Mapeamento da regra
    add_rect(s, 0.60, 3.58, 4.28, 1.52, CARD)
    add_textbox(s, 0.76, 3.66, 3.96, 0.22, "Da regra sem IA para as 7 classes do artigo",
                font_name="Inter", size_pt=9.0, bold=True, color=AZUL)
    sh_t = s.shapes.add_table(4, 2, Inches(0.76), Inches(3.92), Inches(3.96), Inches(1.06))
    t = sh_t.table
    t.columns[0].width = Inches(1.88)
    t.columns[1].width = Inches(2.08)
    rows_m = [
        ("A regra diz", "Vira no ScratchMath", True),
        ("conta", "erro de cálculo", False),
        ("sinal, parêntese, divisão", "lacuna de conhecimento", False),
        ("outro / ilegível", "sem resposta (conta como erro)", False),
    ]
    for ri, (c0, c1, is_h) in enumerate(rows_m):
        bg = NAVY if is_h else (BRANCO if ri % 2 == 1 else CARD)
        fg = BRANCO if is_h else NAVY
        style_cell(t.cell(ri, 0), c0, size_pt=8.0, bold=is_h, color=fg, fill_cor=bg)
        style_cell(t.cell(ri, 1), c1, size_pt=8.0, bold=is_h, color=fg, fill_cor=bg)

    # Cartão inferior direito: Rigor
    add_rect(s, 5.14, 3.58, 4.26, 1.52, CARD)
    add_textbox(s, 5.30, 3.66, 3.94, 0.22, "Como o teste garantiu comparação justa",
                font_name="Inter", size_pt=9.0, bold=True, color=AZUL)
    add_textbox(s, 5.30, 3.92, 3.94, 1.10,
                "• Tudo rodou localmente (Ollama + RTX 5070), temperature = 0.\n"
                "• Sem API paga: até a tradução e o juiz de explicação (Qwen2.5 7B) rodaram na máquina.\n"
                "• Métricas com intervalo de 95% por bootstrap (2.000 reamostras) + checagem de vazamento da resposta.",
                font_name="Inter", size_pt=8.5, bold=False, color=NAVY, line_spacing=1.18)

    set_notes(s, (
        "[~75 s] Em vez de inventar folhas em casa, eu rodei o teste nas 241 folhas reais do ScratchMath — todas anotadas por cinco professores. "
        "A metodologia aconteceu em dois ciclos. No Ciclo 1, eu testei o Atlas exatamente do jeito que ele estava: TrOCR impresso, SymPy, a regra sem IA "
        "e os modelos pequenos Qwen2.5 1.5B e Gemma2 2B, além do Qwen2.5-VL 3B olhando a foto direto. "
        "Quando vi onde o Ciclo 1 quebrou, abri o Ciclo 2 para separar cada causa: filtrei as 57 equações do 1º grau — que são o escopo real do Atlas —, "
        "traduzi todas as 241 folhas para português localmente com o Qwen2.5 7B, sem usar API paga, e troquei o leitor do Passo 1 por três opções feitas "
        "para matemática: Pix2Text na CPU, Qwen2.5-VL 3B e Qwen2.5-VL 7B. Tudo rodou na mesma máquina, com temperature zero e a mesma régua do artigo."
    ))


def preencher_slide5_ciclo1(s, m1: dict):
    """Slide 5: Ciclo 1 — o primeiro choque com cadernos de verdade (241 folhas)."""
    limpar_slide(s)
    add_textbox(s, 0.60, 0.42, 8.8, 0.40, "Ciclo 1: o primeiro choque com cadernos de verdade",
                font_name="Merriweather", size_pt=19.5, bold=True, color=NAVY)
    add_textbox(s, 0.60, 0.84, 8.8, 0.26,
                "241 folhas reais do ScratchMath (7º ao 9º ano), testando a pipeline original antes de qualquer ajuste.",
                font_name="Inter", size_pt=9.2, bold=False, color=CINZA)

    c = m1["condicoes"]
    ece = m1["ece_local"]
    maj = m1["majority_baseline"]

    headers = ["Quem rodou (Ciclo 1 · N = 241)", "Conseguiu ler", "Classificar (7 tipos)", "F1 Macro", "Explicar (juiz 7B)", "Vazou resposta"]
    col_ws = [3.22, 1.05, 1.32, 0.85, 1.15, 1.21]
    linhas = [
        ("Chute (sempre \"erro de cálculo\")", "241/241", fmt_pct(maj["acc"]), fmt_num(maj["f1_macro"]), "—", "—", FUNDO_AMBAR, True),
        ("Atlas atual (TrOCR-printed + SymPy + Regra/IA)", "0/241 (0%)", "0,0%", "0,000", "0,0%", "0 (nunca chutou)", CARD, False),
        ("Qwen2.5 1.5B (só enunciado e solução)", "240/241", fmt_pct(c["B1_texto_qwen25_1.5b"]["acc"]), fmt_num(c["B1_texto_qwen25_1.5b"]["f1_macro"]), fmt_pct(ece["B1_texto_qwen25_1.5b"]["acc"]), "7 dicas (2,9%)", BRANCO, False),
        ("Gemma2 2B (só enunciado e solução)", "241/241", fmt_pct(c["B2_texto_gemma2_2b"]["acc"]), fmt_num(c["B2_texto_gemma2_2b"]["f1_macro"]), fmt_pct(ece["B2_texto_gemma2_2b"]["acc"]), "0 dicas (0%)", CARD, False),
        ("Qwen2.5-VL 3B (olhando a foto direto)", "240/241", fmt_pct(c["C1_visao_qwen25vl_3b"]["acc"]), fmt_num(c["C1_visao_qwen25vl_3b"]["f1_macro"]), fmt_pct(ece["C1_visao_qwen25vl_3b"]["acc"]), "1 dica (0,4%)", BRANCO, False),
    ]

    sh_t = s.shapes.add_table(len(linhas) + 1, len(headers), Inches(0.60), Inches(1.20), Inches(sum(col_ws)), Inches(2.40))
    t = sh_t.table
    for ci, w in enumerate(col_ws):
        t.columns[ci].width = Inches(w)
    for ci, h in enumerate(headers):
        al = PP_ALIGN.LEFT if ci == 0 else PP_ALIGN.RIGHT
        style_cell(t.cell(0, ci), h, size_pt=8.4, bold=True, color=BRANCO, fill_cor=NAVY, align=al)
    for ri, row in enumerate(linhas, 1):
        *vals, bg, is_b = row
        for ci, val in enumerate(vals):
            al = PP_ALIGN.LEFT if ci == 0 else PP_ALIGN.RIGHT
            cor = AMBAR if (ri == 1 and ci in (0, 2)) else (VERM if (ci == 5 and val.startswith(("7", "1"))) else NAVY)
            style_cell(t.cell(ri, ci), val, size_pt=8.4, bold=(is_b or ci == 2), color=cor, fill_cor=bg, align=al)

    add_textbox(s, 0.60, 3.68, 8.80, 0.26,
                "Para lembrar a tabela do artigo nas mesmas 241 folhas: Professores 81,5% · o4-mini 47,3% · Gemma-3 27B 46,1% · Qwen2.5-VL 7B 11,6%.",
                font_name="Inter", size_pt=8.0, bold=False, color=CINZA)

    add_rect(s, 0.60, 4.02, 8.80, 1.08, FUNDO_AMBAR)
    add_rect(s, 0.60, 4.02, 0.08, 1.08, AMBAR)
    add_textbox(s, 0.80, 4.10, 8.45, 0.22, "O que o Ciclo 1 revelou na hora (e puxou o Ciclo 2)",
                font_name="Inter", size_pt=9.6, bold=True, color=AMBAR)
    add_textbox(s, 0.80, 4.34, 8.45, 0.72,
                "1. O TrOCR de texto impresso falhou em 100% das fotos à mão — a regra e o SymPy nem chegaram a trabalhar.\n"
                "2. O Qwen2.5-VL 3B pareceu ir bem (46,5%), mas só porque chutou \"erro de cálculo\" em 234 das 241 folhas (F1 = 0,092).\n"
                "3. O passo seguinte ficou óbvio: trocar o leitor do Passo 1, filtrar o escopo do Atlas e traduzir para português.",
                font_name="Inter", size_pt=8.5, bold=False, color=NAVY, line_spacing=1.18)

    set_notes(s, (
        "[~80 s] Olha o que aconteceu na primeira tentativa, com o Atlas exatamente como estava. "
        "O choque veio já no Passo 1: o TrOCR que eu usava foi treinado em texto impresso, não em rascunho à mão. "
        "Ele não conseguiu ler nenhuma das 241 fotos de forma que o SymPy aceitasse — cobertura zero. "
        "Pelo menos a regra cumpriu o combinado: não chutou nada. "
        "Quando eu testei os modelos pequenos só com o enunciado e a solução, o Qwen 1.5B acertou 26,1% e vazou a resposta em 7 dicas, "
        "e o Gemma2 2B ficou em 9,1%. Já o Qwen2.5-VL 3B olhando a foto pareceu ir bem com 46,5% — só que o F1 Macro de 0,092 entregou o truque: "
        "ele chamou 234 de 241 folhas de 'erro de cálculo', e na hora de explicar o erro acertou só 4,1%. "
        "Esse diagnóstico deixou claro o que testar no Ciclo 2: trocar o leitor do caderno, focar nas equações do 1º grau e traduzir para português."
    ))


def build_slide6_ocr_virada(prs):
    """Slide 6: Ciclo 2 · Passo 1 — trocamos o leitor e o Atlas voltou a enxergar."""
    s = novo_slide_limpo(prs)
    add_textbox(s, 0.60, 0.42, 8.8, 0.40, "Ciclo 2 · Passo 1: trocamos o leitor — e o Atlas enxergou",
                font_name="Merriweather", size_pt=19.0, bold=True, color=NAVY)
    add_textbox(s, 0.60, 0.84, 8.8, 0.26,
                "Nas 57 equações do 1º grau (escopo real do Atlas), trocamos o TrOCR-printed por 3 leitores de matemática.",
                font_name="Inter", size_pt=9.2, bold=False, color=CINZA)

    # Esquerda: gráfico limpo
    s.shapes.add_picture(str(FIG_DIR / "grafico_ocr.png"), Inches(0.55), Inches(1.18), width=Inches(5.15))

    # Direita: exemplo real com a foto do aluno
    add_rect(s, 5.85, 1.18, 3.55, 2.94, CARD)
    add_textbox(s, 6.00, 1.26, 3.25, 0.22, "Exemplo real · folha 000 do ScratchMath",
                font_name="Inter", size_pt=8.8, bold=True, color=AZUL)
    add_rect(s, 6.00, 1.52, 3.25, 1.38, BRANCO, line_cor=CINZA_BADGE)
    s.shapes.add_picture(str(IMG_ALUNO), Inches(6.06), Inches(1.56), width=Inches(3.12))

    add_rect(s, 6.00, 2.98, 3.25, 0.44, FUNDO_VERM)
    add_textbox(s, 6.08, 3.01, 3.10, 0.38,
                "TrOCR-printed leu: \"***\"\n→ SymPy travou (ilegível)",
                font_name="Courier New", size_pt=7.7, bold=True, color=VERM)

    add_rect(s, 6.00, 3.48, 3.25, 0.56, FUNDO_VERDE)
    add_textbox(s, 6.08, 3.51, 3.10, 0.50,
                "Qwen2.5-VL leu: 4x-60+3x=6x-63+7x\n-6x=-3  →  SymPy achou a quebra!",
                font_name="Courier New", size_pt=7.7, bold=True, color=VERDE)

    add_rect(s, 0.60, 4.24, 8.80, 0.86, FUNDO_VERDE)
    add_rect(s, 0.60, 4.24, 0.08, 0.86, VERDE)
    add_textbox(s, 0.80, 4.32, 8.45, 0.22, "A virada da pipeline: a IA só transcreve, o SymPy confere",
                font_name="Inter", size_pt=9.6, bold=True, color=VERDE)
    add_textbox(s, 0.80, 4.56, 8.45, 0.50,
                "O modelo de visão não opina nem corrige o erro: ele só copia as linhas do caderno. "
                "Com isso, saímos de 0% para 49,1% com Qwen2.5-VL 3B — e até o Pix2Text, rodando só na CPU (1,7 s/folha), chegou a 43,9%.",
                font_name="Inter", size_pt=8.7, bold=False, color=NAVY, line_spacing=1.15)

    set_notes(s, (
        "[~75 s] Aqui está o momento em que o projeto virou. Das 241 folhas do artigo, 57 são exatamente equações do 1º grau — o escopo do Atlas. "
        "Eu testei três leitores novos nesse conjunto, comparando com o TrOCR antigo. "
        "O resultado saltou de zero para quase metade das folhas: o Pix2Text, rodando só em CPU e levando menos de dois segundos por folha, "
        "já fez 43,9%; o Qwen2.5-VL 7B fez 47,4%; e o Qwen2.5-VL 3B chegou a 49,1% — 28 de 57 quebras encontradas pelo SymPy. "
        "Olha a foto real de um aluno ali na direita: onde o TrOCR antigo só leu três asteriscos, o Qwen2.5-VL transcreveu as equações certinho, "
        "sem corrigir o erro do aluno, e o SymPy achou a quebra na hora. A sacada aqui é simples: usar a IA só para ler a letra, e deixar a conta com o SymPy."
    ))
    return s


def build_slide7_ciclo2_passo3(prs):
    """Slide 7: Ciclo 2 · Passo 3 — com leitura e português, quem ganhou?"""
    s = novo_slide_limpo(prs)
    add_textbox(s, 0.60, 0.42, 8.8, 0.42, "Ciclo 2 · Passo 3: com leitura e português, quem ganhou?",
                font_name="Merriweather", size_pt=18.5, bold=True, color=NAVY)
    add_textbox(s, 0.60, 0.84, 8.8, 0.26,
                "Com o leitor novo funcionando, comparamos Regra × Qwen × Gemma de igual para igual (em português).",
                font_name="Inter", size_pt=9.2, bold=False, color=CINZA)

    # Esquerda: gráfico N = 57
    s.shapes.add_picture(str(FIG_DIR / "grafico_ciclo2.png"), Inches(0.55), Inches(1.16), width=Inches(5.25))

    # Direita superior
    add_rect(s, 5.92, 1.18, 3.48, 1.40, CARD)
    add_rect(s, 5.92, 1.18, 3.48, 0.06, VERDE)
    add_textbox(s, 6.06, 1.28, 3.22, 0.22, "Nas 57 equações do 1º grau",
                font_name="Inter", size_pt=9.0, bold=True, color=VERDE)
    add_textbox(s, 6.06, 1.52, 3.22, 1.00,
                "• A Regra (12,3% geral · 33,3% quando responde) venceu Qwen 1.5B (8,8%) e Gemma2 2B (1,8%).\n"
                "• Só o Qwen 7B (5× maior) passou a regra.\n"
                "• Separar OCR 3B → Qwen 7B explicou melhor (12,3% ECE) que o VLM 7B na foto (5,3%).",
                font_name="Inter", size_pt=8.1, bold=False, color=NAVY, line_spacing=1.15)

    # Direita inferior
    add_rect(s, 5.92, 2.66, 3.48, 1.48, CARD)
    add_rect(s, 5.92, 2.66, 3.48, 0.06, AZUL)
    add_textbox(s, 6.06, 2.76, 3.22, 0.22, "O que traduzir para PT-BR mudou (241)",
                font_name="Inter", size_pt=9.0, bold=True, color=AZUL)
    add_textbox(s, 6.06, 3.00, 3.22, 1.08,
                "• Qwen2.5 1.5B: 26,1% → 39,8% (+13,7 pp)\n"
                "   F1 subiu 0,091 → 0,153 · mas 5 dicas vazaram.\n"
                "• Gemma2 2B: 9,1% → 9,1% (0 pp!)\n"
                "   Prova que o problema não era o chinês.\n"
                "• Qwen2.5-VL 7B (foto+PT): 38,6% · 6,2% ECE.",
                font_name="Inter", size_pt=8.1, bold=False, color=NAVY, line_spacing=1.16)

    # Faixa vermelha de veredito
    add_rect(s, 0.60, 4.24, 8.80, 0.86, FUNDO_VERM)
    add_rect(s, 0.60, 4.24, 0.08, 0.86, VERM)
    add_textbox(s, 0.80, 4.31, 8.45, 0.22, "Veredito pela régua combinada antes do teste: CAIU",
                font_name="Inter", size_pt=9.6, bold=True, color=VERM)
    add_textbox(s, 0.80, 4.55, 8.45, 0.50,
                "Mesmo em português e com transcrição real, nenhuma IA pequena (1,5B ou 2B) venceu a regra sem IA — "
                "e nenhum modelo local bateu o chute majoritário (56,1% nas 57 equações · 46,9% nas 241 folhas).",
                font_name="Inter", size_pt=8.6, bold=False, color=NAVY, line_spacing=1.15)

    set_notes(s, (
        "[~85 s] Com o leitor novo entregando equações de verdade para o SymPy e com tudo traduzido para português, "
        "o confronto no Passo 3 ficou finalmente justo — e a resposta foi ainda mais clara. "
        "Olhando o gráfico à esquerda, nas 57 equações do 1º grau: a regra sem IA acertou 12,3% no geral e 33,3% quando responde, "
        "ganhando tanto do Qwen2.5 1.5B (8,8%) quanto do Gemma2 2B (1,8%), sem vazar nenhuma resposta. "
        "Só quando eu subi para um modelo cinco vezes maior, o Qwen2.5 7B, a IA passou a regra — e ainda ficou abaixo do chute de 56,1%. "
        "Um achado legal de arquitetura: separar a leitura com o VLM 3B e passar o texto para o Qwen 7B explicou mais que o dobro de erros "
        "(12,3% contra 5,3%) do que jogar a foto direto no VLM 7B. "
        "E na direita, traduzindo as 241 folhas para português: o Qwen 1.5B melhorou quase 14 pontos, mas o Gemma2 2B ficou cravado nos mesmos 9,1%, "
        "provando que a falha não era o idioma chinês. Pela minha própria régua, a hipótese para o Passo 3 caiu."
    ))
    return s


def build_slide8_exemplos(prs):
    """Slide 8: O que a IA escreveu de verdade — exemplos concretos dos logs."""
    s = novo_slide_limpo(prs)
    add_textbox(s, 0.60, 0.42, 8.8, 0.40, "Por dentro dos números: o que a IA escreveu de verdade",
                font_name="Merriweather", size_pt=19.0, bold=True, color=NAVY)
    add_textbox(s, 0.60, 0.84, 8.8, 0.26,
                "Três exemplos reais dos registros que mostram por que não dá para deixar a IA pequena solta dando dica ao aluno.",
                font_name="Inter", size_pt=9.2, bold=False, color=CINZA)

    cards = [
        (
            0.60, CARD, AZUL,
            "1 · A regra não era o problema",
            "48/48 limpo → 49% real",
            "No piloto com equações limpas, a regra sem IA acertou 48 de 48 (100%).\n\n"
            "No Ciclo 1 ela zerou só porque o TrOCR lia lixo. Assim que trocamos o leitor no Ciclo 2, ela voltou a acertar — e venceu Qwen 1.5B e Gemma 2B.\n\n"
            "Quando não tem certeza, chama o professor. Nunca inventa.",
        ),
        (
            3.62, FUNDO_AMBAR, AMBAR,
            "2 · A ilusão dos 46,5%",
            "Chute disfarçado de acerto",
            "A acurácia sozinha quase me enganou: o Qwen2.5-VL 3B fez 46,5%, mas chamou 234 de 241 folhas (97%) de \"erro de cálculo\".\n\n"
            "Os modelos pequenos travam em 1 ou 2 classes: o Gemma2 2B em português jogou 134 de 241 em \"raciocínio\".\n\n"
            "Para montar o Atlas da turma, isso distorce todo o mapa de erros.",
        ),
        (
            6.64, FUNDO_VERM, VERM,
            "3 · Quando a dica atrapalha",
            "Resposta + regra falsa",
            "Mesmo proibida pelo prompt, a IA pequena escorregou em casos reais:\n\n"
            "• Vazou tudo (Qwen 1.5B, caso 100): \"...9x - 27 = 10x - 30 ... então x = 3\".\n\n"
            "• Inventou regra errada (caso 0): \"os números em matemática são sempre positivos ou zero\".\n\n"
            "Em sala de aula, isso confunde quem já está travado.",
        ),
    ]

    for x, bg_c, acc_c, titulo, kpi, corpo in cards:
        add_rect(s, x, 1.24, 2.82, 3.84, bg_c)
        add_rect(s, x, 1.24, 2.82, 0.07, acc_c)
        add_textbox(s, x + 0.14, 1.40, 2.54, 0.24, titulo, font_name="Inter", size_pt=9.2, bold=True, color=acc_c)
        add_textbox(s, x + 0.14, 1.66, 2.54, 0.42, kpi, font_name="Merriweather", size_pt=10.8, bold=True, color=NAVY)
        add_textbox(s, x + 0.14, 2.12, 2.54, 2.88, corpo, font_name="Inter", size_pt=8.4, bold=False, color=NAVY, line_spacing=1.18)

    set_notes(s, (
        "[~75 s] Mais importante que a tabela é abrir os logs e ler o que a IA realmente escreveu. "
        "Primeiro: a regra sem IA não era o gargalo. Com texto limpo ela acertou 48 de 48; quando trocamos o leitor, ela voltou a funcionar e bateu as IAs pequenas sem nunca chutar. "
        "Segundo: acurácia sozinha engana. O Qwen2.5-VL 3B fez 46,5% só porque respondeu 'erro de cálculo' em 97% das folhas; e o Gemma2 2B em português jogou mais da metade em 'raciocínio'. "
        "Se eu somasse isso no Atlas do professor, o mapa da turma sairia todo torto. "
        "Terceiro: na dica para o aluno, o Qwen 1.5B entregou a conta resolvida inteira no caso 100 e, no caso zero, chegou a dizer que números em matemática são sempre positivos ou zero. "
        "Para um aluno de sétimo ano, uma dica errada com cara de certa é pior do que não ter dica."
    ))
    return s


def preencher_slide9_onde_fica_ia(s):
    """Slide 9: Como o Atlas sai desse teste — onde fica a IA + caminho até o pitch."""
    limpar_slide(s)
    add_textbox(s, 0.60, 0.42, 8.8, 0.40, "Como o Atlas sai desse teste: onde fica a IA",
                font_name="Merriweather", size_pt=19.5, bold=True, color=NAVY)
    add_textbox(s, 0.60, 0.84, 8.8, 0.26,
                "A segunda IA sai do Passo 3 — mas o Atlas continua tendo IA onde ela realmente fez diferença.",
                font_name="Inter", size_pt=9.2, bold=False, color=CINZA)

    headers = ["Etapa da pipeline", "Fica com IA?", "Decisão após os 2 ciclos nas 241 folhas"]
    col_ws = [2.10, 1.20, 5.50]
    rows = [
        ("1 · Ler o caderno", "Sim (IA)", "Sai TrOCR-printed (0%) → entra Pix2Text (43,9%, só CPU) ou Qwen2.5-VL 3B (49,1%). Foi onde a IA provou valor real.", FUNDO_VERDE, VERDE),
        ("2 · Achar a quebra", "Não", "SymPy (álgebra simbólica). Mesma entrada, mesma resposta. Só erra se a leitura chegou errada.", CARD, CINZA),
        ("3 · Nomear o erro", "Não", "Regra das correções típicas. Venceu Qwen 1.5B e Gemma2 2B no escopo real; quando não sabe, chama o professor.", BRANCO, CINZA),
        ("4 · Dar a pista", "Não", "Frases revisadas pelo professor por tipo de erro. Garante zero vazamento de resposta e zero regra matemática falsa.", CARD, CINZA),
    ]

    sh_t = s.shapes.add_table(len(rows) + 1, 3, Inches(0.60), Inches(1.22), Inches(sum(col_ws)), Inches(2.58))
    t = sh_t.table
    for ci, w in enumerate(col_ws):
        t.columns[ci].width = Inches(w)
    for ci, h in enumerate(headers):
        style_cell(t.cell(0, ci), h, size_pt=8.8, bold=True, color=BRANCO, fill_cor=NAVY)
    for ri, (c0, c1, c2, bg, cor_c1) in enumerate(rows, 1):
        style_cell(t.cell(ri, 0), c0, size_pt=8.6, bold=True, color=NAVY, fill_cor=bg)
        style_cell(t.cell(ri, 1), c1, size_pt=8.6, bold=True, color=cor_c1, fill_cor=bg, align=PP_ALIGN.CENTER)
        style_cell(t.cell(ri, 2), c2, size_pt=8.4, bold=False, color=NAVY, fill_cor=bg)

    add_rect(s, 0.60, 4.00, 8.80, 1.08, CARD)
    add_textbox(s, 0.78, 4.08, 8.40, 0.22, "Caminho até o pitch de 02/12",
                font_name="Inter", size_pt=9.0, bold=True, color=AZUL)

    marcos = [
        ("18/11", "régua + ScratchMath · feito", VERDE),
        ("24/11", "Ciclos 1 e 2 (241 folhas) · feito", VERDE),
        ("27/11", "revisão qualitativa e ensaio", AZUL),
        ("02/12", "pitch com os resultados reais", NAVY),
    ]
    for i, (data, desc, cor) in enumerate(marcos):
        x = 0.78 + i * 2.15
        add_textbox(s, x, 4.34, 2.05, 0.26, data, font_name="Merriweather", size_pt=12.0, bold=True, color=cor)
        add_textbox(s, x, 4.62, 2.05, 0.40, desc, font_name="Inter", size_pt=8.2, bold=False, color=CINZA)

    set_notes(s, (
        "[~60 s] Muita gente pergunta: se a LLM saiu do Passo 3, o Atlas deixa de ser um projeto de IA? Não. "
        "Ele fica mais honesto e mais útil. A IA fica exatamente onde código comum não resolve e onde os dados mostraram ganho enorme: "
        "no Passo 1, ler a letra do aluno, saindo de 0% para quase 50% — inclusive com opção rodando só na CPU, como o Pix2Text. "
        "Os passos 2, 3 e 4 ficam sem IA: o SymPy encontra a quebra, a regra nomeia o erro — e quando não sabe chama o professor —, "
        "e a pista vem de uma lista revisada, sem risco de vazar resposta nem inventar regra errada. "
        "Os dois ciclos já estão concluídos; até o dia 27 fecho o ensaio para o pitch de 2 de dezembro."
    ))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--entrada", type=Path, required=True)
    parser.add_argument("--saida", type=Path, required=True)
    args = parser.parse_args()

    m1 = json.loads(M1_PATH.read_text(encoding="utf-8"))
    prs = Presentation(str(args.entrada))

    # Slides originais (indices 0..6):
    #   0: Slide 1 (pipeline) -> mantém intacto
    #   1: Slide 2 (ScratchMath) -> mantém visual, atualiza notas
    #   2: Slide 3 (o que eu quero mostrar) -> mantém visual, atualiza notas
    #   3: Slide 4 -> reescrito in-place: Metodologia em dois ciclos
    #   4: Slide 5 -> reescrito in-place: Ciclo 1 (241 folhas)
    #   5: Slide 6 (fecho escuro #1E2B4A) -> atualizado in-place, vai para o final (Slide 10)
    #   6: Slide 7 -> reescrito in-place: Onde fica a IA (Slide 9)
    # Novos slides adicionados (indices 7..9):
    #   7: Slide 6 (Ciclo 2 · Passo 1: OCR)
    #   8: Slide 7 (Ciclo 2 · Passo 3: quem ganhou?)
    #   9: Slide 8 (Por dentro dos números: exemplos reais)

    set_notes(prs.slides[1], (
        "[~70 s] Para testar o Atlas em cima de algo concreto, eu usei o benchmark ScratchMath, publicado na AIED 2026. "
        "São 1.720 rascunhos feitos à mão por alunos de verdade na China; 241 deles são do 7º ao 9º ano. "
        "Cinco professores anotaram cada folha com um de sete tipos de erro e escreveram a explicação. "
        "O detalhe mais importante da tabela está ali embaixo: 47% das folhas são 'erro de cálculo'. "
        "Ou seja, chutar sempre essa categoria já acerta 46,9%, quase o mesmo que o o4-mini, o melhor modelo do artigo. "
        "Por isso, para saber se a IA está acertando de verdade, não basta olhar acurácia — tem que olhar também o F1 e se ela sabe explicar o erro."
    ))
    set_notes(prs.slides[2], (
        "[~60 s] Antes de rodar qualquer modelo nas 241 folhas, eu escrevi a régua para não mudar o critério depois de ver o número. "
        "Para passar, a IA tinha que classificar melhor que a regra sem IA e acima do chute de 46,9%, além da margem de erro de uns 6 pontos, "
        "e sem entregar a resposta pronta em nenhuma dica. Se empatasse ou perdesse, a hipótese cairia e a IA sairia do Passo 3. "
        "Foi com essa régua travada que eu fui para o teste."
    ))

    preencher_slide4_metodologia(prs.slides[3])
    preencher_slide5_ciclo1(prs.slides[4], m1)

    # Atualiza o Fecho escuro (idx 5) in-place
    s_fecho = prs.slides[5]
    set_shape_text(s_fecho.shapes[1], "O que as 241 folhas reais responderam",
                   font_name="Inter", size_pt=9.5, bold=True, color=AZUL_CLARO)
    set_shape_text(s_fecho.shapes[2],
                   "A IA pequena perdeu para a regra no diagnóstico. Mas a IA certa na leitura tirou o Atlas de 0% para quase metade dos cadernos reais.",
                   font_name="Merriweather", size_pt=15.8, bold=True, color=TEXTO_ESCURO_BG)
    set_shape_text(s_fecho.shapes[3],
                   "Testado com gabarito de professores (241 folhas + 57 equações do 1º grau), sem inventar dados.",
                   font_name="Inter", size_pt=9.5, bold=False, color=SUB_ESCURO_BG)
    set_shape_text(s_fecho.shapes[5], "A decisão para o Atlas a partir daqui",
                   font_name="Inter", size_pt=9.5, bold=True, color=ROSA_CLARO)
    set_shape_text(s_fecho.shapes[6],
                   "A IA sai do Passo 3 e vai inteira para o Passo 1: ler a letra do aluno com segurança, para o SymPy e a regra fazerem o resto.",
                   font_name="Merriweather", size_pt=15.3, bold=True, color=TEXTO_ESCURO_BG)
    set_shape_text(s_fecho.shapes[7],
                   "Descobrir onde a IA falha antes de ir para a escola também protege o aluno.",
                   font_name="Inter", size_pt=10.5, bold=False, color=TEXTO_ESCURO_BG)
    set_notes(s_fecho, (
        "[~45 s] Então, fechando a história toda: testar nas 241 folhas reais do ScratchMath mudou o rumo do projeto para melhor. "
        "Ficou provado que modelos pequenos de 1,5B ou 2B perdem para uma regra simples na hora de diagnosticar — e ainda correm risco "
        "de vazar resposta ou inventar matemática errada. Mas também ficou provado que trocar o leitor do Passo 1 resolve o maior gargalo, "
        "levando o Atlas de zero para quase metade das equações reais. "
        "Por isso, a IA sai do Passo 3 e concentra toda a força no Passo 1. Obrigada."
    ))

    preencher_slide9_onde_fica_ia(prs.slides[6])

    # Adiciona 3 slides novos (indices 7, 8, 9 -> slide8.xml, slide9.xml, slide10.xml)
    build_slide6_ocr_virada(prs)
    build_slide7_ciclo2_passo3(prs)
    build_slide8_exemplos(prs)

    # Reordena para sequência narrativa 1..10:
    # [S1=0, S2=1, S3=2, S4=3, S5=4, S6=7, S7=8, S8=9, S9=6, S10=5]
    reordenar_slides(prs, [0, 1, 2, 3, 4, 7, 8, 9, 6, 5])

    total = len(prs.slides)
    for i, sl in enumerate(prs.slides, 1):
        add_rodape(sl, i, total, escuro=(i == total))

    prs.save(str(args.saida))
    print(f"Apresentação narrativa salva com sucesso em: {args.saida} ({total} slides)")


if __name__ == "__main__":
    main()
