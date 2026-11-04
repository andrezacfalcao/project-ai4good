# Atlas do Erro · fluxograma e arquitetura

O caminho de uma resolução, do caderno do aluno até a pista que volta para ele e o atlas que
volta para o professor. Artefato **fluxograma e arquitetura** (`flx`) da disciplina AI4Good;
a folha está em [flx.md](flx.md).

Formas: **pessoa** `([ ])` · **IA** `{{ }}` · **regra** `[ ]`. Caixas: onde cada peça roda.

```mermaid
flowchart TD
    subgraph PAPEL["caderno do aluno, em papel"]
        A(["1 · aluno resolve a lista à mão, no caderno"])
    end

    subgraph CEL["celular da turma, usado pelo professor: tudo roda aqui, sem internet"]
        B(["2 · professor fotografa a página no celular da turma"])
        C["3 · separar a foto em linhas, pelos vãos entre as linhas escritas"]
        D{{"4 · transcrever cada linha (TrOCR)"}}
        E(["5 · aluno confere a transcrição na tela e corrige o que foi mal lido"])
        F["6 · achar a primeira linha que não é equivalente à anterior (SymPy)"]
        G["7 · tipo do erro: testar no SymPy as correções típicas; a que devolve a equivalência dá a categoria; nenhuma vira 'outro'"]
        P[("lista de pistas escrita pelo professor")]
        H["8 · pista: a primeira da lista do professor para a categoria"]
        I(["9 · aluno vê a linha da quebra e a pista, sem a resposta, e tenta de novo"])
        J["10 · se ele pedir, a próxima pista da lista; depois de 3, ou em 'outro', a tela chama o professor"]
        K["11 · só a categoria, o exercício e a data entram no atlas, sem nome e sem foto"]
        DB[("atlas da turma: categoria, exercício e data")]
        L["12 · contar os erros mais comuns da turma, por exercício"]
        M(["13 · professor vê o atlas e escolhe a aula de reforço"])
    end

    A -- "a página, mostrada ao professor" --> B
    B -- "foto, só na memória do app" --> C
    C --> D --> E --> F --> G --> H --> I
    P --> H
    P --> J
    I -- "pede outra pista" --> J
    J --> I
    G --> K --> DB --> L --> M
```

## os dados

| dado pessoal | de quem é | onde fica | quem vê | por quanto tempo |
|:--|:--|:--|:--|:--|
| foto da página (a letra do aluno, e o nome, se estiver escrito no caderno) | aluno | memória do app, no celular da turma; não vai para a galeria | aluno e professor, na tela | até o aluno conferir a transcrição (passo 5); o app apaga |
| transcrição das linhas | aluno | memória do app | aluno e professor, na tela | até o fim do exercício |
| nome do aluno | aluno | não é guardado | ninguém | nunca é registrado |
| categoria do erro, exercício, data e número de pistas pedidas | da turma, sem nome | atlas, no celular da turma | professor | até o fim do bimestre; depois, fica só a contagem por categoria |

Nada sai do celular da turma. A foto é tirada pela câmera do próprio app e não passa pela
galeria, para não entrar no backup automático do celular.
