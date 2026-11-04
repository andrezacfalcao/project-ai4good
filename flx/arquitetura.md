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
    G{{"7 · tipo do erro, de uma lista fixa, e pista sem a resposta (Qwen)"}}
    I(["8 · aluno vê a linha da quebra e a pista, sem a resposta, e tenta de novo"])
    J["9 · se ele pedir, o passo 7 roda de novo, pedindo uma pista mais clara; depois de 3 pistas, a tela chama o professor"]
    K["10 · só a categoria, o exercício e a data entram no atlas, sem nome e sem foto"]
    L["11 · contar os erros mais comuns da turma, por exercício"]
    M(["12 · professor vê o atlas e escolhe a aula de reforço"])

    A --> B --> C --> D --> E --> F --> G --> I
    I -- "pede outra pista" --> J
    J -- "nova pista" --> G
    G --> K --> L --> M
```
