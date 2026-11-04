# sem1 · Andreza Maria Coutinho Falcão

> roteiro do [seminário · preliminares](https://lucassf.pages.dev/ai4good/artefatos/4-seminario-preliminares.md). de 4 a 6 slides, de 3 a 5
> minutos. em cada slide: o que aparece, o que você fala, e quanto tempo leva.

**link dos slides:** [sem1.pptx](https://github.com/andrezacfalcao/project-ai4good/blob/main/sem1/sem1.pptx), com a fala de cada slide nas notas do apresentador. Gerado por [gerar_slides.js](gerar_slides.js).

## as quatro frases, sem IA

1. **a ideia:** o aluno usa a IA para pegar a resposta da lista pronta e chega na prova sem saber fazer; no Atlas do Erro ele resolve à mão, tira foto, e a IA mostra só a linha onde o raciocínio quebrou, com uma pista, sem dar a resposta.
2. **o produto mais próximo:** o Photomath, porque é o que o aluno já usa: lê a conta pela câmera, até escrita à mão, mas entrega a solução inteira e lê o exercício, não a resolução do aluno.
3. **o artigo mais próximo:** "Can MLLMs Read Students' Minds?" (Song et al., AIED 2026), porque é o único que pede a modelos para achar o erro em rascunhos à mão de alunos de verdade, e mostrou que eles ficam longe dos especialistas, principalmente ao ler a letra.
4. **o que só a minha faz:** lê o caderno de papel e dá só a pista, no próprio aparelho, sem internet; e pergunta se um sistema pequeno e local acha a linha do erro como o professor, em 8 de cada 10 resoluções. No piloto, com imagens de teste, a resposta foi não: 72%.

## slide 1 · a ideia · 45 s

- **aparece:** "O aluno resolve. A IA aponta onde quebrou." À esquerda, a foto de teste do caderno com a linha 2 marcada de vermelho; à direita, o protótipo rodando, com a categoria, a pista e a conferência com o gabarito.
- **eu falo:** "Pensa num aluno do sétimo ano fazendo a lista de equação em casa. Ele trava numa conta, tira foto com o Photomath ou com o ChatGPT, e a resposta aparece pronta. Ele copia e entrega. Só que na prova não tem IA, e aí ele não sabe fazer. E isso já foi medido: num estudo com quase mil alunos do ensino médio, quem estudou com a IA dando a resposta tirou 17% menos na prova sem a IA. O Atlas do Erro faz o contrário. O aluno continua resolvendo no caderno, à mão. Ele tira uma foto, a IA lê a resolução linha por linha e mostra só onde o raciocínio quebrou, com uma pista. A resposta ela não dá. Aqui é o protótipo rodando de verdade. Ele achou o erro na linha 2, o sinal trocado quando o 4 passou para o outro lado, e a pista só manda revisar o sinal. Quem corrige é o aluno."

## slide 2 · o produto mais próximo · 45 s

- **aparece:** "Photomath: lê a foto e entrega a resposta." A imagem oficial do app, com a câmera lendo 3x + 4 = 8 ([photomath.com](https://photomath.com/)), e três linhas: ✓ lê a conta pela câmera, até escrita à mão; ✕ entrega a solução inteira; ✕ lê o exercício, não a resolução do aluno.
- **eu falo:** "O produto que chega mais perto é o Photomath, que hoje é do Google. Escolhi ele porque é o que o aluno já usa: aponta a câmera para a conta e ele lê na hora, e lê bem, até letra à mão. O problema é o que ele faz depois. Ele resolve a conta inteira, passo a passo. Ele lê o exercício, não o que o aluno escreveu. Então ele não diz em que linha o aluno errou, ele mostra o caminho certo pronto. Para quem quer aprender, isso é a resposta pronta de novo. Eu também tentei derrubar a minha ideia com o ChatGPT com visão. Ele até acha o erro se você pedir, mas se o aluno insistir, ele dá o resultado. E os dois mandam a foto para a nuvem."

## slide 3 · o artigo mais próximo · 45 s

- **aparece:** "O artigo mais próximo: ScratchMath." A primeira página do artigo, o título "Can MLLMs Read Students' Minds? Unpacking Multimodal Error Analysis in Handwritten Math", Song et al., AIED 2026, artigo completo nos anais (LNCS, páginas 110 a 124), [doi.org/10.1007/978-3-032-29744-0_8](https://doi.org/10.1007/978-3-032-29744-0_8), e três números: 1.720 rascunhos à mão, 16 modelos, longe dos especialistas.
- **eu falo:** "Na ciência, o mais próximo é esse artigo da AIED deste ano, que é uma das conferências principais de IA na educação. É artigo completo. Eles juntaram 1.720 rascunhos de verdade, feitos à mão por alunos do fundamental na China, e pediram para 16 modelos explicarem e classificarem o erro de cada um. É quase a minha tarefa. E o resultado é que os modelos ficaram bem longe dos especialistas, e o pior foi justamente ler a letra e seguir o raciocínio do aluno. Os modelos abertos, que são os que dariam para rodar num celular, foram os mais fracos. Para mim isso é um alerta: ler o caderno é o ponto fraco. E foi exatamente onde o meu piloto quebrou, como eu mostro agora."

## slide 4 · o que só a minha faz · 60 s

- **aparece:** "O que só o Atlas faz, e a pergunta." Dois cartões: "para o aluno: lê o caderno de papel e dá só a pista, no próprio aparelho, sem internet" e "para a ciência: um sistema pequeno, local, acha a linha do erro como o professor, em 8 de cada 10?". Ao lado, os números do piloto: 72%, abaixo da meta de 80%, e a leitura caindo de 90% para 64% das linhas com a pauta ([exp.md](../exp/exp.md), § 2.4).
- **eu falo:** "Nenhum trabalho que eu achei faz as três coisas juntas: ler o caderno de papel, apontar só a linha que quebrou sem dar a resposta, e rodar no próprio aparelho, sem mandar a foto do aluno para fora. Esse é o diferencial para o aluno. A pergunta científica é essa: um sistema pequeno, rodando local, acha a linha do erro como o professor acharia, em pelo menos 8 de cada 10 resoluções? E a resposta pode ser não. No meu piloto, com 60 resoluções de teste, ele achou em 72%, abaixo da meta. Com a folha pautada, a leitura caiu de 90% para 64% das linhas. E o modelo que dá o tipo do erro chamou tudo de troca de sinal. Então, hoje, com imagem de teste, a resposta é não. É por isso que o experimento com caderno de verdade importa."

## slide 5 (opcional) · o fecho · 15 s

- **aparece:** em fundo escuro, "A IA não pensa pelo aluno. Ela mostra onde ele parou.", com a mesma foto do caderno e a linha 2 marcada.
- **eu falo:** "Então é isso. O Photomath e o ChatGPT pensam pelo aluno. O Atlas devolve o raciocínio para ele: mostra onde ele parou, e quem termina a conta continua sendo o aluno."

**tempo total, cronometrado:** [cronometrar duas vezes em voz alta; a estimativa é de 3 min 30 s]

## ensaio cético

**a pergunta mais difícil:** [rodar o prompt do passo 3 do guia numa conversa nova e responder de cabeça]

**o que eu mudei por causa dela:** [preencher depois do ensaio]
