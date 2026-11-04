# Atlas do Erro · fluxograma e arquitetura

O caminho de uma resolução, do caderno do aluno até a pista que volta para ele e o atlas que
volta para o professor. Artefato **fluxograma e arquitetura** (`flx`) da disciplina AI4Good;
a folha está em [flx.md](flx.md).

Formas: **pessoa** `([ ])` · **IA** `{{ }}` · **regra** `[ ]`.

```mermaid
flowchart TD
    A(["1 · aluno resolve a lista à mão, no caderno"])
    B(["2 · professor fotografa a página no celular da turma"])
    C["3 · separar a foto em linhas, pelos vãos entre as linhas escritas"]
    D{{"4 · transcrever cada linha (TrOCR)"}}
    E(["5 · aluno confere a transcrição na tela e corrige o que foi mal lido"])
    F["6 · achar a primeira linha que não é equivalente à anterior (SymPy)"]
    G["7 · tipo do erro: testar no SymPy as correções típicas; a que devolve a equivalência dá a categoria; nenhuma vira 'outro'"]
    H["8 · pista: a primeira da lista do professor para a categoria"]
    I(["9 · aluno vê a linha da quebra e a pista, sem a resposta, e tenta de novo"])
    J["10 · se ele pedir, a próxima pista da lista; depois de 3, ou em 'outro', a tela chama o professor"]
    K["11 · só a categoria, o exercício e a data entram no atlas, sem nome e sem foto"]
    L["12 · contar os erros mais comuns da turma, por exercício"]
    M(["13 · professor vê o atlas e escolhe a aula de reforço"])

    A --> B --> C --> D --> E --> F --> G --> H --> I
    I -- "pede outra pista" --> J
    J --> I
    G --> K --> L --> M
```
