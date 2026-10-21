# Roteiro de fala · CP02 (ModernTCN)

Um bloco por slide, em ordem. O mesmo texto está nas notas do `cp02_slides.pptx`.

## 1 · Abertura

Esta é a CP02: reproduzir um modelo de aprendizado profundo da literatura e modificar a arquitetura dele. Escolhi o ModernTCN, um artigo do ICLR de 2024. Vou mostrar que consegui reproduzir os resultados do artigo, qual modificação testei e, principalmente, que ela não melhorou o modelo, e por quê.

## 2 · O artigo base: ModernTCN

O artigo é o ModernTCN, de Luo e Wang, publicado no ICLR 2024. É uma rede convolucional pura, e atende ao que a atividade pede: é de 2024, dentro do exigido (2023 em diante), usa CNN e tem código aberto sob licença MIT. Os autores publicam os scripts com todos os hiperparâmetros, e a base de dados é pública. Isso importa porque só assim dá para reproduzir de verdade. Eu tentei antes com outro artigo, o HCBiLSTM, mas ele não publica código, então troquei.

## 3 · Como o ModernTCN funciona

A tarefa é prever as próximas 96 horas de sete medições de um transformador elétrico, olhando as 336 horas anteriores. O modelo corta cada medição em 84 pedaços, os patches. Cada pedaço passa por um bloco com três partes: uma convolução com kernel grande, de 51 passos, que olha bem para trás; uma rede que mistura as características de cada variável; e outra que mistura as variáveis entre si. No fim, uma camada linear dá a previsão. O ponto-chave é que esses filtros de kernel grande são fixos: tratam toda entrada do mesmo jeito.

## 4 · Reprodução: o artigo fecha

Primeiro reproduzi o baseline, sem mudar nada: usei o código oficial com o comando exato do artigo, para a base ETTh2 e horizonte de 96 horas, com as cinco sementes que o artigo usa. O artigo reporta erro quadrático médio de 0,263. Eu obtive 0,2645, com desvio de 0,0006. A diferença é de 0,0015, menos de 1 por cento. Isso é uma boa notícia: significa que o código e o protocolo estão certos, e que qualquer diferença depois vem da minha modificação. Fiz só dois ajustes de compatibilidade, que não mudam o modelo: uma função do NumPy 2 e o uso da GPU do Mac.

## 5 · A modificação: atenção sobre patches

A minha hipótese é que, como os filtros convolucionais são fixos, uma camada de atenção poderia deixar o modelo ponderar o passado conforme a entrada, o que ajudaria numa série que muda ao longo do tempo. Então acrescentei, no fim de cada bloco, uma auto-atenção sobre os patches. Para não estragar o modelo, o ganho dessa camada, o gamma, começa em zero. Assim, no início, o modelo é idêntico ao oficial, e qualquer diferença nos resultados foi aprendida. Eu testei isso: com gamma igual a zero, a saída é exatamente a mesma. A mudança custa 22 mil parâmetros a mais, 3,4 por cento.

## 6 · Resultado: a atenção não ajudou

Aqui está a comparação, com as mesmas cinco sementes e o mesmo protocolo. O modelo modificado teve erro um pouco maior que o baseline: 0,2654 contra 0,2645. A diferença é pequena, mas consistente: em quatro das cinco sementes o modificado foi pior, e na outra empatou. Ou seja, a hipótese não se confirmou. Isso é um resultado negativo, e a atividade pede modificar, retreinar e medir, não que a modificação melhore.

## 7 · Por quê? O modelo ignorou a atenção

Para entender por que, olhei o gamma que o modelo aprendeu. Ele partiu de zero e ficou em torno de 0,02, com sinal ora positivo, ora negativo: a rede quase não usou a atenção. Por isso as previsões dos dois modelos são quase idênticas. Janela a janela, o modificado só vence em 39,9 por cento dos casos. Nesta figura, a temperatura do óleo em três janelas reais do teste: a que a modificação mais ajuda, a que mais atrapalha, e a pior do baseline. As duas curvas acertam o ciclo diário, o formato, mas erram o nível, e erram igual.

## 8 · O erro é de nível, não de formato

Por variável, o erro muda muito pouco com a modificação: as mais difíceis são MULL e HUFL, e nenhuma muda mais de 0,003. Também vi que 4 por cento das janelas concentram o erro, e nelas os dois modelos dão o mesmo resultado, cerca de quatro vezes pior que nas demais. Minha interpretação, que é uma hipótese e eu não testei, é que existe uma mudança de regime entre o período de treino e o de teste. Se for isso, o limite está nos dados, e não na capacidade do modelo, que é o que a atenção acrescentaria.

## 9 · Conclusão

Em resumo: reproduzi o ModernTCN com erro de menos de 1 por cento em relação ao artigo. A modificação com atenção não melhorou o modelo, e eu consegui mostrar por quê: o ganho aprendido ficou perto de zero. Como limitações: testei uma base e um horizonte, e a modificação tem um único desenho. Como próximos passos, testar outras bases e horizontes, e atacar a mudança de nível com técnicas de normalização adaptativa.

## 10 · O que a atividade pede e onde está

Para fechar, o que a atividade pede e onde está cada evidência no repositório. A pasta tem o CONTEXT ponto md; os dados são os do artigo; o baseline roda com um script e tem log por semente; e a modificação está marcada no código, com um arquivo de diferenças que mostra exatamente o que mudou em relação ao oficial. O relatório em LaTeX está no Overleaf, com trabalhos relacionados, tabela comparativa e análise qualitativa.
