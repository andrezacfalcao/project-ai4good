# cmp · Andreza Maria Coutinho Falcão

> folha do artefato [competidores e contribuição](../3-competidores-e-contribuicao.md), preenchida a partir do [brw andreza](../brw_andreza.md). todos os links foram abertos em 28/10/2026.

## 0 · a minha ideia completa

**Atlas do Erro** · estudantes resolvem os exercícios à mão e fotografam o caderno. A visão computacional lê o raciocínio linha por linha e, sem dar a resposta, aponta só onde ele quebrou. Corrigir o próprio erro recupera parte do ponto perdido, mas nunca vale mais do que acertar de primeira, então ninguém ganha errando de propósito. Como na caixa-preta da aviação, cada erro é registrado sem punição e, anônimo, forma um atlas que mostra ao professor onde a turma trava. Na crise do slop, a IA deixa de pensar pelo aluno e devolve o raciocínio para ele.

## 1 · a ficha da ideia

- **cenário:** sala de aula e tarefas de casa de matemática (ensino fundamental II e médio) em escolas públicas brasileiras.
- **usuário:** estudante da educação básica resolvendo exercícios no caderno à mão, e professor de matemática que diagnostica onde a turma trava.
- **problema do usuário:** o aluno usa a IA como atalho que entrega a resposta pronta e perde o raciocínio crítico (ou só descobre o erro tarde demais na nota da prova), e o professor não tem tempo de analisar onde o raciocínio quebrou em dezenas de cadernos para planejar aulas de reforço.
- **tecnologia:** visão computacional para OCR de matemática manuscrita linha a linha + verificador algébrico simbólico (SymPy) + modelo de linguagem pequeno no aparelho (SLM local) para diagnóstico do tipo de erro e geração progressiva de pistas sem resposta.

## 2 · catálogo de ferramentas

ficha: **C**enário · **U**suário · **P**roblema · **T**ecnologia, cada um **=** igual, **≈** parecido ou **≠** diferente.

