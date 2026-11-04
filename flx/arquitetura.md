# Atlas do Erro · fluxograma e arquitetura

O caminho de uma resolução, do caderno do aluno até a pista e a nota que voltam para ele e o
atlas que volta para o professor. Artefato **fluxograma e arquitetura** (`flx`) da disciplina
AI4Good; a folha está em [flx.md](flx.md).

Formas: **pessoa** `([ ])` · **IA** `{{ }}` · **regra** `[ ]`.

```mermaid
flowchart TD
    A(["1 · aluno resolve a lista à mão, no caderno"])
    B(["2 · professor fotografa a página no celular da turma"])
    C["3 · separar a foto em linhas, pelos vãos entre as linhas escritas"]
    D{{"4 · transcrever cada linha (TrOCR)"}}
    E(["5 · aluno confere a transcrição, corrige e apaga o que não é conta, como o nome"])
    F["6 · achar a primeira linha que não é equivalente à anterior (SymPy)"]
    G{{"7 · tipo do erro, de uma lista fixa, e pista sem a resposta (Qwen)"}}
    H(["8 · aluno vê a quebra, a categoria e a pista; pode contestar e escolhe se entra no atlas"])
    I(["9 · professor confirma ou troca a categoria contestada"])
    J["10 · outra pista: o passo 7 roda de novo, mais claro; depois de 3, chama o professor"]
    K(["11 · professor atende o aluno na carteira"])
    L(["12 · aluno corrige no caderno; nova foto"])
    N["13 · nota: corrigir recupera parte do ponto, nunca mais que acertar de primeira"]
    O["14 · ao fechar o exercício, uma entrada no atlas: categoria final, exercício e semana, só de quem aceitou"]
    P["15 · contar os erros mais comuns da turma, por exercício"]
    Q(["16 · professor vê só a contagem e escolhe a aula de reforço"])

    A --> B --> C --> D --> E
    E -- "foto ilegível" --> B
    E --> F
    F -- "sem quebra" --> N
    F -- "quebra" --> G --> H
    H -- "contesta" --> I --> H
    H -- "pede outra pista" --> J
    J -- "nova pista" --> G
    J -- "3 pistas" --> K --> L
    H -- "tenta de novo" --> L
    L --> B
    N --> O --> P --> Q
```
