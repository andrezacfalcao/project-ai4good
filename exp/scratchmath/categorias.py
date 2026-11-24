"""Taxonomia oficial das 7 categorias do ScratchMath (Song et al., AIED 2026)
e mapeamento determinístico da regra do Atlas.
"""

CATEGORIAS_SCRATCHMATH = [
    {
        "id": 0,
        "codigo": "erro_calculo",
        "zh": "计算错误",
        "en": "Calculation Error",
        "pt": "Erro de cálculo",
        "descricao": "Errou operação aritmética ou manipulação numérica/algébrica básica (soma, subtração, multiplicação, divisão, sinal em conta).",
    },
    {
        "id": 1,
        "codigo": "erro_compreensao",
        "zh": "题目理解错误",
        "en": "Comprehension Error",
        "pt": "Erro de compreensão do enunciado",
        "descricao": "Interpretou mal o texto do problema, as condições dadas ou o que a questão pede.",
    },
    {
        "id": 2,
        "codigo": "lacuna_conhecimento",
        "zh": "知识点错误",
        "en": "Knowledge Gap Error",
        "pt": "Lacuna de conhecimento ou conceito",
        "descricao": "Desconhece ou aplicou incorretamente uma regra matemática, propriedade, fórmula ou conceito (ex.: distributiva, regra de sinais, propriedade de frações/equações).",
    },
    {
        "id": 3,
        "codigo": "erro_estrategia",
        "zh": "答题技巧错误",
        "en": "Strategy Error",
        "pt": "Erro de estratégia ou método",
        "descricao": "Escolheu uma abordagem, método ou plano de resolução inadequado ou incompleto para o problema.",
    },
    {
        "id": 4,
        "codigo": "erro_transcricao",
        "zh": "手写誊抄错误",
        "en": "Transcription Error",
        "pt": "Erro de transcrição ou cópia manuscrita",
        "descricao": "Copiou errado um número, símbolo ou expressão do enunciado ou de uma linha para a outra, ou transferiu errado do rascunho para a resposta final.",
    },
    {
        "id": 5,
        "codigo": "erro_raciocinio",
        "zh": "逻辑推理错误",
        "en": "Reasoning Error",
        "pt": "Erro de raciocínio lógico",
        "descricao": "Cometeu falha de dedução lógica ou salto inválido entre premissas e conclusões.",
    },
    {
        "id": 6,
        "codigo": "erro_atencao",
        "zh": "注意力与细节错误",
        "en": "Attention Error",
        "pt": "Erro de atenção e detalhes",
        "descricao": "Descuido pontual: esqueceu um sinal negativo, omitiu um termo, ignorou unidade/restrição ou cometeu lapso de atenção.",
    },
]

CODIGOS_VALIDOS = [c["codigo"] for c in CATEGORIAS_SCRATCHMATH]
POR_ID = {c["id"]: c for c in CATEGORIAS_SCRATCHMATH}
POR_CODIGO = {c["codigo"]: c for c in CATEGORIAS_SCRATCHMATH}
POR_ZH = {c["zh"]: c for c in CATEGORIAS_SCRATCHMATH}

# Mapeamento pré-definido da regra determinística do Atlas (4 tipos + outro)
# para a taxonomia de 7 classes do ScratchMath:
# - conta -> erro_calculo (Calculation Error)
# - troca_sinal, distributiva, divisao -> lacuna_conhecimento (Knowledge Gap Error),
#   que é a categoria do ScratchMath que engloba aplicação incorreta de regras/procedimentos algébricos.
# - outro / ilegivel / sem_quebra -> None (sem resposta -> conta como erro na métrica ECC).
MAPA_REGRA_PARA_SCRATCHMATH = {
    "conta": "erro_calculo",
    "troca_sinal": "lacuna_conhecimento",
    "distributiva": "lacuna_conhecimento",
    "divisao": "lacuna_conhecimento",
    "outro": None,
}
