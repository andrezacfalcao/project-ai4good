# Conferência do artefato [5] — arena git repo

Rubrica: cinco itens, dois pontos por item. Esta matriz identifica evidência; não atribui nota em nome do professor.

| Item | Antes desta revisão | Implementação atual | O que falta para demonstração |
|---|---|---|---|
| 1. Subrepositório estruturado | Pasta isolada, sem CONTEXT.md | `arn-c/CONTEXT.md`, propósito, escopo, papéis e histórico selecionado | Conferência do avaliador |
| 2. Diagrama e fluxo | Diagrama/documentação com ambiguidade sobre remoto | README com papéis, pesquisa, sequência, retorno e salvamento | Conferência do avaliador |
| 3. Prompts e parâmetros | Perfil local explícito; outros papéis eram textos fixos | Arquivos de sistema consumidos pelo código, temperatura e contexto por perfil | Conferir configuração e payloads de uma nova execução |
| 4. Busca em tempo de execução | Links de referência, sem integração de busca | Pesquisador chama Google Search via Gemini; exige consultas e fontes retornadas | Rodar com credencial e apresentar `research.grounding.webSearchQueries` e `groundingChunks` nos resultados novos |
| 5. Thinking/reasoning e atuação | Sem configuração comprovada nos registros antigos | Gemini com thinking habilitado e juiz que lê o debate real | Rodar com credencial; registrar parâmetros, `thought_tokens_observed` quando retornado e avaliação pública das falas |

## Critério 4: o que não conta

Uma lista fixa de links, uma pesquisa manual feita antes da execução ou uma ferramenta apenas mencionada no prompt não demonstram busca do agente em tempo de execução. O adaptador exige consultas e fontes em `groundingMetadata` para aceitar a etapa de pesquisa.

## Critério 5: o que é registrado

- Modelo solicitado e `modelVersion` quando fornecido pela API.
- `thinkingBudget` positivo no Gemini 2.5, ou `thinkingLevel: high` nos modelos 3/4 compatíveis.
- Contagem de tokens de thinking quando fornecida pela API.
- Argumento, justificativa pública, limites e parecer sobre as quatro falas reais.

Uma configuração positiva não garante que a resposta seja correta. Se a contagem de thinking for zero ou ausente, isso permanece explícito. Não publicar cadeia privada de pensamento; usar explicação pública e dados de uso para auditoria.

## Limite atual

A integração remota não foi executada nesta revisão porque `GEMINI_API_KEY` não está configurada. Portanto, **itens 4 e 5 têm código, mas não têm demonstração externa nova**. Os vinte registros preservados não foram adulterados para suprir essa ausência.

## Por que parecia haver mais de vinte rodadas

O mesmo intercâmbio aparecia em `rodadas`, `entradas`, `intercambio`, `julgamentos` e `chamadas_locais`. A cópia anterior também incluía um incidente antigo. A revisão conserva somente o conjunto canônico 01–20. Cada JSON contém as tentativas e o juiz; o Markdown é a versão para leitura. Os 26 PNG são slides da apresentação anterior.

## Seleção das últimas alterações

Foram preservados os últimos vinte registros disponíveis, todos do protocolo 4. Não foram carregados os experimentos antigos nem criadas rodadas 21 em diante. O código posterior v5 não tinha novos vinte resultados correspondentes. O protocolo 6 implementado agora é distinguido de ambos e aguarda execução autenticada.
