# tec · tecnologia base demonstrável — Atlas do Erro

> folha do artefato [tecnologia base demonstrável](https://lucassf.pages.dev/ai4good/artefatos/3-tecnologia-base), preenchida a partir do [brw (`brw_andreza.md`)](../brw_andreza.md) e do [cmp (`va2/cmp.md`)](cmp.md).

## 0 · a minha ideia e a técnica do brw

- **ideia completa (do `cmp.md` § 0):** **Atlas do Erro · diagnóstico formativo de álgebra manuscrita e mapa coletivo de lacunas para a turma.** alunos do ensino fundamental II e médio resolvem problemas de matemática à mão no caderno e fotografam os passos; um modelo de visão computacional (OCR matemático) transcreve linha a linha a resolução manuscrita e um verificador simbólico (`SymPy`) confere a equivalência algébrica entre linhas consecutivas para encontrar exatamente a primeira passagem onde o erro ocorreu. um modelo de linguagem pequeno rodando localmente classifica o tipo conceitual do erro (inversão de sinal na transposição, distributiva incompleta, soma indevida de denominadores, erro aritmético) e devolve ao aluno uma dica curta e localizada sobre o passo incorreto, sem entregar a resposta final. antes da aula seguinte, o caderno do professor agrega anonimamente as categorias de erro de toda a turma em um mapa de calor coletivo ("Atlas"), indicando quais conceitos precisam ser retomados no quadro.
- **técnica nomeada no `brw.md` § 6b:** pipeline híbrido neuro-simbólico local combinando **Transformer de visão para OCR linha a linha (`TrOCR`)** + **álgebra computacional determinística (`SymPy`)** + **modelo de linguagem pequeno local (`Qwen2.5-1.5B` via Ollama)** para diagnóstico pedagógico do erro sem revelar o gabarito.

## 1 · técnica escolhida

| papel | técnica / modelo | repositório oficial | licença | por que esta e não outra |
|:--|:--|:--|:--|:--|
| **central** | `TrOCR` (`microsoft/trocr-small-printed`, 62M parâmetros, encoder DeiT-small + decoder MiniLM) via `transformers` | [microsoft/unilm/tree/master/trocr](https://github.com/microsoft/unilm/tree/master/trocr) · pesos em [huggingface.co/microsoft/trocr-small-printed](https://huggingface.co/microsoft/trocr-small-printed) | MIT | 246 MB em disco; roda em CPU no MacBook sem exigir GPU dedicada; ao contrário do checkpoint `trocr-small-handwritten` (treinado no corpus literário IAM, onde sinais de `+` e `=` quase não existem e são convertidos em hífens `-`), o `trocr-small-printed` foi ajustado no dataset SROIE (recibos com dígitos e operadores) e reconhece números, `x`, `+`, `-` e `=` em caligrafia escolar legível. mais leve que `Nougat-small` (350M, ~1,4 GB, focado em PDFs científicos inteiros) e sem o conflito de dependências antigas (`pydantic v1`) do `pix2tex`. |
| apoio | `SymPy` (`sympy.solveset` + `parse_expr` com multiplicação implícita) | [sympy/sympy](https://github.com/sympy/sympy) | BSD-3-Clause | biblioteca determinística de álgebra simbólica em Python puro (~25 MB); transforma cada linha `A = B` em conjunto-solução exato e detecta em $< 5\text{ ms}$ em qual linha a equivalência quebrou, evitando que o modelo de linguagem alucine aritmética (limitação documentada no benchmark MathClean). |
| apoio | `Qwen2.5-1.5B-Instruct` (`qwen2.5:1.5b` em GGUF Q4_K_M) servido pelo `Ollama` | [QwenLM/Qwen2.5](https://github.com/QwenLM/Qwen2.5) · runtime [ollama/ollama](https://github.com/ollama/ollama) | Apache-2.0 (Qwen2.5-1.5B) / MIT (Ollama) | 986 MB quantizado em 4 bits; gera JSON estruturado em português localmente (~1,2 s por caderno) sem enviar fotos de alunos para APIs pagas em nuvem; supera o `qwen2.5:0.5b` na formulação de dicas pedagógicas em português e exige um terço da RAM de modelos 7B (~4,5 GB). |

## 2 · passo 2 — exemplo oficial rodando

- **repositório:** [https://github.com/andrezacfalcao/project-ai4good](https://github.com/andrezacfalcao/project-ai4good) (pasta [`va2/tec/`](https://github.com/andrezacfalcao/project-ai4good/tree/main/va2/tec))
- **commit 1 (exemplo oficial):** [`76b9dba`](https://github.com/andrezacfalcao/project-ai4good/commit/76b9dba) — `tec: exemplo oficial do TrOCR-small-printed rodando em CPU`
- **máquina:** Apple M3, 16 GB RAM, sem uso de GPU dedicada (execução em CPU via PyTorch 2.14.0), macOS, Python 3.14.3
- **espaço em disco (pesos + ambiente):** 246 MB (`~/.cache/huggingface/hub/models--microsoft--trocr-small-printed`) + 986 MB (`qwen2.5:1.5b` no Ollama)
- **memória RAM no pico:** 681 MB RSS (`433 MB` de *peak memory footprint* medido com `/usr/bin/time -lp`)
- **tempo do comando:** 6,09 s (incluindo carga dos 360 tensores do modelo em CPU)

**comando:**

```bash
.venv/bin/python va2/tec/ler_caderno.py
```

**saída no terminal (copiada sem edição):**

```text
Loading weights: 100%|█████████████████████| 360/360 [00:00<00:00, 7335.12it/s]
UNPLUS THE
```

*(nota: o exemplo oficial do `README` de `microsoft/trocr-small-printed` carrega a imagem `a01-122-02-00.jpg` do banco cursivo IAM — o próprio código oficial da Microsoft inclui o comentário `# load image from the IAM database (actually this model is meant to be used on printed text)`, razão pela qual a palavra cursiva `"industry"` é lida como `"UNPLUS THE"` no teste padrão do README).*

## 3 · passo 3 — alteração mínima com a minha entrada e a minha saída

- **commit 2 (alteração mínima):** [`26f14db`](https://github.com/andrezacfalcao/project-ai4good/commit/26f14db) — `tec: entrada e saida do Atlas do Erro com SymPy e Qwen local`
- **o que mudou na entrada:** no lugar do recorte único `a01-122-02-00.jpg` do dataset IAM, entram três imagens simulando fotos de resoluções manuscritas de equações do 1º grau em 3 linhas (`va2/tec/cadernos/caderno-1.png`, `caderno-2.png` e `caderno-3.png`), fatiadas automaticamente em 3 faixas horizontais (`h // 3`):
  - `caderno-1.png` (folha sem pauta, letra escolar legível): `2x + 4 = 10` $\to$ `2x = 10 + 4` $\to$ `x = 7` (aluno esqueceu de inverter o sinal do `+4` ao transpor para o lado direito).
  - `caderno-2.png` (folha sem pauta, letra escolar legível): `3x - 6 = 9` $\to$ `3x = 9 - 6` $\to$ `x = 1` (aluno manteve `-6` em vez de somar `+6`).
  - `caderno-3.png` (folha com pauta azul de caderno cortando a base do texto e letra cursiva inclinada): `4x + 8 = 20` $\to$ `4x = 20 + 8` $\to$ `x = 7`.
- **o que mudou na saída:** depois do `processor.batch_decode` do `TrOCR`, o script avalia o conjunto-solução de cada linha com `sympy.solveset` (identificando em qual linha a equivalência quebrou ou se faltou `=` por erro de OCR) e passa a transição quebrada ao `qwen2.5:1.5b` local (via API HTTP do Ollama em `localhost:11434`, `temperature: 0`, `format: "json"`), imprimindo um JSON com `categoria_erro` (para o Atlas da turma) e `dica_aluno` (sem revelar o valor final de $x$).

**código alterado (`va2/tec/ler_caderno.py`):**

```python
import json, sys, urllib.request
from PIL import Image
from sympy import Eq, Symbol, solveset
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

TR = standard_transformations + (implicit_multiplication_application,)
PROMPT = (
    'Responda APENAS JSON: {"categoria_erro": str, "dica_aluno": str}. '
    'O aluno errou na passagem indicada pelo SymPy (ex: passou termo para o outro lado sem inverter o sinal). '
    'Nomeie o tipo de erro para o Atlas da turma e explique ao aluno o que revisar nessa linha, SEM dar o valor de x.\n'
)

processor = TrOCRProcessor.from_pretrained("microsoft/trocr-small-printed")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-small-printed")


def raizes(linha):
    if "=" not in linha:
        return None
    esq, dir_ = linha.lower().split("=", 1)
    return solveset(Eq(parse_expr(esq, transformations=TR), parse_expr(dir_, transformations=TR)), Symbol("x"))


for caminho in sys.argv[1:]:
    image = Image.open(caminho).convert("RGB")
    w, h = image.size
    faixas = [image.crop((0, i * (h // 3), w, (i + 1) * (h // 3))) for i in range(3)]
    pixel_values = processor(images=faixas, return_tensors="pt").pixel_values
    generated_ids = model.generate(pixel_values, max_new_tokens=20)
    linhas = processor.batch_decode(generated_ids, skip_special_tokens=True)

    sols = [raizes(l) for l in linhas]
    diagnostico = "equivalencia mantida"
    for i in range(len(linhas)):
        if sols[i] is None:
            diagnostico = f"falha de OCR na linha {i+1} ('{linhas[i]}' sem '=')"
            break
        if i > 0 and sols[i] != sols[i - 1]:
            diagnostico = f"quebra na linha {i+1}: '{linhas[i-1]}' -> '{linhas[i]}'"
            break

    req = urllib.request.Request(
        "http://localhost:11434/api/generate",
        data=json.dumps({
            "model": "qwen2.5:1.5b", "format": "json", "stream": False,
            "options": {"temperature": 0},
            "prompt": PROMPT + f"Passos lidos: {linhas} | SymPy: {diagnostico}",
        }).encode(),
        headers={"Content-Type": "application/json"},
    )
    dica = json.loads(urllib.request.urlopen(req).read())["response"]
    print(f"[{caminho}]\n  trocr : {linhas}\n  sympy : {diagnostico}\n  qwen  : {dica}")
```

**comando:**

```bash
.venv/bin/python va2/tec/ler_caderno.py va2/tec/cadernos/caderno-*.png
```

**saída no terminal (copiada sem edição):**

```text
[va2/tec/cadernos/caderno-1.png]
  trocr : ['2X + 4 =10', '2X = 10 + 4', 'X=7']
  sympy : quebra na linha 2: '2X + 4 =10' -> '2X = 10 + 4'
  qwen  : {
    "categoria_erro": "Equação do primeiro grau",
    "dica_aluno": "Revisar a passagem de equações para resolver o problema. A linha correta seria: '2X + 4 = 10' -> '2X = 10 - 4'."
}
[va2/tec/cadernos/caderno-2.png]
  trocr : ['3X-6=9', '3X= 9 - 6', 'X=1']
  sympy : quebra na linha 2: '3X-6=9' -> '3X= 9 - 6'
  qwen  : {
    "categoria_erro": "Operação Inválida",
    "dica_aluno": "Revisar a operação de subtração para garantir que o sinal seja invertido corretamente."
}
[va2/tec/cadernos/caderno-3.png]
  trocr : ['4X+8-20', '4X=20+8', '* * *']
  sympy : falha de OCR na linha 1 ('4X+8-20' sem '=')
  qwen  : {
    "categoria_erro": "OCR falha",
    "dica_aluno": "Revisar a passagem para corrigir o termo '4X' que foi omitido. A linha deve ser lida como '4x + 8 - 20 = 0'."
}
```

*(tempo total para os 3 cadernos: `10,72 s`; pico de memória RAM do processo Python: `731 MB` RSS / `489 MB` footprint + ~1,1 GB do servidor Ollama).*

**onde a saída erra:**

- **no `caderno-3.png` (pauta azul + letra cursiva inclinada):** a linha horizontal azul da pauta do caderno encosta na barra inferior do sinal `=`. O `TrOCR` confunde `=` com `-` na linha 1 (`4x + 8 = 20` vira `'4X+8-20'`) e lê `x = 7` na linha 3 como `'* * *'`. Sem o sinal `=`, o `SymPy` rejeita a linha 1 (`falha de OCR na linha 1 ('4X+8-20' sem '=')`).
- **no `caderno-3.png` (`qwen2.5:1.5b` chamado mesmo após falha de OCR):** em vez de apenas pedir ao aluno uma foto mais nítida sem pauta cortando os sinais, o `qwen2.5:1.5b` alucina uma explicação algébrica sobre o erro de OCR (`"corrigir o termo '4X' que foi omitido. A linha deve ser lida como '4x + 8 - 20 = 0'"`).
- **no `caderno-1.png` (vazamento do passo corrigido e categoria genérica):** embora o `qwen2.5:1.5b` tenha respeitado a restrição de não revelar o valor final (`x = 3`), ele entregou a linha 2 já reescrita (`'2X = 10 - 4'`) em vez de fazer apenas uma pergunta orientadora como fez no `caderno-2.png`, e preencheu `categoria_erro` como `"Equação do primeiro grau"` (assunto da questão) em vez de uma categoria fechada de erro (`"inversao_sinal_transposicao"`).

## 4 · passo 4 — vídeo da demonstração

- **link do vídeo:** *(grave um vídeo de 20 a 30 s da sua tela rodando os três comandos abaixo no terminal e cole aqui o link não listado do YouTube ou Google Drive com permissão de visualização)*

**roteiro exato de 25 segundos para gravar no terminal:**

```bash
git log --oneline -n 2
.venv/bin/python va2/tec/ler_caderno.py va2/tec/cadernos/caderno-*.png
```

## 5 · passo 5 — o que deu certo e o que errou

1. **o que a técnica acertou na sua entrada?**
   Nos cadernos 1 e 2 (fundo limpo e letra escolar legível), o `microsoft/trocr-small-printed` leu corretamente todas as 6 linhas com incógnitas e sinais (`+`, `-`, `=`). O `SymPy` converteu as strings com multiplicação implícita (`2X` $\to$ `2*x`) em equações simbólicas e cravou com precisão determinística que a equivalência quebrou na passagem da linha 1 para a linha 2 em ambos os casos (raiz mudou de $\{3\}$ para $\{7\}$ no caderno 1 e de $\{5\}$ para $\{1\}$ no caderno 2). No caderno 2, o `qwen2.5:1.5b` formulou uma dica curta e correta sobre a inversão de sinal na subtração sem entregar o resultado final.
2. **onde ela errou, e por quê?**
   O `TrOCR` falhou no `caderno-3.png` porque o traço horizontal da pauta azul do caderno se fundiu visualmente à barra inferior do sinal `=`, fazendo o encoder visual DeiT interpretar as duas barras paralelas do `=` como um único traço `-` (`4X+8-20`) e perder completamente a linha 3 (`* * *`). Já o `qwen2.5:1.5b` errou em dois pontos por ser um modelo pequeno (1,5B) com prompt aberto: (a) quando recebeu um erro de OCR no caderno 3, tentou inventar uma correção matemática para uma linha mal lida; e (b) sem um `enum` fechado no schema JSON, rotulou o erro do caderno 1 com o nome do conteúdo (`"Equação do primeiro grau"`) e mostrou a linha 2 já corrigida (`2X = 10 - 4`).
3. **o que isso muda no desenho da sua solução (vai para o fluxograma)?**
   Três mudanças diretas entram na arquitetura do Atlas do Erro:
   - **pré-processamento de imagem antes do OCR:** aplicar remoção de pauta horizontal (filtro morfológico / limiarização adaptativa em OpenCV) antes de enviar as faixas para o `TrOCR`;
   - **curto-circuito determinístico no `SymPy`:** se o `SymPy` detectar `falha de OCR` (ausência de `=` ou erro de sintaxe), o sistema **não chama o LLM** e devolve diretamente um aviso de interface pedindo ao aluno que confirme ou edite a linha mal lida;
   - **schema JSON com taxonomia fechada (`enum`):** restringir o campo `categoria_erro` no JSON Schema do Ollama a uma lista fixa (`["inversao_sinal_transposicao", "distributiva_incompleta", "soma_indevida_denominadores", "erro_aritmetico"]`) para que a agregação do Atlas do professor seja exata por regra.

## 6 · passo 6 — auditoria cega (em outra conversa)

> [!IMPORTANT]
> **Instrução da disciplina (regra 6 do guia):** a auditoria cega deve ser rodada em uma **conversa nova** (sem histórico desta sessão) colando as seções 0 a 5 acima junto com o prompt do Passo 6 do guia (`https://lucassf.pages.dev/ai4good/artefatos/3-tecnologia-base#passo-6--auditoria-cega-em-outra-conversa`), e a **sua resposta** aos itens apontados deve ser escrita por você mesma, com suas próprias palavras.

**crítica da IA (colada sem edição da conversa nova):**

| # | trecho ou passo | problema (reprodutibilidade, alteração mínima, falha escondida, métrica ausente, licença) | como consertar |
|:-:|:--|:--|:--|
| 1 | *(cole aqui a linha 1 da auditoria cega gerada em conversa nova)* | | |
| 2 | *(cole aqui a linha 2 da auditoria cega gerada em conversa nova)* | | |

**minha resposta (escrita por mim, item a item):**

- **item 1:** *(escreva aqui com suas próprias palavras o que você ajustou ou por que manteve a decisão)*
- **item 2:** *(escreva aqui com suas próprias palavras o que você ajustou ou por que manteve a decisão)*
