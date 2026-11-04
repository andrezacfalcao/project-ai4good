# Atlas do Erro · fluxograma e arquitetura

O caminho de uma resolução, do caderno do aluno até a pista e a nota que voltam para ele e o
atlas que volta para o professor. Artefato **fluxograma e arquitetura** (`flx`) da disciplina
AI4Good; a folha está em [flx.md](flx.md).

Formas: **pessoa** `([ ])` · **IA** `{{ }}` · **regra** `[ ]`. Caixas: onde cada peça roda.

```mermaid
flowchart TD
    subgraph PAPEL["caderno do aluno, em papel"]
        A(["1 · aluno resolve a lista à mão, no caderno"])
    end

    subgraph CEL["celular da turma, usado pelo professor: sem internet nem servidor"]
        B(["2 · professor fotografa a página no celular da turma"])
        C["3 · separar a foto em linhas, pelos vãos entre as linhas escritas"]
        D{{"4 · transcrever cada linha (TrOCR)"}}
        E(["5 · aluno confere a transcrição, corrige e apaga o que não é conta, como o nome"])
        F["6 · achar a primeira linha que não é equivalente à anterior (SymPy)"]
        G{{"7 · tipo do erro, de uma lista fixa, e pista sem a resposta (Qwen)"}}
        H(["8 · aluno vê a quebra, a categoria e a pista; pode contestar e escolhe se entra no atlas"])
        I(["9 · professor confirma ou troca a categoria contestada"])
        J["10 · outra pista: o passo 7 roda de novo, mais claro; depois de 3, ou de 2 leituras ilegíveis, chama o professor"]
        L(["12 · aluno corrige no caderno; nova foto"])
        N["13 · nota: corrigir recupera parte do ponto, nunca mais que acertar de primeira"]
        O["14 · ao fechar o exercício, uma entrada no atlas: categoria final, exercício e semana, só de quem aceitou"]
        DB[("atlas da turma: categoria final, exercício e semana")]
        P["15 · contar os erros mais comuns da turma, por exercício"]
        Q(["16 · professor vê só a contagem e escolhe a aula de reforço"])
    end

    subgraph SALA["sala de aula"]
        K(["11 · professor atende o aluno na carteira"])
    end

    subgraph NB["plano B, só se a foto à pista passar de 10 s no celular: notebook da escola, na rede local"]
        NB1["passos 4 a 7, na memória do programa, sem gravar em disco"]
    end

    A -- "a página, mostrada ao professor" --> B
    B -- "foto, só na memória do app" --> C
    C --> D --> E
    E -- "foto ilegível" --> B
    E -- "2 leituras ilegíveis seguidas" --> K
    E --> F
    F -- "sem quebra" --> N
    F -- "quebra" --> G --> H
    H -- "contesta" --> I --> H
    H -- "pede outra pista" --> J
    J -- "nova pista" --> G
    J -- "3 pistas" --> K --> L
    H -- "tenta de novo" --> L
    L --> B
    N --> O --> DB --> P --> Q
    C -. "plano B: foto e linhas, por Wi-Fi cifrado" .-> NB1
    NB1 -. "pista" .-> H
```

## os dados

| dado pessoal | de quem é | onde fica | quem vê | por quanto tempo |
|:--|:--|:--|:--|:--|
| foto da página (a letra do aluno, e o nome, se estiver escrito no caderno) | aluno | memória do app, no celular da turma, sem passar pela galeria; no plano B, memória do programa no notebook | aluno e professor, na tela | até o aluno conferir a transcrição (passo 5); o app apaga |
| transcrição das linhas | aluno | memória do app e do Qwen | aluno e professor, na tela | até o exercício fechar; o nome escrito no caderno é apagado pelo aluno no passo 5 |
| categoria, pista e contestação | aluno | memória do app | aluno e professor, na tela | até o exercício fechar; só a categoria final vai para o atlas |
| nome do aluno | aluno | não é guardado | ninguém | nunca é registrado |
| entrada no atlas: categoria final, exercício e semana | da turma, sem nome | atlas, no celular da turma | professor, só a contagem | até o fim do bimestre; só de quem aceitou |

No caminho principal, nada sai do celular da turma, e o app desliga o backup automático dos
próprios dados. No plano B, a foto e as linhas vão pelo Wi-Fi da escola, cifradas, até o notebook,
ficam só na memória do programa e não vão para a internet.
