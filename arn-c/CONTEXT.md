# ARN-C — contexto do artefato arena git repo

**Autora:** Andreza Maria Coutinho Falcão. **Idioma:** pt-BR. **Código no painel:** `arn·c`. Diretório no Git: `arn-c`.

## Propósito

Investigar como inteligência artificial, automação e gestão algorítmica podem modificar emprego, renda, poder de negociação e proteção social. A arena contrapõe propostas trabalhistas e liberais e usa um juiz para exigir mecanismos, evidências e limites. O pesquisador consulta a web durante a execução.

O experimento produz uma sequência de passos conectados, com responsáveis, indicadores e riscos. Não pretende provar que uma proposta salvará o mundo nem otimizar a produção de danos. Distopia é diagnóstico de uma trajetória adversa, com sinais e prevenção.

## O que está sendo entregue

1. **Um conjunto selecionado de vinte rodadas anteriores**, numeradas 01–20, em `resultados/ultima_execucao/rodadas/`. São vinte `.md` para leitura e vinte `.json` dos mesmos registros. Não são quarenta rodadas. Os JSONs já contêm chamadas, tentativas e julgamentos; por isso não foram mantidas pastas duplicadas de entradas, intercâmbio ou chamadas locais.
2. **Executor atualizado, protocolo 6**, com chamadas remotas reais, busca Google Search e configuração explícita de thinking. Ele não foi usado para reescrever as vinte rodadas preservadas.
3. **Materiais da apresentação anterior**, em `materiais/`. Existem 26 páginas/imagens de slides, que não são 26 rodadas. Não foram regeneradas nesta revisão.

As execuções antigas, os incidentes de acesso e os rascunhos não integram este subdiretório. O conjunto selecionado está identificado por hashes no `manifesto.json`. A preparação e eventuais cópias de trabalho fora do repositório não contam como evidência adicional do artefato.

## Histórico e limite das evidências

O último conjunto disponível registra **protocolo 4**, Qwen2.5 1,5B em quarenta turnos locais e sessenta e quatro requisições incluindo tentativas. O código encontrado posteriormente tinha versão 5 e falas/pareceres remotos pré-definidos. Esses dois fatos não foram igualados por edição dos resultados.

Os arquivos anteriores atribuem os papéis remotos a Antigravity/Gemini, sem registro de novas chamadas remotas realizadas pelo executor antigo. Também não comprovam busca web em tempo de execução nem thinking configurado. Não servem como prova retrospectiva dos critérios 4 e 5.

O protocolo 6 remove as falas remotas fixas. Sem `GEMINI_API_KEY` no ambiente, a integração nova permanece **implementada, mas sem validação externa e sem novas vinte rodadas**. Não marcar os critérios 4 e 5 como demonstrados apenas porque há código ou links.

## Papéis e responsabilidades

| Agente | Localização | Responsabilidade |
|---|---|---|
| Trabalhista | Gemini por API remota | Abrir cada rodada, defender direitos e responder às objeções reais do Qwen |
| Liberal | Qwen2.5 1,5B no Ollama local | Formular risco/custo e pergunta; abrir segundo turno com outro foco |
| Juiz | Outra chamada e outro perfil Gemini | Comparar as quatro falas, criticar evidências, atualizar passos e memória |
| Pesquisador | Gemini com ferramenta Google Search | Buscar fontes em cada rodada, retornar contrapontos e registrar consultas e URLs |

São perfis diferentes; os remotos podem usar o mesmo modelo. Não se confunde o nome de um ambiente de autoria com um identificador de modelo da API.

## Protocolo de comunicação

Cada rodada recebe um tema, uma pergunta específica, o cenário e uma memória curta. A pesquisa precede a discussão. Abertura trabalhista e retorno do Qwen são lidos antes da defesa. O juiz recebe os quatro textos reais e as evidências encontradas. A memória que ele produz vai para a próxima rodada.

O fluxo é sequencial por dependência das mensagens. Não há geração antecipada das vinte falas remotas. Um checkpoint permite retomar etapas sem repetir chamadas concluídas. Cenários utópico e distópico usam diretórios, estados e memórias independentes. Cada execução nova contém exatamente vinte rodadas; não se juntam dois cenários em uma contagem única de vinte.

## Repetição e qualidade

O Qwen recebe contexto curto e retorna JSON com `risco` e `pergunta`. Há até três tentativas por etapa, com feedback sobre a recusa. Filtros verificam idioma provável, cópia da entrada, similaridade global, repetição do risco entre turnos e termos do tema. O juiz examina repetição semântica e pertinência. Nenhum filtro demonstra correção econômica ou jurídica.

Se todas as tentativas locais falharem, o resultado fica como `accepted: false`; não se substitui por fala do Gemini. Falha de busca ou geração remota interrompe a rodada e preserva o checkpoint, sem produzir um parecer fixo de sucesso.

## Pesquisa e raciocínio

O pesquisador usa `tools: [{google_search: {}}]`. Para considerar busca executada, a resposta precisa conter consultas e fontes em `groundingMetadata`. Links estáticos da configuração não contam como execução da ferramenta.

Gemini 2.5 usa `thinkingBudget` positivo; Gemini 3/4, quando selecionados por configuração, usam `thinkingLevel: high`. As respostas registram modelo efetivo quando fornecido, parâmetros, metadados de busca e contagem de tokens de thinking quando retornada. O número pode ser ausente ou zero: nesse caso, não se afirma que a atuação foi comprovada.

O artefato guarda justificativas públicas, pressupostos e limites. Não solicita nem publica a cadeia privada de pensamento interno. O Qwen2.5 local não é apresentado como modelo de thinking.

## Critérios de qualidade da estratégia

- Dependência lógica entre passos e mecanismo plausível.
- Fontes primárias, contrapontos e alcance da evidência.
- Responsáveis e indicadores definidos.
- Distribuição dos efeitos, financiamento e capacidade institucional.
- Limites, critérios de revisão e hipóteses ainda não testadas.

O desempenho de modelos ou o número de rodadas não valida políticas públicas. A conferência dos cinco itens da rubrica está em `docs/CRITERIOS.md`.