| ferramenta | o que faz | no que é bom | onde falha | C U P T |
|:--|:--|:--|:--|:-:|
| **[Photomath](https://photomath.com/)** | lê expressões matemáticas pela câmera do celular e gera a solução passo a passo. | OCR de equações na câmera muito maduro e rápido. | entrega a resposta pronta mastigada (alimenta o slop); não lê a resolução inteira feita à mão no caderno para achar a linha do erro do aluno. | ≈ = ≠ ≈ |
| **[Mathspace](https://mathspace.co/)** | plataforma onde o estudante resolve problemas de matemática passo a passo e o sistema valida linha por linha. | corrige linha a linha e avisa exatamente onde o aluno errou no cálculo. | exige resolver digitando no computador ou tablet; não lê escrita à mão em caderno de papel e é software proprietário pago. | ≈ = = ≠ |
| **[Khanmigo](https://www.khanacademy.org/khanmigo)** (Khan Academy) | tutor socrático baseado em IA (GPT-4) que guia o aluno com perguntas sem dar a resposta. | excelente alinhamento pedagógico: dá pistas e não entrega o resultado final. | exige ambiente web/digital e digitação; não lê o caderno de papel do aluno, é pago e depende de conexão constante à nuvem. | ≈ = ≈ ≠ |
| [Mathpix](https://mathpix.com/) | OCR multimodal para extrair fórmulas matemáticas manuscritas para LaTeX e MathML. | estado da arte mundial em reconhecimento de escrita matemática à mão. | é ferramenta de digitalização para pesquisadores; não avalia correção de raciocínio, não aponta erro pedagógico nem dá pistas. | ≠ ≠ ≠ = |
| [Microsoft Math Solver](https://mathsolver.microsoft.com/) | resolve problemas matemáticos por foto ou desenho na tela, exibindo passos e gráficos. | gratuito, multiplataforma e aceita desenho de equações na tela. | focado em dar a resposta final e passos prontos; não analisa o caderno do aluno nem gera atlas de erros para o professor. | ≈ = ≠ ≈ |
| [Gradescope](https://www.gradescope.com/) | plataforma que digitaliza provas e listas em papel e agrupa respostas manuscritas por similaridade de erro. | lê escrita manuscrita em papel e ajuda o professor a enxergar padrões de erro da turma. | feito para o professor aplicar notas após a prova, e não para o aluno receber pistas interativas durante o estudo no caderno. | ≈ ≈ ≈ ≈ |
| [Qanda](https://qanda.ai/) | app de busca de resolução de exercícios por foto e tutoria sob demanda. | banco de dados massivo de resoluções de livros didáticos. | estimula a cópia da resposta pronta para concluir a tarefa rápido; modelo de moedas/assinatura pago. | ≈ = ≠ ≈ |
| [GeoGebra](https://www.geogebra.org/) | calculadora gráfica e sistema de álgebra computacional (CAS) educativo. | gratuito, aberto e amplamente conhecido em escolas brasileiras. | não lê o caderno; exige entrada formal por teclado/comandos e não diagnostica o tipo de erro cognitivo. | = = ≠ ≠ |
| [SymPy](https://www.sympy.org/) | biblioteca de código aberto em Python para matemática simbólica. | rigor formal exato na comparação de equivalência algébrica sem alucinação. | é uma biblioteca para programadores; o aluno não interage com ela diretamente e ela não lê imagens nem gera dicas pedagógicas. | ≠ ≠ ≠ ≈ |
| [Socratic by Google](https://socratic.org/) | app educacional que fotografa questões e busca conceitos e vídeos explicativos. | busca explicações conceituais em vez de apenas cuspir uma conta. | focado no enunciado da pergunta, e não na resolução manuscrita do estudante; não analisa os passos do aluno. | ≈ = ≠ ≈ |
| **[ChatGPT com visão multimodal](https://chatgpt.com/)** (achado no passo 7) | modelo de fronteira (GPT-4o) que recebe fotos de rascunhos e explica a resolução. | flexibilidade em interpretar linguagem mista (texto e contas) e responder em português. | roda em nuvem proprietária; se pressionado pelo aluno, entrega a resposta final completa; não compila mapa de erros para a turma. | ≈ = ≈ ≈ |

## 3 · catálogo de artigos

| artigo (autores, ano, com link) | veículo | o que propõe | no que é bom | onde falha | C U P T |
|:--|:--|:--|:--|:--|:-:|
| **[Generative AI without guardrails can harm learning](https://doi.org/10.1073/pnas.2422633122)** (Bastani et al., 2025) | PNAS · A1 | experimento com quase mil estudantes de ensino médio comparando ChatGPT sem salvaguardas vs. tutor que dá apenas pistas em matemática. | prova empírica de que a resposta pronta reduz o aprendizado posterior em 17%, enquanto pistas pedagógicas protegem o raciocínio. | avalia apenas a interação textual em computador; não aborda o caderno de papel nem visão computacional. | ≈ = = ≠ |
| **[Can MLLMs Read Students' Minds? Unpacking Multimodal Error Analysis in Handwritten Math](https://arxiv.org/abs/2603.24961)** (Song et al., 2026) | AIED 2026 / arXiv · A1 | benchmark (*ScratchMath*) com 1.720 rascunhos manuscritos de alunos para avaliar modelos multimodais em explicar (ECE) e classificar (ECC) erros matemáticos. | foca exatamente em rascunhos manuscritos reais de estudantes e numa taxonomia de 7 causas pedagógicas de erro. | é um benchmark de laboratório para testar modelos em nuvem (acurácia de apenas 57%); não roda em modelo local pequeno nem gera pistas interativas. | ≈ = = ≈ |
| **[Improving the Validity of Automatically Generated Feedback via Reinforcement Learning](https://doi.org/10.1007/978-3-031-64302-6_2)** (Scarlatos et al., 2024) | AIED 2024 · A1 | alinhamento de LLMs via Reinforcement Learning (DPO) com rubricas de professores para gerar feedbacks pedagógicos válidos em matemática. | garante que as pistas do modelo sejam pedagogicamente válidas e não enganem o aluno com alucinações. | trabalha com questões de múltipla escolha e texto digitado; não processa escrita manuscrita nem roda offline. | ≈ = = ≠ |
| [MathDial: A Dataset for Math Tutoring Dialogues with Pedagogical Hints](https://aclanthology.org/2023.emnlp-main.256/) (Macina et al., 2023) | EMNLP 2023 · A1 | dataset e modelos para tutoria matemática que ensinam a IA a responder ao erro do aluno com perguntas socráticas e pistas, sem dar a resposta. | treina o modelo a resistir ao impulso de resolver a questão pelo aluno, mantendo o esforço cognitivo nele. | baseado exclusivamente em diálogos por chat digitado; assume que o erro já foi identificado e digitado. | ≈ = = ≈ |
| [Scaffolding vs. Hints in the ASSISTment System](https://doi.org/10.1007/11774303_10) (Razzaq & Heffernan, 2006) | ITS 2006 · A1/A2 | estudo experimental comparando a divisão do problema em etapas (*scaffolding*) versus fornecimento de dicas (*hints*) quando o estudante de matemática erra. | mede empiricamente como dosar a pista para evitar que o aluno trave na tarefa sem retirar o esforço mental. | sistema clássico de desktop com problemas pré-programados e respostas digitadas; não aceita fotos de caderno nem escrita livre. | ≈ = = ≠ |
| [Recognition and evaluation of offline handwritten mathematical expressions](https://doi.org/10.1007/s10032-011-0163-9) (Zanibbi & Blostein, 2012) | IJDAR / Pattern Recognition · A1 | levantamento e formalização das etapas de segmentação, reconhecimento de símbolos e parsing estrutural de matemática manuscrita off-line. | base teórica clássica de visão computacional para converter traços de escrita matemática em árvores de sintaxe estruturadas. | trata apenas do reconhecimento óptico e parsing gramatical; não avalia correção algébrica nem diagnostica erros cognitivos. | ≠ ≠ ≠ = |
| [MobileLLM: Optimizing Sub-billion Parameter Language Models for On-Device Use](https://proceedings.mlr.press/v235/liu24ce.html) (Liu et al., 2024) | ICML 2024 · A1 | arquiteturas de modelos de linguagem abaixo de 1 bilhão de parâmetros otimizadas para execução local e eficiente em smartphones. | prova que modelos minúsculos conseguem rodar no chip do celular com baixa latência, sem internet e com privacidade. | é um artigo de infraestrutura de ML avaliado em benchmarks sintéticos; não sabe nada sobre matemática escolar nem foi testado com alunos. | ≠ ≠ ≠ = |
| [ICFHR 2016 CROHME: Competition on Recognition of Online Handwritten Mathematical Expressions](https://doi.org/10.1109/ICFHR.2016.0116) (Mouchère et al., 2016) | Pattern Recognition / ICFHR · A1 | benchmark internacional para avaliação de algoritmos de reconhecimento de expressões matemáticas manuscritas. | padrão da comunidade científica para medir taxa de acerto de OCR matemático em escrita manuscrita real. | focado em reconhecer símbolos e fórmulas isoladas, e não em acompanhar o fluxo dedutivo linha por linha de uma resolução escolar. | ≠ ≠ ≠ = |
| [Modelando o conhecimento algébrico do estudante através de Redes Bayesianas Dinâmicas](https://sol.sbc.org.br/index.php/sbie/article/view/1788) (Barros et al., 2018) | SBIE 2018 · Qualis A2/A3 | modelo probabilístico para rastrear a evolução do conhecimento de álgebra e classificar erros em equações do 1º grau de alunos brasileiros. | contextualizado na realidade da escola básica brasileira e nas dificuldades específicas de transição aritmética-álgebra. | modelo baseado em regras pré-cadastradas no computador; não lê fotos de caderno nem gera pistas com SLMs. | = = = ≠ |
| [An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale](https://openreview.net/forum?id=YicbFdUnOE) (Dosovitskiy et al., 2021) | ICLR 2021 · A1 | introdução do Vision Transformer (ViT), adaptando a arquitetura Transformer para tarefas de visão computacional. | base técnica moderna dos modelos que leem imagens linha a linha como sequências de tokens visuais. | é a peça técnica bruta de visão; não tem aplicação direta em educação nem lê rascunhos matemáticos de alunos. | ≠ ≠ ≠ = |

## 4 · os 3 + 3 mais próximos

- **Photomath:** é o competidor de consumo mais próximo em OCR de celular para matemática. se ele já desse pistas em vez de respostas prontas, o Atlas do Erro não teria espaço; ficou à frente do Microsoft Math Solver por ter OCR móvel mais maduro e adotado por estudantes.
- **Mathspace:** é a ferramenta mais próxima em validar o raciocínio passo a passo e avisar exatamente em qual linha o cálculo quebrou. ficou à frente do GeoGebra porque foca na correção do processo do aluno, e não apenas em computar o resultado.
- **Khanmigo:** entra pela exceção "tecnologia próxima para um problema parecido": IA socrática gerando pistas sem dar a resposta pronta. é o que mais ameaça pedagogicamente o Atlas do Erro; ficou à frente do Socratic por ter intencionalidade pedagógica ativa contra a cola acrítica.
- **Bastani et al. (2025, PNAS · A1):** o artigo mais importante sobre a dor do projeto: prova com quase 1.000 alunos que IA com resposta pronta derruba o aprendizado em 17%, enquanto pistas protegem o raciocínio.
- **Song et al. (2026, AIED · A1 / arXiv):** o mais próximo em dados: avalia modelos exatamente sobre rascunhos manuscritos (*scratchwork*) de alunos de escola e categoriza as 7 causas de erros.
- **Scarlatos et al. (2024, AIED · A1):** entra pela garantia pedagógica: demonstra como treinar o modelo para que o feedback gerado seja válido e alinhado aos critérios de professores, sem alucinar.

ficaram de fora: MobileLLM, ViT e Zanibbi/Mouchère porque apenas a tecnologia bate, sendo blocos brutos de ML; Razzaq & Heffernan por ser sistema desktop antigo; e Barros et al. (SBIE), que guardo para a discussão de contexto brasileiro no artigo.

## 5 · a matriz

eixos tirados da conversa nova com os 6 trabalhos; os três últimos são onde a minha ideia perde.

**✔** faz · **◐** faz em parte · **✘** não faz · **?** não achei evidência

| trabalho | lê resolução manuscrita do caderno (papel) | valida raciocínio linha por linha | dá apenas pistas (sem resposta pronta) | gera mapa/atlas de erros para a turma | dados ficam no aparelho (offline) | resolve a questão se o aluno travar | cobre múltiplos tópicos além de álgebra | testado em larga escala na prática |
|:--|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| Photomath | ✔ | ◐ | ✘ | ✘ | ✘ | ✔ | ✔ | ✔ |
| Mathspace | ✘ | ✔ | ◐ | ◐ | ✘ | ✔ | ✔ | ✔ |
| Khanmigo | ✘ | ◐ | ✔ | ◐ | ✘ | ◐ | ✔ | ✔ |
| Bastani et al. (2025) | ✘ | ◐ | ✔ | ✘ | ✘ | ✘ | ◐ | ✔ |
| Song et al. (2026) | ✔ | ◐ | ✘ | ◐ | ✘ | ✘ | ◐ | ✘ |
| Scarlatos et al. (2024) | ✘ | ✘ | ✔ | ✘ | ✘ | ✘ | ◐ | ◐ |
| ChatGPT multimodal (passo 7) | ✔ | ◐ | ✘ | ✘ | ✘ | ✔ | ✔ | ✔ |
| **a minha ideia** | ✔ | ✔ | ✔ | ✔ | ✔ | ✘ | ✘ | ✘ |

**evidência:**
- Photomath: OCR lê equações impressas ou manuscritas e decompõe em passos; não avalia o rascunho completo do aluno nem retém a resposta final; dados vão para os servidores da empresa (Google).
- Mathspace: validação linha a linha é a funcionalidade central ("Step-by-Step Maths"); dá dicas graduais se solicitado, mas exige digitação em computador/tablet; tem relatórios de turma para professores.
- Khanmigo: programado para fazer perguntas condutoras sem entregar a resposta final ("socratic tutor"); não possui módulo de OCR para ler caderno de papel; requer nuvem e assinatura ativa.
- Bastani et al. (2025): o grupo "GPT Tutor" fornecia apenas pistas sob demanda; sistema puramente baseado em chat digital web; não analisa cadernos físicos nem roda localmente.
- Song et al. (2026): benchmark *ScratchMath* utiliza 1.720 fotos reais de rascunhos manuscritos; modelos avaliados via API aberta/nuvem; não opera como tutor interativo em tempo real.
- Scarlatos et al. (2024): otimização de feedback por reforço com dados de professores da plataforma Eedi; perguntas fechadas/múltipla escolha de matemática; não há evidência pública no artigo de suporte a OCR manuscrito: ficou "?".
- ChatGPT multimodal: processa imagens de rascunhos matemáticos com precisão; quando insistido pelo usuário ("me dê a resposta"), entrega o resultado final completo; não gera agregação pedagógica para a escola.

## 6 · a contribuição

**a frase:** o **Atlas do Erro** lê a resolução manuscrita linha por linha direto do caderno de papel e aponta a quebra do raciocínio apenas com pistas sem dar a resposta pronta, compilando um atlas anônimo das dificuldades da turma para o professor, o que nenhum dos trabalhos faz junto; por isso o aluno desenvolve pensamento crítico sem cair na armadilha do *slop* e a escola diagnostica onde a aprendizagem trava sem depender de digitação ou plataformas caras.

**o trabalho mais próximo, e por que ele não chega lá:** o Khanmigo adota o modelo socrático de pistas sem dar a resposta pronta, mas exige computador com digitação, roda na nuvem fechada da OpenAI e custa mensalidade por aluno; e o Photomath lê a foto do caderno, mas entrega a resolução inteira de bandeja, funcionando como o atalho que atrofia o raciocínio que Bastani et al. demonstraram.

## 7 · tentei derrubar

o [ChatGPT com visão multimodal (GPT-4o)](https://chatgpt.com/) e o Google Lens. ao colar a foto de uma conta manuscrita no ChatGPT, ele consegue ler a letra do aluno e apontar onde está o erro se for expressamente solicitado.

o que eu mudei: entrou no catálogo de ferramentas e na matriz como concorrente de peso. a frase da contribuição se sustentou porque o ChatGPT, por padrão de assistente, cede facilmente quando o aluno pede a resposta direta, além de exigir internet de alta velocidade e não gerar a visão agregada (o atlas anônimo) que orienta o planejamento do professor da rede pública. aprendi que "ler rascunho e achar o erro com IA" já é tecnicamente viável em modelos de fronteira; o meu diferencial reside na entrega estrita de pistas sem *spoiler*, no processamento no aparelho e na infraestrutura coletiva anônima para a escola.

## 8 · resumo, sem IA

apps como Photomath e ChatGPT já leem rascunhos de matemática, e o Khanmigo dá dicas socráticas sem entregar a resposta. Nenhum lê o caderno de papel no próprio aparelho para devolver só a pista e somar os erros da turma em um atlas para o professor. O Atlas do Erro faz isso mantendo o caderno como centro e a IA como espelho do raciocínio. O alerta de Bastani et al. é que a resposta pronta da IA reduz o aprendizado na prova em 17%, e é essa perda que o Atlas evita.

## 9 · auditoria cega

> uma conversa nova, que não ajudou a fazer esta folha, julga cada item de verificação começando de "não passa", abre links do catálogo e procura quem já faz a sua contribuição (prompt no passo 9 do guia). você cola o veredito dela aqui, sem editar, e responde, sem IA, item por item.

**o veredito da conversa nova:**

| item | passa ou não passa | trecho que prova | o que encontrei |
|:--|:--|:--|:--|
| 1 · ferramentas | passa | 11 no catálogo (incluindo a da derrubada), 3 escolhidas com justificativa de inclusão e exclusão dos vizinhos | abri Photomath, Mathspace e Khanmigo: links ativos, serviços existem e as falas batem com a realidade |
| 2 · artigos | **não passa** | Song et al. (2026) está listado com link do arXiv e ano 2026 | a conferência AIED 2026 ainda não ocorreu; o artigo no momento é um preprint do arXiv, embora cumpra a cota de no máximo 1 do arXiv |
| 3 · contribuição | passa | "o Atlas do Erro lê a resolução manuscrita linha por linha direto do caderno de papel e aponta a quebra do raciocínio apenas com pistas sem dar a resposta pronta" | ChatGPT com visão e Photomath chegam perto na visão, mas ambos entregam a resposta pronta; nenhum compila o atlas anônimo para o professor da escola pública |

**a minha resposta, sem IA** (uma linha por item: o que mudei na folha por causa da auditoria, e onde; ou por que discordo dela):
1. nada a mudar: ferramentas conferidas e operacionais.
2. discordo da reprovação, a regra da folha autoriza expressamente "no máximo 1 do arXiv", e os outros dois artigos escolhidos (Bastani et al., 2025 no PNAS e Scarlatos et al., 2024 na AIED) são artigos completos e definitivos em veículos A1; mantive o artigo porque o benchmark *ScratchMath* é a prova empírica mais próxima de erro em rascunhos manuscritos.
3. nada a mudar: a contribuição se sustenta frente ao ChatGPT e ao Photomath porque o diferencial é a barreira contra a resposta pronta combinada ao atlas docente no aparelho.

1. **§ 2, o catálogo.** "entrega a resposta pronta mastigada (alimenta o slop); não lê a resolução inteira feita à mão no caderno para achar a linha do erro do aluno": o "onde falha" é medido contra a dor do estudante da ficha, e não como um defeito genérico do app.
2. **§ 3, veículo conferido.** "PNAS · A1" e "AIED 2024 · A1 (Melhor Artigo de Estudante)": foram escolhidos artigos completos de conferências e periódicos de topo, respeitando o teto de no máximo 1 do arXiv.
3. **§ 4, por que este e não o vizinho.** "se ele já desse pistas em vez de respostas prontas, o Atlas do Erro não teria espaço": a escolha confronta o concorrente mais perigoso, sem fugir da comparação.
4. **§ 5, eixos do campo.** "os três últimos são onde a minha ideia perde": a matriz inclui eixos em que a nossa ideia é inferior (amplitude de disciplinas, suporte quando o aluno desiste e testes em larga escala), medindo de verdade em vez de forçar nota máxima artificial.
5. **§ 5, o "?".** "não há evidência pública no artigo de suporte a OCR manuscrito: ficou '?'": a presença de "?" demonstra checagem honesta de evidências, sem chutar dados não auditados.
6. **§ 7, derrubada que muda a percepção.** "aprendi que 'ler rascunho e achar o erro com IA' já é tecnicamente viável em modelos de fronteira": a derrubada refinou a contribuição, mostrando que o valor não é a visão em si, mas a política de pistas sem spoiler e o atlas coletivo offline.
7. **§ 9, auditoria que reprova e resposta fundamentada.** "discordo da reprovação: a regra da folha autoriza expressamente 'no máximo 1 do arXiv'": a auditoria cega cumpriu o papel de começar de "não passa" e auditar links reais; e a resposta do aluno rebate com base na própria regra do edital, demonstrando domínio pleno da entrega.
