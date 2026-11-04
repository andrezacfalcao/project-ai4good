# Execução no Linux · 04/11/2026

Segunda máquina, separada da execução do Mac registrada em `../`. O código é o do
commit `abf1638`, sem alteração. O ambiente foi criado do zero com uv; o registro
completo está em [ambiente.json](ambiente.json).

- **Máquina:** WSL2 (Linux 6.6), Intel i5-13450HX, 16 GB de RAM, RTX 4050 Laptop 6 GB.
- **Python:** 3.14.6 em `tec/.venv`. O TrOCR roda em CPU, porque o script não move o modelo.
- **Ollama:** 0.32.1, `qwen2.5:1.5b` com o mesmo digest do Mac
  (`65ec0654…`), carregado inteiro na GPU.

Comandos, a partir da raiz do repositório:

```bash
HF_HUB_OFFLINE=1 /usr/bin/time -p ./tec/rodar.sh oficial
HF_HUB_OFFLINE=1 /usr/bin/time -p ./tec/rodar.sh adaptado   # executado duas vezes seguidas
```

| Arquivo | O que mostra |
| --- | --- |
| [oficial.stdout.txt](oficial.stdout.txt) | `UNPLUS THE`, idêntico à saída do Mac. |
| [adaptado-1.stdout.txt](adaptado-1.stdout.txt) | Primeira execução; 42,61 s, incluindo a carga do Qwen na GPU. |
| [adaptado-2.stdout.txt](adaptado-2.stdout.txt) | Execução seguinte, com o modelo já carregado; 7,72 s. |
| `*.stderr.txt` | Avisos completos e tempos medidos por `/usr/bin/time`. |

## O que se repetiu e o que mudou

- **TrOCR e SymPy:** as nove linhas lidas e os três diagnósticos são iguais aos
  do Mac nas duas execuções, inclusive a falha de leitura no caderno 3.
- **Qwen:** as categorias e as dicas diferem das do Mac e também variaram entre
  as duas execuções nesta máquina, apesar de `temperature: 0`. Veja o teste de
  variação abaixo.
- Na primeira execução, o caderno 1 voltou a receber o passo corrigido
  (`'2X = 10 - 4'`). Na segunda, a dica do caderno 2 termina com
  "Isso resulta em $x=1$": dá um valor de x, que o prompt proíbe, e o valor está errado.
- No caderno 3, o Qwen atribuiu uma categoria algébrica a uma falha de leitura.

## Teste de variação do Qwen

Duas saídas se alternaram, cada uma idêntica a uma das execuções acima:
**A**, de `adaptado-1`, e **B**, de `adaptado-2`. Os cadernos 1 e 2 mudam; o 3 não.

| Ensaio, sem mudar o código versionado | Resultado |
| --- | --- |
| Descarregar o modelo do Ollama e rodar duas vezes, repetido em dois ciclos | A na primeira execução e B na segunda, nos dois ciclos |
| Cópia temporária com `"seed": 42` nas opções: três execuções com o modelo carregado e uma depois de descarregá-lo | B nas três primeiras; A depois de descarregar. O `seed` não alterou o padrão, como esperado com `temperature: 0` |
| Cópia temporária com `"keep_alive": 0` em cada chamada, três execuções | A primeira e a segunda já diferiram entre si |

A saída depende do estado do modelo no Ollama, carregado agora ou já usado,
e não de sorteio. Nenhuma das duas opções testadas tornou a dica reproduzível,
e nenhuma foi incorporada ao código. Não foi isolado qual mecanismo interno
do runtime produz a diferença.

Em uma instalação só com o `requirements.txt` daquele commit, o tokenizador do
TrOCR não carregou por falta de `sentencepiece` e `protobuf`. As duas
dependências foram acrescentadas antes destas execuções.

Tempos de execuções únicas, não benchmark. Não foi medido pico de memória.
