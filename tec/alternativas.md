# Pesquisa de tecnologias · LAYA e alternativas

Fontes consultadas em **03/11/2026**. Os nomes abaixo representam peças diferentes
do Atlas do Erro. Reconhecer uma foto, verificar uma igualdade, classificar um
erro e escrever uma pista são tarefas distintas.

## Onde LAYA se encaixa

O [LAYA](https://github.com/NandhaKishorM/laya) é um mecanismo de decisão sobre
texto ou JSON. Sua API oferece `choice` (categoria), `noul` (sim/não) e `score`
(escala). O código não é um OCR nem um gerador livre de dicas. Sua utilidade
potencial aqui é escolher uma categoria a partir das linhas transcritas e do
diagnóstico do verificador. Uma categoria poderia selecionar uma pista escrita
previamente pelo professor, desde que o diagnóstico fosse confiável.

Código: [Apache-2.0](https://github.com/NandhaKishorM/laya/blob/main/LICENSE).
O [checkpoint multilíngue](https://huggingface.co/convaiinnovations/laya-multilingual)
declara Apache-2.0 e 322 milhões de parâmetros. É uma opção mais coerente para
português que o checkpoint descrito pelo projeto como inglês. A model card
reconhece erros de classificação e excesso de confiança; a frase promocional
“nothing to hallucinate” não significa que a decisão esteja correta.

**Teste local realizado:** [relatório e reprodução](experimentos/laya/README.md).
Foram dez transições sintéticas, com a taxonomia definida antes do teste:

| Condição | LAYA multilingual | Qwen2.5 1.5B |
| --- | --- | --- |
| Somente as duas linhas | 3/10 categorias corretas | 1/10 |
| Linhas + diagnóstico calculado pelo SymPy | 4/10 | 6/10 |

Nenhum dos dois deve ser tratado como classificador pedagógico confiável com
base nesses resultados. Os ensaios usam dez exemplos escritos com apoio de IA,
sem professor rotulador nem conjunto independente. Não medem OCR, qualidade de
pistas ou aprendizagem. O Qwen recebeu um prompt novo para essa tarefa isolada;
os resultados não são a acurácia do protótipo anterior inteiro.

## Alternativas para classificação textual

| Opção e fonte oficial | Licença | O que pode oferecer | Limite para o nosso caso | Situação local |
| --- | --- | --- | --- | --- |
| [LAYA multilingual](https://huggingface.co/convaiinnovations/laya-multilingual) | Código e checkpoint Apache-2.0 | Categorias fechadas e probabilidades, sem texto gerado | Zero-shot não demonstrou domínio dos tipos de erro de álgebra; houve escolhas erradas com probabilidade alta | Executado: 3/10 e 4/10 nas condições acima |
| [GLiClass](https://github.com/Knowledgator/GLiClass), candidato [v4-edge](https://huggingface.co/knowledgator/gliclass-v4-edge) | Código e este checkpoint Apache-2.0 | Classificação zero-shot com rótulos e instruções, também sem geração livre | O checkpoint consultado está identificado como inglês; nem português nem diagnóstico de álgebra estão validados aqui | Documentação consultada; não instalado nem executado |
| [mDeBERTa-v3-base-mnli-xnli](https://huggingface.co/MoritzLaurer/mDeBERTa-v3-base-mnli-xnli) | Checkpoint MIT; runtime Transformers tem licença própria | Classificação multilíngue via inferência textual, com exemplo oficial curto | Foi ajustado para NLI, não correção de matemática; português não aparece entre as 15 línguas da tabela XNLI da model card | Documentação consultada; não instalado nem executado |
| Qwen2.5 1.5B da base existente | [Checkpoint Apache-2.0](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct/blob/main/LICENSE) | Pode classificar e formular linguagem natural; já existe no Ollama local | Neste teste de categorias também errou; no protótipo anterior houve dica que entregou o passo corrigido | Executado nas mesmas dez entradas; resultados acima |
| SymPy + regras explícitas | [SymPy BSD-3-Clause](https://github.com/sympy/sympy/blob/master/LICENSE) | Validar equivalência e tratar estados como leitura inválida e passo equivalente | Classificar a causa conceitual exige regras adicionais e validação; não se deduz intenção do aluno só pela conta | Equivalência executada; classificador de causas por regras ainda não implementado |

## Alternativas para ler o caderno

Esta é a técnica central do brw. Testar LAYA não resolve o problema de OCR
observado no terceiro caderno da demonstração.

| Opção e fonte oficial | Licença consultada | Por que investigar | Limite / requisito ainda por conferir | Situação local |
| --- | --- | --- | --- | --- |
| [TrOCR small printed](https://huggingface.co/microsoft/trocr-small-printed) | Código UniLM MIT; model card sem licença própria explícita | Baseline leve que já roda e permite observar onde a leitura falha | Ajustado para texto impresso, não matemática manuscrita; recorte fixo de três linhas no protótipo | Executado no artefato principal; sete de nove linhas sintéticas exatas após normalizar caixa/espaços |
| [TrOCR base handwritten](https://huggingface.co/microsoft/trocr-base-handwritten) | Model card MIT | Comparação da mesma família ajustada a manuscritos IAM | Manuscrito textual não equivale a expressão matemática; RAM e leitura dos sinais precisam ser medidas | Não executado neste projeto |
| [pix2tex / LaTeX-OCR](https://github.com/lukas-blecher/LaTeX-OCR) | Código MIT; licença dos pesos não conferida separadamente nesta pesquisa | Converte imagens de fórmulas para LaTeX e tem exemplo Python curto | Fotos de resoluções manuscritas completas e execução neste Mac continuam por validar | Não executado neste projeto |
| [PaddleOCR-VL 0.9B](https://huggingface.co/PaddlePaddle/PaddleOCR-VL), [código](https://github.com/PaddlePaddle/PaddleOCR) | Código e checkpoint Apache-2.0 | Model card inclui reconhecimento de fórmulas e manuscritos; candidato pertinente para a etapa visual | Os exemplos incluem caminhos GPU/Paddle e Transformers; compatibilidade e consumo no Mac ainda não medidos. O checkpoint consultado é o 0.9B original, não toda a família | Não instalado nem executado |

Não usamos resultados de benchmarks genéricos dos autores como se fossem
medidas em cadernos brasileiros ou no computador da aluna.

## Recomendação técnica após os ensaios

1. Manter a validação de equivalência no SymPy. Leitura inválida e ausência de
   quebra podem ser tratadas por regras, sem pedir que o classificador redescubra
   o que já foi calculado.
2. Registrar LAYA como opção testada, com o resultado negativo no recorte atual.
   Não há evidência para adotá-lo como responsável autônomo pelo diagnóstico.
3. Para o próximo ensaio de leitura, priorizar uma comparação controlada do OCR
   atual com uma opção voltada a manuscritos/fórmulas, usando as mesmas fotos reais
   e transcrições de referência. PaddleOCR-VL e TrOCR handwritten são candidatos;
   a escolha ainda é da aluna.
4. Se a classificação continuar no projeto, compará-la com uma lista fixa de
   regras e rótulos revisados pelo professor, como previsto no brw. Dez casos
   sintéticos não bastam para escolher a tecnologia final.

Esta pesquisa não é uma auditoria cega nem a justificativa pessoal da aluna.
