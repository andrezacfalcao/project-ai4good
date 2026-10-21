# Prompts de sistema e parâmetros por agente

O executor carrega diretamente os arquivos abaixo. Eles não são apenas documentação paralela. As mensagens completas de cada chamada ficam nos JSONs das novas rodadas, sem cabeçalhos de autenticação.

| Agente | Prompt de sistema | Modelo padrão | Temperatura | Limite de contexto da aplicação | Saída / thinking |
|---|---|---|---|---|---|
| Trabalhista | `prompts/trabalhista.md` | `gemini-2.5-flash` | 0,4 | 18.000 caracteres de entrada | 4.096 tokens máximos de geração, incluindo thinking; orçamento thinking 1.024 |
| Liberal local | `prompts/liberal_qwen.md` + instrução de JSON/tema | `qwen2.5:1.5b` | 0,25 / 0,55 / 0,8 por tentativa | `num_ctx:1024` tokens | `num_predict:140`; `repeat_penalty:1.18`; sem thinking declarado |
| Juiz | `prompts/juiz.md` | `gemini-2.5-flash` | 0,2 | 24.000 caracteres de entrada | 8.192 tokens máximos de geração, incluindo thinking; orçamento thinking 2.048 |
| Pesquisador | `prompts/pesquisador.md` | `gemini-2.5-flash` | 0,2 | 10.000 caracteres de entrada | 4.096 tokens máximos de geração; orçamento thinking 1.024; Google Search |

**Caracteres não são tokens.** Os limites dos remotos são controles da aplicação, sem afirmar que equivalem à janela máxima do provedor. Excedê-los interrompe a chamada; não se corta silenciosamente uma fala. A memória deliberadamente resumida do juiz usa até 1.800 caracteres entre rodadas.

Os limites de geração Gemini incluem os tokens de thinking; não são uma promessa de saída com esse comprimento. `includeThoughts:false` evita solicitar a divulgação de pensamento interno.

## Composição do prompt local

`ponte_debate.call_qwen` usa o perfil liberal e acrescenta formato JSON, tema e termos de foco. No segundo turno, a primeira resposta local entra como mensagem `assistant` e a nova tarefa entra como `user`. A configuração alimenta os parâmetros da requisição; os valores efetivos ficam no payload registrado.

O perfil liberal é uma posição definida para esta arena. Não representa todas as correntes liberais nem pressupõe que qualquer proibição do perfil seja uma conclusão científica.

## Controles locais preservados

- De 12 a 125 palavras; interrupção por limite de tokens é recusada.
- Idioma provável em português, com limitação heurística.
- Cópia de mais de 45% dos seis-gramas da entrada é recusada.
- Similaridade de risco entre os dois turnos de pelo menos 65% é recusada.
- Similaridade global com respostas locais recentes de pelo menos 85% é recusada.
- Termos do tema e exclusão de certos termos anteriores, conforme configuração.
- Até três tentativas locais com feedback; falhas e saídas são preservadas.

Esses números são escolhas do experimento, não limiares validados cientificamente. Podem recusar uma resposta útil ou aceitar uma resposta ruim. A avaliação semântica do juiz continua necessária.

## Novas chamadas remotas

O adaptador permite até duas tentativas por etapa em cada invocação da execução/retomada. Uma falha não gera texto substituto. O checkpoint mantém tentativas anteriores e o motivo da interrupção. A configuração e o código são identificados por hashes para impedir retomada com mistura de versões.

## Metadados da execução preservada

Os parâmetros da tabela são do código novo. Os vinte registros históricos têm protocolo 4 e parâmetros próprios — por exemplo, temperatura0,3/0,5/0,7, contexto1.024 e geração150 nos registros locais. Esses valores não foram substituídos pelos novos.
