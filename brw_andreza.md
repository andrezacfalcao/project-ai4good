# brw · [Andreza Maria Coutinho Falcão]

> folha do artefato [brainwriting híbrido](../3-brainwriting-hibrido.md). siga o guia passo a passo
> e preencha cada seção aqui. as decisões são suas, e decidir é saber explicar.

## 1 · onde atacar

**crise** (marque 1 com `x`):

| | crise |
|:-:|:--|
| [ x ] | perda do raciocínio crítico e alienação (*slop*) |
| [ ] | a verdade sob mira e colapso epistêmico (*fakes*) |
| [ ] | manipulação política e democracia (*bots*) |
| [ ] | crise ecológica da IA (água e energia) |
| [ ] | alimentação com veneno e ultraprocessados (vs. feiras agroecológicas) |
| [ ] | endividamento e dreno das *bets* |
| [ ] | moradia e especulação (casas vazias) |
| [ ] | concentração de plataformas e trabalho |
| [ ] | outra: [preencha: a crise, e em 1 linha por que é relevante] |

por que esta crise: é a crise que chega primeiro na escola. 73% dos estudantes brasileiros de 15 anos estão abaixo do nível básico em matemática ([PISA 2022, Inep](https://agenciagov.ebc.com.br/noticias/202312/divulgados-os-resultados-do-pisa-2022)), e 70% dos alunos do ensino médio já usam IA generativa nas tarefas escolares ([TIC Educação 2024, Cetic.br](https://canaltech.com.br/mercado/7-em-cada-10-alunos-do-ensino-medio-ja-usam-ia-generativa-em-pesquisas-no-brasil/)): se a IA vira o atalho que resolve a lista, quem já não sabia resolver deixa de tentar.

**tecnologias de IA** (marque 3 e chame de A, B, C):

| | tecnologia de IA |
|:-:|:--|
| [ A ] | modelos locais / no aparelho (*SLMs*, 1B–7B) |
| [ B ] | sistemas multiagente e agência (*tools*, MCP) |
| [ C ] | visão computacional e OCR |
| [ ] | voz (fala ↔ texto) e interfaces sem tela |
| [ ] | grafos e RAG (redes de grafos, busca vetorial) |
| [ ] | modelos de difusão / geração visual |
| [ ] | outra: [preencha] |

**infraestruturas tradicionais** (marque 3 e chame de 1, 2, 3):

| | infraestrutura |
|:-:|:--|
| [ ] | plataformas de dois lados (*matching*, como Uber) |
| [ 1 ] | geolocalização, GPS e mapas |
| [ ] | e-commerce, marketplaces e catálogos |
| [ 2 ] | mensageria leve e bots (WhatsApp, SMS) |
| [ ] | redes sociais, feeds e comunidades |
| [ ] | pagamento instantâneo (Pix, moeda local) |
| [ 3 ] | crowdsourcing e curadoria coletiva |
| [ ] | outra: [preencha] |

## 2 · clichês

| clichê | o que acerta | onde fica raso |
|:--|:--|:--|
| app que resolve o exercício pela foto | entende o problema escrito pelo aluno | entrega a resposta pronta; o aluno copia sem pensar |
| tutor de IA que explica a matéria | personaliza o ensino para cada aluno | o aluno ouve a explicação, mas continua sem tentar sozinho |
| detector de texto feito por IA | reconhece que há trapaça com IA | vira caça ao aluno, erra muito e não ensina ninguém a pensar |
| proibir IA na escola | protege o esforço do aluno | ignora a realidade; o aluno usa escondido em casa |
| plataforma de videoaulas e simulados | conteúdo de qualidade e prática | só mostra se acertou ou errou, nunca onde o raciocínio quebrou |
| dashboard de notas para o professor | dá visão geral da turma | mostra o resultado, não o raciocínio; a nota não diz por que o aluno erra |

## 3 · matriz 3 × 3 e a minha ideia

| | 1 · geolocalização e mapas | 2 · mensageria leve e bots (WhatsApp, SMS) | 3 · crowdsourcing e curadoria coletiva |
|:--|:--|:--|:--|
| **A · modelos locais (SLMs)** | **Caderno Offline** · aluno de escola sem internet fotografa a resolução; o modelo no aparelho aponta onde errou | **Grupo de Estudo Privado** · colegas mandam fotos das resoluções no grupo de WhatsApp da turma; o modelo local remove nomes e rostos antes | **Erro Anônimo** · o erro do aluno é processado no aparelho e só sai anônimo para o atlas coletivo |
| **B · multiagente** | **Rota de Reforço** · agentes encontram, perto do aluno, colegas ou monitores que já superaram o mesmo erro | **Duplas do Erro** · agentes num bot de WhatsApp juntam alunos que erraram de jeitos diferentes para um explicar ao outro | **Professor Avisado** · agentes leem o atlas da turma e propõem ao professor a aula sobre o erro mais comum |
| **C · visão computacional** | **Mapa do Erro** · a visão lê resoluções à mão; erros somados por escola e região formam um mapa nacional da aprendizagem | **Raciocínios no Grupo** · a visão lê as fotos da turma, e o bot manda no grupo caminhos diferentes para o mesmo problema | **Atlas do Erro** · aluno resolve à mão e fotografa; a visão aponta onde o raciocínio quebrou; os erros somados formam um atlas |

**as 9 no mapa impacto × viabilidade:**

| | viabilidade alta | viabilidade baixa |
|:--|:--|:--|
| **impacto alto** | Atlas do Erro, Professor Avisado, Erro Anônimo, Caderno Offline | Mapa do Erro, Duplas do Erro |
| **impacto baixo** | Raciocínios no Grupo, Grupo de Estudo Privado | Rota de Reforço |

por que cada uma está aí:
- **Atlas do Erro** · alto e alta: muda o papel da IA na lista de exercícios, e dá para testar com uma turma e um celular.
- **Professor Avisado** · alto e alta: o professor escolhe a aula pelo erro real da turma; só precisa do Atlas funcionando.
- **Erro Anônimo** · alto e alta: sem privacidade, nenhuma escola adota; o modelo no aparelho já roda offline.
- **Caderno Offline** · alto e alta: alcança a escola sem internet, que é onde a crise é maior.
- **Mapa do Erro** · alto e baixa: mostraria ao país onde os alunos travam, mas exige muitas escolas coletando.
- **Duplas do Erro** · alto e baixa: ensinar o colega fixa o conteúdo, mas combinar horários entre alunos é difícil.
- **Raciocínios no Grupo** · baixo e alta: mostra outros caminhos, mas sozinho não faz o aluno tentar.
- **Grupo de Estudo Privado** · baixo e alta: protege o nome, mas o grupo da turma já existe.
- **Rota de Reforço** · baixo e baixa: pede deslocamento e horário, e a monitoria da escola já faz isso.

**as duas perguntas: o argumento do interesse próprio e a alternativa sem IA:**

| ideia | quem usa ganha, para si | o que custa a ele | o que resolve sem IA avançada | se sustenta? |
|:--|:--|:--|:--|:--|
| Caderno Offline | o aluno sem internet sabe na hora onde errou, sem esperar o professor | ter espaço no celular para o modelo, e uma foto | o gabarito do livro diz se acertou, não onde errou; um verificador algébrico exige digitar tudo | sim |
| Grupo de Estudo Privado | o aluno vê como o colega resolveu sem se expor | uma foto no grupo | o grupo de WhatsApp da turma já existe, e tirar o nome é recortar a foto | **não**: o grupo e um recorte resolvem |
| Erro Anônimo | o aluno usa o Atlas sem medo de o professor ver o erro dele | nada além do Atlas | tirar o nome antes de enviar é uma regra; classificar o erro no aparelho exige o modelo | sim, como parte do Atlas; sozinha não tem ganho |
| Rota de Reforço | o aluno acha ajuda perto de casa | deslocar-se, combinar horário e admitir que não sabe | o plantão de monitoria da escola | **não**: o custo vence o ganho, e a monitoria já existe |
| Duplas do Erro | quem errou ganha explicação de colega | combinar horário; quem explica quase não ganha nada para si | o professor forma duplas olhando as notas | **não**: o ganho de quem explica é fraco |
| Professor Avisado | o professor sabe o erro mais comum da turma sem corrigir 40 cadernos | ler um resumo; depende de os alunos fotografarem | prova de múltipla escolha com alternativas que denunciam o erro, mas só em questão fechada | sim |
| Mapa do Erro | a secretaria de educação sabe onde pôr reforço | convencer as escolas a coletar | SAEB e provas estaduais já mapeiam por escola, mas só acerto e erro, não o raciocínio | sim, mas só depois que o Atlas funcionar numa escola |
| Raciocínios no Grupo | o aluno vê outros caminhos para o mesmo problema | ler as mensagens | o professor fotografa três resoluções e manda no grupo | **não**: o professor faz em 2 minutos |
| Atlas do Erro | o aluno descobre na hora em que linha errou, sem receber a resposta, e chega à prova (onde não há ChatGPT) sabendo que tipo de erro comete | resolver à mão, o que já faz, e uma foto | o gabarito diz só o resultado final; um verificador algébrico acha a linha errada se tudo for digitado, mas não lê o caderno nem diz o tipo do erro | sim |

onde discordei da IA, e por quê: a IA pôs o Atlas do Erro em viabilidade alta sem ressalva. Ler matemática escrita à mão erra muito, principalmente com letra de caderno. para caber no semestre, acho melhor só equações do 1º grau,soma, subtracao, multiplicacao, uma turma, 30 cadernos fotografados, medindo quantas linhas a transcrição acerta e se a linha do erro apontada é a mesma que o professor apontaria. também discordo de o Erro Anônimo ser uma ideia própria, sozinho ele não dá ganho a ninguém, ele é uma camada do Atlas.

**minha ideia escolhida:** Atlas do Erro · o aluno resolve à mão e fotografa, a IA mostra onde o raciocínio quebrou, sem dar a resposta, e os erros de todos formam um atlas que mostra à escola como os alunos pensam.

**por que ela, sem IA, em até 3 linhas:** A ideia é mudar o papel da IA. No Atlas do Erro, o aluno resolve à mão e a IA não entrega a resposta, só aponta em que linha o raciocínio quebrou. Assim, quem pensa e corrige continua sendo o aluno, e o erro vira aprendizado.

## 4 · motores

| motor | nome | frase | o que mudou em relação à ideia |
|:--|:--|:--|:--|
| inverter | O Aluno Corrige a IA | a IA resolve o exercício com um erro escondido, e o aluno precisa encontrar em que linha ela errou | o aluno deixa de ser corrigido e passa a ser quem avalia; desconfiar da IA vira exercício |
| canalizar | Erro que Vale Ponto | o aluno ganha pontos por encontrar e corrigir o próprio erro, não por acertar de primeira | o interesse pela nota passa a recompensar o raciocínio, e não a resposta copiada |
| transplantar | Caixa-Preta da Escola | como na aviação, cada erro é registrado sem punição para que todos aprendam com ele | traz a cultura de segurança da aviação: errar deixa de ser vergonha e vira informação |
| reescalar | Atlas Nacional | os erros de todas as escolas públicas formam uma infraestrutura aberta, como o Pix | de ferramenta de uma turma para mapa da aprendizagem do país, usado por redes e autores de livros |
| trocar a persona | Atlas da EJA | adultos que voltaram a estudar recebem apoio privado, sem a vergonha de errar na frente de outros | foca em quem mais tem medo de errar e menos tempo para estudar |
| trocar o contexto | Atlas da Argumentação | o aluno escreve a redação à mão, e a IA aponta onde o argumento perde a lógica, sem reescrever | sai da matemática e vai para a escrita, onde o slop é ainda mais comum |
| trocar a tecnologia | Pensa Alto | o aluno explica o raciocínio em voz alta, e a IA aponta em que momento a explicação quebrou | troca a foto pela voz; o aluno precisa organizar o pensamento para falar |
| juntar | Erro em Dupla | depois de errar, o aluno é conectado a um colega que já superou o mesmo erro | junta o Atlas com as Duplas do Erro; o colega explica, e os dois aprendem |
| restringir | Uma Pista por Exercício | a IA só pode apontar a linha do erro uma vez; depois, o aluno segue sozinho | limita a ajuda para evitar dependência e obrigar o aluno a pensar |

**o que cada motor mudou, o ganho de quem usa e as duas perguntas:**

| motor | o que foi [invertido, canalizado…], em 1 linha | o que quem usa ganha para si | se sustenta nas duas perguntas? |
|:--|:--|:--|:--|
| inverter | quem corrige quem: antes a IA corrigia o aluno; agora o aluno corrige a IA | treina achar erro, que é o que a prova cobra | sim |
| canalizar | a vontade de tirar nota, que o aluno já tem | recupera parte do ponto perdido | só em parte: depende do professor contar, e nunca pode valer mais que acertar de primeira |
| transplantar | o registro de erro sem punição, da aviação para a escola | erra sem vergonha e sem ser rotulado | sim, como regra do Atlas |
| reescalar | o tamanho: de uma turma para todas as escolas públicas | a rede de ensino sabe onde pôr reforço | sim, mas só depois de funcionar numa escola |
| trocar a persona | saiu o adolescente, entrou o adulto da EJA | estuda no próprio tempo, sem se expor | sim |
| trocar o contexto | da matemática para a redação | sabe onde o argumento falhou antes do ENEM | não por enquanto: falha de argumento é menos objetiva, e não há regra que confira como o SymPy confere a conta |
| trocar a tecnologia | da foto do caderno para a voz | não precisa escrever | não: perde o caderno, onde o raciocínio fica registrado |
| juntar | Atlas do Erro + Duplas do Erro | ganha a explicação de um colega | não: o colega pode dar a resposta, e quem explica ganha pouco |
| restringir | a quantidade de ajuda: uma pista por exercício | não fica dependente da IA | sim |
## 5 · o que fica e o que sai

**o que eu gostei:** do Erro que Vale Ponto (canalizar), porque resolve o incentivo. O aluno passa a querer mostrar o próprio raciocínio, já que é isso que dá nota, e não a resposta copiada. Gostei também da Caixa-Preta da Escola (transplantar), porque muda a forma de ver o erro. Em vez de vergonha, ele vira informação que ajuda todo mundo. Mas o ponto só vale se, depois de identificar o erro, o aluno conseguir corrigir e chegar sozinho à resposta certa.

**o que achei interessante:** no O Aluno Corrige a IA, desconfiar da IA vira exercício. Eu não teria pensado em usar o erro da própria IA para treinar o aluno, e isso ataca o slop de frente. No Atlas Nacional, os erros de uma turma, somados, poderiam servir a quem escreve livro didático, e não só ao professor.

**o que eu descarto, e por quê:** descarto o Pensa Alto (trocar a tecnologia), porque a voz tira a força do caderno, que é onde o raciocínio fica registrado e pode ser lido linha por linha. Descarto o Erro em Dupla (juntar), porque o colega pode acabar dando a resposta pronta, e o foco da ideia é o aluno chegar sozinho à solução. Descarto também o Atlas Nacional por enquanto. Ele é o horizonte da ideia, mas começar pelo país inteiro tornaria o projeto inviável, então faz mais sentido começar por uma escola.

**minha ideia completa:** Atlas do Erro · estudantes resolvem os exercícios à mão e fotografam o caderno. A visão computacional lê o raciocínio linha por linha e, sem dar a resposta, aponta só onde ele quebrou. Corrigir o próprio erro recupera parte do ponto perdido, mas nunca vale mais do que acertar de primeira, então ninguém ganha errando de propósito. Como na caixa-preta da aviação, cada erro é registrado sem punição e, anônimo, forma um atlas que mostra ao professor onde a turma trava. Na crise do slop, a IA deixa de pensar pelo aluno e devolve o raciocínio para ele.

## 6 · refinamento

**a · e se todo mundo usasse?**

o tamanho da crise hoje:
- 73% dos estudantes brasileiros de 15 anos estão abaixo do nível 2 em matemática, o mínimo que a OCDE considera para exercer a cidadania; na média da OCDE são 31% ([PISA 2022, Inep/MEC](https://agenciagov.ebc.com.br/noticias/202312/divulgados-os-resultados-do-pisa-2022)).
- 70% dos alunos do ensino médio com acesso à internet já usam IA generativa nas pesquisas escolares, e só 32% deles receberam orientação da escola sobre como usá-la ([TIC Educação 2024, Cetic.br](https://canaltech.com.br/mercado/7-em-cada-10-alunos-do-ensino-medio-ja-usam-ia-generativa-em-pesquisas-no-brasil/)).
- num experimento com quase mil alunos de ensino médio, quem estudou matemática com o GPT-4 dando a resposta tirou 17% menos na prova sem IA do que quem nunca usou; a versão que dava só pistas, sem a resposta, eliminou essa queda ([Bastani et al., 2025, PNAS](https://ideas.repec.org/a/nas/journl/v122y2025pe2422633122.html)).
- o Brasil tem 7,8 milhões de alunos no ensino médio ([Censo Escolar 2024, Inep/MEC](https://exame.com/brasil/numero-de-alunos-aumenta-no-ensino-medio-mostra-censo-escolar-2024/)).

se todo mundo usasse por 5 anos (a minha aposta):
- se metade dos 7,8 milhões trocasse o ChatGPT que dá a resposta pelo Atlas na lista de exercícios, seriam 3,9 milhões de alunos fazendo a lista sozinhos. pelo estudo de Bastani, só isso já evita a queda de 17% na prova que a IA com resposta pronta causa.
- se cada professor dedicasse uma aula por semana ao erro mais comum da turma, aposto que a parcela abaixo do nível 2 no PISA cairia de 73% para 65% em 5 anos. é uma hipótese minha, que parte do dado do PISA e não foi medida.
- pela primeira vez, a rede de ensino saberia, por escola, qual erro trava os alunos, e não só a nota.
- de onde vem a metade: o aluno não precisa trocar de ferramenta sozinho. quem adota é o professor, que passa a lista pelo Atlas porque deixa de corrigir cadernos à mão; metade é a minha aposta de quantos professores de matemática fariam isso em 5 anos. o 70% da TIC mede uso de IA, não cópia; o que liga a resposta pronta à perda de aprendizagem é o estudo de Bastani.


Se todo mundo usasse, a IA deixaria de ser o atalho que pensa pelo aluno e passaria a ser o que torna o raciocínio dele visível. Milhões de estudantes voltariam a tentar antes de pedir ajuda, e as escolas saberiam, pela primeira vez, onde seus alunos realmente travam. O incentivo é individual, e não depende da nota.

por que cada pessoa usaria: o aluno, porque descobre na hora em que linha errou, sem esperar a correção do professor, e chega à prova, onde não tem ChatGPT, sabendo que tipo de erro comete; copiar a lista do ChatGPT não o prepara para isso. o professor, porque deixa de corrigir 40 cadernos à mão e já sabe qual erro levar para a aula. se a escola quiser dar nota, a correção só recupera parte do ponto perdido e nunca vale mais que acertar de primeira, então errar de propósito não compensa.

a pista funciona sem o atlas: quem não quiser contribuir não envia nada, e o atlas só recebe o tipo do erro de quem aceitar.

**b · a IA que não pode faltar.** técnica: visão computacional para reconhecimento de escrita à mão (OCR de manuscritos e de expressões matemáticas), que transcreve a resolução linha por linha para que um modelo de linguagem verifique cada passo · aula da disciplina: aula 07 · redes convolucionais (arquiteturas de deep learning 1/4), para ler a escrita à mão, e aula 11 · transformers, para o modelo que lê a transcrição e escreve a pista

por que sem ela não roda: sem a visão, o aluno teria que digitar a resolução, e o caderno, onde o raciocínio acontece, ficaria de fora. Digitar também facilita copiar uma resposta pronta. É a visão que permite ler o caminho que o aluno fez à mão, linha por linha, e apontar exatamente onde ele quebrou.

o que a IA faz que um verificador de passos algébricos sem IA não faz: um verificador simbólico (como o SymPy) compara duas linhas e diz se são equivalentes, e eu uso ele: a conferência da conta é feita por regra. Mas ele (1) não lê o caderno: o aluno teria que digitar tudo em formato de computador, que é o que a ideia quer evitar; (2) diz que a linha 3 está errada, mas não diz por quê (o aluno trocou o sinal ao passar o termo, ou cortou uma parcela de uma soma), e sem o tipo do erro não há pista nem atlas; (3) não entende problema escrito em palavras, em que o erro está em montar a equação, não em resolvê-la. A IA faz essas três coisas; a regra faz a conta.

**onde e como a IA entra, passo a passo:**

| passo | o que acontece | quem faz | IA ou regra? |
|:--|:--|:--|:--|
| 1 | o aluno resolve a lista à mão, no caderno, em casa ou na sala | aluno | nada |
| 2 | fotografa a página, no próprio celular ou no celular da turma | aluno | nada |
| 3 | a visão lê a escrita à mão e transcreve cada linha como expressão matemática | visão computacional (C): rede convolucional + transformer de OCR | **IA** |
| 4 | o aluno confere a transcrição e corrige o que foi mal lido | aluno | nada |
| 5 | o verificador compara cada linha com a anterior e acha a primeira que não é equivalente | SymPy | regra |
| 6 | o modelo diz o tipo do erro (sinal trocado, distributiva, corte errado) e escreve uma pista, sem a resposta | modelo de linguagem pequeno no aparelho (A) | **IA** |
| 7 | o aluno tenta de novo; se pedir, ganha uma pista um pouco mais clara; depois de 3 pistas, o professor é avisado | aluno e regra | regra |
| 8 | só o tipo do erro, sem nome e sem foto, sai do aparelho para o atlas da turma | regra de anonimização | regra |
| 9 | o professor vê os erros mais comuns da turma e escolhe a aula | contagem e professor | regra |

a IA só entra onde uma regra não dá conta: ler o caderno (passo 3) e dizer por que a linha está errada sem entregar a resposta (passo 6). o resto é regra, para ficar barato e conferível.

o que provaria que a IA não é necessária: se no teste com uma turma os alunos digitarem a resolução tão rápido quanto fotografam, e uma lista fixa de regras disser o tipo do erro tão bem quanto o modelo, eu retiro a IA e fico com o verificador simbólico.

**o que já existe e onde para:** o Photomath lê o exercício pela foto, mas entrega a solução inteira (é o primeiro clichê do § 2); o Mathpix transcreve matemática escrita à mão, mas não diz onde nem por que o aluno errou; o SymPy confere a conta, mas só com tudo digitado. nenhum lê o caderno e devolve só a pista.

**como o piloto mede cada parte (uma turma, 30 cadernos):**

| o que pode falhar | como medir | passa se |
|:--|:--|:--|
| leitura | quantas linhas a visão transcreve certo | 90% das linhas, depois da conferência do aluno |
| localização | a linha apontada é a mesma que o professor aponta? | 8 em cada 10 cadernos |
| diagnóstico | o tipo do erro bate com o do professor? comparar o modelo com uma lista fixa de regras, nos mesmos cadernos | o modelo acerta mais que as regras; se não, sai o modelo |
| pista | o professor julga se cada pista está certa e não entrega a resposta | nenhuma pista errada ou com a resposta; se houver, as pistas viram uma lista escrita pelo professor |
| aparelho | tempo entre a foto e a pista no celular da turma (modelo de 1B a 3B, que ocupa de 1 a 2 GB) | até 10 segundos; se não, a pista roda no computador da escola |

**c · o cético e as saídas**

| crítica | saída 1 | saída 2 | minha decisão |
|:--|:--|:--|:--|
| "o aluno pode copiar a resposta do ChatGPT no caderno e só fotografar" | o que vale nota é a prova, sem celular; na lista, a correção só recupera parte do ponto perdido | o sistema compara a tentativa original com a correção e o tempo entre as duas | saída 1, porque quem copia a lista não ganha o que importa para ele, que é saber o próprio erro antes da prova, e errar de propósito nunca rende mais que acertar |
| "a IA pode ler a letra errado ou apontar um erro onde não existe" | o aluno confere a transcrição antes da análise | o aluno pode contestar a indicação, e o professor revisa as contestações | as duas, porque contestar a IA também é pensamento crítico |
| "registrar erros pode expor ou rotular alunos, e são dados de menores" | o modelo roda no aparelho, e o erro só sai anônimo | o professor vê apenas os padrões da turma, nunca um ranking individual | as duas, porque sem confiança nenhuma escola adotaria a ideia |
| "o aluno pode travar, se frustrar e desistir" | a IA dá uma pista por vez, cada uma um pouco mais clara | depois de algumas tentativas, o professor é avisado para ajudar | saída 2, porque mantém a IA sem dar a resposta e devolve o papel ao professor |
| "muitas escolas públicas não têm internet nem um celular por aluno" | o modelo funciona offline, no próprio aparelho | um único celular por turma, usado pelo professor para fotografar os cadernos | as duas, começando por um celular por turma no protótipo |

## 7 · resumo, sem IA

A crise é o uso frequente da IA para ver as respostas das questões prontas, o que faz muitos alunos não conseguirem resolver nada sozinhos. No Atlas do Erro, o aluno resolve à mão e fotografa o caderno, e a IA lê a resolução e mostra onde ele errou, dando pistas para ele testar e forçar a cabeça, sem entregar a resposta. Se os alunos passassem a usar a IA desse jeito, e menos do jeito mais "fácil", desenvolveriam um pensamento crítico melhor. Cada aluno usaria porque descobre na hora onde errou e chega preparado à prova, onde não há IA para copiar, e o professor, porque passa a ver onde a turma trava.
