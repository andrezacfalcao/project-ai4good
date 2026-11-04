# tec · tecnologia base demonstrável · Atlas do Erro

> Aluna: Andreza Maria Coutinho Falcão. Execução verificada em 03/11/2026 (Mac)
> e repetida em 04/11/2026 (Linux, [registro](resultados/linux-2026-11-04/README.md)).
> Pasta de entrega: [tec/](https://github.com/andrezacfalcao/project-ai4good/tree/main/tec).
> Esta folha registra uma demonstração executada com apoio de IA. As partes de
> autoria da aluna, o vídeo e a auditoria em outra conversa continuam pendentes.

## 0 · a minha ideia e a técnica central

**Ideia completa, transcrita de [brw_andreza.md](../brw_andreza.md), § 5:**

Atlas do Erro · estudantes resolvem os exercícios à mão e fotografam o caderno. A visão computacional lê o raciocínio linha por linha e, sem dar a resposta, aponta só onde ele quebrou. Corrigir o próprio erro recupera parte do ponto perdido, mas nunca vale mais do que acertar de primeira, então ninguém ganha errando de propósito. Como na caixa-preta da aviação, cada erro é registrado sem punição e, anônimo, forma um atlas que mostra ao professor onde a turma trava. Na crise do slop, a IA deixa de pensar pelo aluno e devolve o raciocínio para ele.

**Técnica nomeada no § 6b, transcrita do brw:**

técnica: visão computacional para reconhecimento de escrita à mão (OCR de manuscritos e de expressões matemáticas), que transcreve a resolução linha por linha para que um modelo de linguagem verifique cada passo · aula da disciplina: aula 07 · redes convolucionais (arquiteturas de deep learning 1/4), para ler a escrita à mão, e aula 11 · transformers, para o modelo que lê a transcrição e escreve a pista

**Recorte desta execução:** três resoluções sintéticas de equações de primeiro
 grau, cada uma com três linhas. Leitura com TrOCR, verificação de equivalência
 com SymPy e tentativa de geração de pista com Qwen local. O protótipo não
 implementa coleta de uma turma, atlas agregado, pontuação nem pistas progressivas.

## 1 · técnica escolhida e alternativas

As fontes abaixo foram abertas pelo assistente em 03/11/2026. A aluna ainda
precisa abrir os links e conferir pessoalmente as licenças.

| Peça | Papel | Implementação e link oficial | Licença conferida | Exemplo oficial? | Máquina / execução |
| --- | --- | --- | --- | --- | --- |
| OCR, base reaproveitada | central | [TrOCR / UniLM](https://github.com/microsoft/unilm/tree/master/trocr), checkpoint [trocr-small-printed](https://huggingface.co/microsoft/trocr-small-printed) | [Código UniLM: MIT](https://github.com/microsoft/unilm/blob/master/LICENSE). O model card do checkpoint não declara uma licença própria explicitamente. | [Sim: Python curto](https://huggingface.co/microsoft/trocr-small-printed#how-to-use) | Executado em CPU no Mac Apple M3 com 16 GiB de RAM; pesos já em cache. Repetido em CPU no Linux (i5-13450HX, 16 GB), com a mesma leitura. |
| OCR, alternativa 1 | central | [pix2tex / LaTeX-OCR](https://github.com/lukas-blecher/LaTeX-OCR) | [Código: MIT](https://github.com/lukas-blecher/LaTeX-OCR/blob/main/LICENSE); licença dos pesos não verificada separadamente | Sim: `LatexOCR()` no README | Não instalado nem medido nesta execução. Reconhece imagens de fórmulas para LaTeX; não há evidência local de desempenho em cadernos reais. |
| OCR, alternativa 2 | central | [Nougat](https://github.com/facebookresearch/nougat) | [Código: MIT](https://github.com/facebookresearch/nougat/blob/main/LICENSE); [pesos: CC-BY-NC-4.0](https://github.com/facebookresearch/nougat/blob/main/LICENSE-MODEL.md) | Sim: CLI no README | Não instalado nem medido nesta execução; é voltado a documentos acadêmicos em PDF. |
| Verificação algébrica | apoio | [SymPy](https://github.com/sympy/sympy) | [BSD-3-Clause](https://github.com/sympy/sympy/blob/master/LICENSE) | [Sim: documentação](https://docs.sympy.org/latest/modules/solvers/solveset.html) | Executado no mesmo processo Python, sem GPU. |
| Pista em linguagem natural | apoio | [Qwen2.5-1.5B-Instruct](https://github.com/QwenLM/Qwen2.5), runtime [Ollama](https://github.com/ollama/ollama) | [Qwen 1.5B: Apache-2.0](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct/blob/main/LICENSE); [Ollama: MIT](https://github.com/ollama/ollama/blob/main/LICENSE) | [Sim: API local](https://docs.ollama.com/api/generate) | Q4_K_M de 986.061.892 bytes em disco; o Ollama informou 1.111.259.872 bytes carregados, incluindo GPU unificada. Isso não é o pico de RAM do sistema. No Linux, mesmo digest, 1.166.236.712 bytes na GPU RTX 4050. |

**Decisão técnica desta reprodução:** foi mantida a base TrOCR + SymPy + Qwen que
já constava do código no commit `26f14db`. A reprodução confirma que essa base
executa; não prova que ela é superior às alternativas. O TrOCR escolhido foi
ajustado para texto impresso e não é um OCR matemático especializado.

**Justificativa da escolha, escrita pela aluna sem IA:** pendente.

**Conferência das fontes da disciplina:** em 03/11/2026, as tentativas de abrir
[tec-excelente](https://lucassf.pages.dev/ai4good/tec-excelente) e
[tec-raso](https://lucassf.pages.dev/ai4good/tec-raso) foram bloqueadas com HTTP 403.
Em 04/11/2026 as duas abriram, redirecionadas para
[excelente.md](https://lucassf.pages.dev/ai4good/artefatos/tec/excelente.md) e
[raso.md](https://lucassf.pages.dev/ai4good/artefatos/tec/raso.md), junto com o
[enunciado](https://lucassf.pages.dev/ai4good/artefatos/3-tecnologia-base.md).
A aluna ainda precisa ler as anotações do professor e comparar com esta folha.

## 2 · exemplo oficial rodando

- **Commit do exemplo:** [ae9a9b4](https://github.com/andrezacfalcao/project-ai4good/commit/ae9a9b4).
- **Arquivo preservado:** [exemplo_oficial.py](exemplo_oficial.py).
- **Origem:** seção “How to use” do model card do TrOCR-small-printed.
- **Ajustes de reprodução:** leitura da mesma imagem IAM a partir de arquivo
  local, em vez de baixá-la em cada execução, e `print` da variável resultante.
  As chamadas de processamento, geração e decodificação permanecem as do exemplo.
- **Máquina:** Apple M3, 16 GiB de RAM, macOS 26.5.2, Python 3.14.6;
  TrOCR executado em CPU. Versões completas em [ambiente.json](resultados/ambiente.json).
- **Tempo observado:** 8,21 s, incluindo inicialização do Python e carga do modelo;
  pesos já disponíveis. Um único ensaio, não média nem benchmark.
- **Pico de memória:** não medido nesta reprodução. Não reaproveitamos a medida
  de outra execução como se tivesse sido obtida agora.

Comando executado, a partir de `tec/`, usando o ambiente existente na raiz:

```bash
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 /usr/bin/time -p ../.venv/bin/python ler_caderno.py
```

Esse comando foi executado antes do segundo commit. Para repetir no estado atual:

```bash
HF_HUB_OFFLINE=1 ./tec/rodar.sh oficial
```

Saída padrão, sem edição:

```text
UNPLUS THE
```

Arquivos completos: [stdout](resultados/oficial.stdout.txt) e
[stderr, com avisos e tempo](resultados/oficial.stderr.txt).
O próprio exemplo usa uma imagem cursiva IAM com um modelo voltado a texto
impresso; o resultado é uma falha de transcrição, não uma leitura correta.
O Transformers também informa parâmetros `encoder.pooler` ausentes no checkpoint
 e avisa sobre o comprimento padrão de geração; esses avisos estão preservados.

**Repetição no Linux, 04/11/2026:** WSL2, Intel i5-13450HX, 16 GB de RAM,
Python 3.14.6 em `tec/.venv` criado com uv. A primeira instalação só com o
`requirements.txt` não carregou o tokenizador por falta de `sentencepiece` e
`protobuf`, que foram acrescentados. Depois disso, a saída foi a mesma,
`UNPLUS THE`, em 3,67 s com os pesos em cache. Arquivos em
[resultados/linux-2026-11-04/](resultados/linux-2026-11-04/README.md).

## 3 · alteração mínima de entrada e saída

- **Commit da adaptação:** [abf1638](https://github.com/andrezacfalcao/project-ai4good/commit/abf1638).
- **Código:** [ler_caderno.py](ler_caderno.py).
- **Diff:** [adaptacao.diff](resultados/adaptacao.diff).
- **Explicação dos trechos adicionados:** [ALTERACOES.md](ALTERACOES.md).
- **Entrada:** três imagens sintéticas de resoluções, reaproveitadas da versão
  anterior; [descrição e transcrições esperadas](cadernos/README.md). Não são
  fotografias coletadas de alunos. O programa recorta cada imagem em três faixas.
- **Saída:** transcrição das linhas, primeira passagem em que o conjunto-solução
  muda e JSON de categoria/pista gerado pelo Qwen. SymPy e Qwen são as peças de
  apoio adicionadas na saída; a inferência TrOCR continua reconhecível.
- **Tempo observado:** 17,28 s para as três imagens, incluindo a carga do OCR e
  chamadas ao Ollama. Não foi isolado o tempo de cada etapa nem medido em celular.

Comando executado a partir de `tec/`:

```bash
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 /usr/bin/time -p ../.venv/bin/python -u ler_caderno.py cadernos/caderno-1.png cadernos/caderno-2.png cadernos/caderno-3.png
```

Atalho para repetir a partir da raiz:

```bash
HF_HUB_OFFLINE=1 ./tec/rodar.sh adaptado
```

Saída padrão, sem edição:

```text
[cadernos/caderno-1.png]
  trocr : ['2X + 4 =10', '2X = 10 + 4', 'X=7']
  sympy : quebra na linha 2: '2X + 4 =10' -> '2X = 10 + 4'
  qwen  : {
    "categoria_erro": "Equação do primeiro grau",
    "dica_aluno": "Revisar a passagem de equações para resolver o problema. A linha correta seria: '2X + 4 = 10' -> '2X = 10 - 4'."
}
[cadernos/caderno-2.png]
  trocr : ['3X-6=9', '3X= 9 - 6', 'X=1']
  sympy : quebra na linha 2: '3X-6=9' -> '3X= 9 - 6'
  qwen  : {
    "categoria_erro": "Operação Inválida",
    "dica_aluno": "Revisar a operação de subtração para garantir que o sinal seja invertido corretamente."
}
[cadernos/caderno-3.png]
  trocr : ['4X+8-20', '4X=20+8', '* * *']
  sympy : falha de OCR na linha 1 ('4X+8-20' sem '=')
  qwen  : {
    "categoria_erro": "OCR falha",
    "dica_aluno": "Revisar a passagem para corrigir o termo '4X' que foi omitido. A linha deve ser lida como '4x + 8 - 20 = 0'."
}
```

Arquivos completos: [stdout](resultados/adaptado.stdout.txt) e
[stderr, com avisos e tempo](resultados/adaptado.stderr.txt).

**Acertos e falhas observados nesta execução:**

- Cadernos 1 e 2: as seis linhas são lidas corretamente desconsiderando espaços
  e maiúsculas/minúsculas. O SymPy localiza a primeira quebra na linha 2.
- Caderno 1: o Qwen dá uma categoria genérica e entrega o passo corrigido.
  Portanto, a exigência de apenas uma pista ainda não é garantida.
- Caderno 3: o OCR lê `=` como `-` na primeira linha e falha na terceira.
  O LLM recebe a transcrição defeituosa e inventa uma orientação algébrica.
- O corte fixo pressupõe três linhas igualmente espaçadas; ainda não trata
  uma foto real de página inteira. A causa visual específica da falha não foi
  isolada experimentalmente.
- A demonstração contém somente tentativas erradas. O prompt presume erro;
  não há validação do comportamento em uma resolução inteiramente correta.

**Repetição no Linux, 04/11/2026**, com o mesmo código, as mesmas imagens e o mesmo
digest do `qwen2.5:1.5b` no Ollama 0.32.1, com o Qwen na GPU RTX 4050:

- TrOCR e SymPy repetiram as nove leituras e os três diagnósticos acima.
- As categorias e as dicas do Qwen mudaram em relação ao Mac e variaram
  entre execuções na mesma máquina, apesar de `temperature: 0`. Duas saídas se
  alternam, conforme o modelo acabou de ser carregado ou já foi usado.
  Fixar `seed` não mudou isso. A saída do Qwen colada acima é uma amostra.
- Em uma das execuções, a dica do caderno 2 diz "Isso resulta em $x=1$": dá um
  valor de x, que o prompt proíbe, e o valor está errado (o correto é 5).
- Tempos: 7,72 s com o Qwen já carregado; 42,61 s quando a execução inclui
  carregar o Qwen na GPU. Saídas completas em
  [resultados/linux-2026-11-04/](resultados/linux-2026-11-04/README.md).

## 4 · vídeo da demonstração

**Link do vídeo:** pendente.

Gravar de **1 a 3 minutos**, mostrando os dois commits do código, os comandos
 e as saídas aparecendo. O [roteiro](VIDEO.md) está separado nesta mesma pasta.
Se a gravação for feita no Linux, as leituras do TrOCR e do SymPy coincidem com
as do § 3, mas as dicas do Qwen podem aparecer diferentes, como registrado acima.
Abrir o link em janela anônima para verificar o acesso sem login.

## 5 · o que deu certo e o que errou, sem IA

O modelo TrOCR leu certo 7 das 9 linhas das três resoluções sintéticas, e o SymPy apontou a linha 2 como a quebra nos dois cadernos que não tinham pauta. Mas no caderno com pauta o "=" virou "-", e a terceira linha teve como resultado ilegível. O Qwen recebeu essa leitura errada e inventou uma correção (alucinou), já nos outros casos chegou a entregar o passo corrigido e, numa execução, até um valor de x errado, algo proibido pelo prompt! Tudo rodou num notebook, de 8 a 17 s no Mac (M3, 16 GB, OCR em CPU) e de 4 a 8 s no Linux, com o modelo de linguagem ocupando cerca de 1 GB, o que mostra que o recorte offline é viável. Podemos tirar algumas conclusões disso: a leitura do caderno real é o gargalo e precisa ser comparada com um OCR de manuscrito ou de fórmulas em fotos reais, e a pista não pode sair livre do modelo; deve vir de regras ou de uma lista revisada pelo professor, com o SymPy decidindo onde está a quebra.

## 6 · auditoria cega, em uma conversa nova

**Pendente.** Esta conversa ajudou a preparar a demonstração e não deve dar
 o veredito da própria produção. O prompt está em [AUDITORIA.md](AUDITORIA.md).

**Tabela recebida na conversa nova, colada sem edição:**

<!-- Colar aqui a tabela integral do auditor. Não há veredito gerado nesta conversa. -->

**Resposta da aluna, sem IA, item por item:**

<!-- A própria aluna escreve aqui. A IA não deve redigir ou reformular esta resposta. -->

## Situação da entrega

- [x] Código-fonte em pasta própria, com dependências e instruções.
- [x] Exemplo oficial executado e registrado no primeiro commit.
- [x] Adaptação executada e registrada em um segundo commit separado.
- [x] Saídas reais e limitações visíveis, sem ocultar a falha do terceiro caderno.
- [ ] Aluna abre os links, confere as licenças e escreve a justificativa.
- [ ] Vídeo de 1–3 minutos publicado e acessível sem login.
- [ ] Reflexão do § 5 escrita pela aluna sem IA.
- [ ] Auditoria cega em conversa nova e resposta da aluna no § 6.
- [ ] Conferência dos exemplos excelente/raso e alinhamento final com brw/cmp.
