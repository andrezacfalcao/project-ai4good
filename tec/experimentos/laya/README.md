# Experimento LAYA · Atlas do Erro

Experimento separado, sugerido pelo link indicado pelo professor:
[NandhaKishorM/laya](https://github.com/NandhaKishorM/laya).

**Resultado em 03/11/2026:** a biblioteca executou, mas a classificação de erros
de álgebra não ficou confiável nos dez casos sintéticos. O exemplo de suporte
original atribuiu `0.9717` à solicitação explícita de reembolso; isso comprova uma
inferência real, não a capacidade de diagnosticar matemática.

| Condição | LAYA | Qwen2.5 1.5B |
| --- | --- | --- |
| Somente as linhas | 3/10 corretas; mediana 167 ms/chamada | 1/10; mediana 514 ms/chamada |
| Linhas + diagnóstico do SymPy | 4/10; mediana 171 ms/chamada | 6/10; mediana 557 ms/chamada |

Os tempos são exploratórios: uma chamada por caso após aquecimento, LAYA em CPU
e Qwen via Ollama no seu runtime próprio com GPU unificada. Não estabelecem uma
comparação justa de velocidade entre arquiteturas. Carga inicial LAYA com download:
75,91 s; segunda carga, com cache: 6,77 s. Não foi medido pico de RAM.

## Fonte, checkpoint e licença

- Código LAYA **0.4.22**, inspecionado e instalado do
  [commit `462c2644e654add83516e53c7a65909f8072d529`](https://github.com/NandhaKishorM/laya/tree/462c2644e654add83516e53c7a65909f8072d529).
- Checkpoint: [convaiinnovations/laya-multilingual](https://huggingface.co/convaiinnovations/laya-multilingual),
  revisão `e4e9ddf21a7b1903b7acffd8814ad4307bf63a67`, fornecida explicitamente ao loader.
- Código e checkpoint: Apache-2.0. [Aviso de licença do código](LICENSE-LAYA.txt).
- Cerca de 647 MiB de cache local após o download. Os pesos e o ambiente estão
  ignorados pelo Git; não fazem parte da entrega publicada.
- O script de controle deriva do [exemplo mínimo oficial](https://github.com/NandhaKishorM/laya/blob/462c2644e654add83516e53c7a65909f8072d529/examples/01_first_call_minimal.py).
  Mantém sua entrada e pergunta, escolhe o checkpoint multilíngue e CPU, fixa a
  revisão e acrescenta funções para reutilização e registro do resultado.

## O que foi testado

[casos.json](casos.json) contém duas transições por categoria: troca de sinal,
distributiva, aritmética, passo equivalente e leitura inválida. São dados sintéticos
escritos com apoio de IA; a taxonomia e os rótulos foram definidos antes de executar.
O campo `esperado` serve apenas à conferência e não é enviado aos modelos.

As duas condições foram executadas em sequência, com os mesmos casos e critérios,
sem ajuste de prompt para melhorar as respostas após observar os resultados.
Na segunda, o status de equivalência/leitura é calculado pelo SymPy a partir das
equações; o diagnóstico de tipo de erro continua sendo responsabilidade do modelo.

O benchmark pede apenas uma categoria; não lê imagens, não dá dicas, não usa
treinamento ou fine-tuning, e não é o mesmo prompt de geração de pistas do artefato
principal. O Qwen usa um JSON Schema com as cinco categorias permitidas. Isso
restringe o formato, mas não torna correta a decisão.

## Evidências completas

- [Exemplo de controle](resultados/exemplo_oficial.json).
- [Primeiro ensaio: stdout](resultados/execucao.stdout.txt), [stderr](resultados/execucao.stderr.txt),
  [todos os resultados brutos](resultados/casos_observados.json), [ambiente e resumo](resultados/resumo.json).
- [Com SymPy: stdout](resultados/com_sympy/execucao.stdout.txt), [stderr](resultados/com_sympy/execucao.stderr.txt),
  [resultados brutos](resultados/com_sympy/casos_observados.json), [ambiente e resumo](resultados/com_sympy/resumo.json).
- [Tabela por caso](resultados/comparacao.md).

O primeiro ensaio não teve corte de entrada/perguntas segundo o `usage` de nenhuma
das dez respostas LAYA. O mesmo foi conferido no segundo. As respostas Qwen
terminaram normalmente (`done_reason: stop`), sem atingir o limite de geração.

## Como reproduzir

Na raiz do repositório, para preparar um ambiente próprio:

```bash
python3 -m venv tec/experimentos/laya/.venv
tec/experimentos/laya/.venv/bin/python -m pip install -r tec/experimentos/laya/requirements-lock.txt
```

Nesta máquina, o ambiente já foi criado e a instalação pela fonte foi executada.
O Ollama precisa estar ativo em `localhost:11434`, com `qwen2.5:1.5b` instalado.

```bash
# Primeiro uso: permite baixar o checkpoint público.
./tec/experimentos/laya/rodar.sh

# Checkpoint em cache: compara também com o status do verificador simbólico.
HF_HUB_OFFLINE=1 ./tec/experimentos/laya/rodar.sh --contexto-sympy

# Apenas LAYA, sem chamar Ollama.
HF_HUB_OFFLINE=1 ./tec/experimentos/laya/rodar.sh --sem-qwen
```

Esses comandos atualizam os resultados da condição correspondente. Preserve uma
cópia se quiser comparar outra execução. O `HF_HOME` padrão do experimento é
`.cache/huggingface/` dentro desta pasta; nenhum peso é incluído nos commits.

## Implicação para o projeto

O modelo produz uma categoria permitida, mas pode escolher a categoria errada
com probabilidade alta: no primeiro caso de troca de sinal, escolheu `aritmetica`
com `0.8158` no ensaio sem SymPy. É um exemplo de excesso de confiança observado.

A proposta de usar LAYA para escolher uma pista pré-escrita exige antes validar
o diagnóstico. O ensaio não autoriza essa adoção. A [pesquisa de alternativas](../../alternativas.md)
discute GLiClass, mDeBERTa e alternativas específicas de OCR.

O artefato principal continua documentado em [tec.md](../../tec.md). Esta pasta
adiciona pesquisa e evidências; não substitui a auditoria cega nem os textos que
devem ser escritos pela aluna.
