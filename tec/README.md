# tec · tecnologia base demonstrável

Artefato do **Atlas do Erro**, separado das outras atividades da disciplina.

Esta é a única pasta ativa do artefato `tec`. A folha anterior foi preservada
no [histórico do Git](https://github.com/andrezacfalcao/project-ai4good/blob/928e765/va2/tec.md);
para executar, editar ou entregar, use os arquivos desta pasta.

**Folha da entrega:** [tec.md](tec.md). **Mudanças no código:** [ALTERACOES.md](ALTERACOES.md).

**Pesquisa adicional:** [LAYA e alternativas](alternativas.md), com
[experimento local separado](experimentos/laya/README.md). Em dez transições
sintéticas com diagnóstico do SymPy, LAYA acertou 4 categorias e Qwen, 6.
Esses ensaios exploratórios ainda não sustentam adoção autônoma do classificador.

## Rodar agora nesta máquina

Na raiz do repositório:

```bash
HF_HUB_OFFLINE=1 ./tec/rodar.sh oficial
HF_HUB_OFFLINE=1 ./tec/rodar.sh adaptado
```

O script prefere `tec/.venv/`; nesta máquina, enquanto esse ambiente não for
criado, usa o ambiente já existente em `.venv/` na raiz. Os pesos do TrOCR e
do Qwen já estavam disponíveis localmente durante a verificação.

O modo adaptado requer o Ollama rodando em `localhost:11434` com `qwen2.5:1.5b`.
As três imagens incluídas são **sintéticas**, não fotos de estudantes.

## Instalar em outro ambiente

Instale o [uv](https://docs.astral.sh/uv/) e o [Ollama](https://ollama.com/download). Na raiz do repositório:

```bash
cd tec
uv venv --python 3.14.6 .venv
uv pip install --python .venv/bin/python -r requirements.txt
```

Em outro terminal, se o aplicativo Ollama ainda não estiver em execução:

```bash
ollama serve
```

De volta à pasta `tec/`:

```bash
ollama pull qwen2.5:1.5b
./rodar.sh oficial
./rodar.sh adaptado
```

A primeira execução do OCR baixa os pesos. As versões do `requirements.txt` são
as do ambiente que executou esta demonstração, registrado em
[resultados/ambiente.json](resultados/ambiente.json). Em 04/11/2026, uma
instalação limpa com uv no Linux (WSL2, Python 3.14.6) mostrou que faltavam
`sentencepiece` e `protobuf` para carregar o tokenizador; ambos foram
acrescentados. Com eles, `./rodar.sh oficial` reproduziu a mesma saída do Mac.
No modo adaptado, com o mesmo digest do `qwen2.5:1.5b` e o Ollama 0.32.1, o
TrOCR e o SymPy repetiram as linhas e diagnósticos do Mac, mas as categorias e
dicas do Qwen mudaram e variaram entre duas execuções seguidas na mesma máquina,
apesar de `temperature: 0`. A variação acompanha o estado do modelo no Ollama,
recém-carregado ou já usado; fixar `seed` não a eliminou. A saída do Qwen
registrada é uma amostra, não um resultado reproduzível. Evidências em
[resultados/linux-2026-11-04/](resultados/linux-2026-11-04/README.md).

## Exemplo oficial

Origem: [model card do TrOCR-small-printed](https://huggingface.co/microsoft/trocr-small-printed#how-to-use).
O carregamento, processamento, geração e decodificação seguem o exemplo oficial.
A imagem IAM do exemplo foi disponibilizada localmente e a transcrição é impressa
no terminal. O checkpoint é voltado a texto impresso; este teste não comprova
reconhecimento de matemática manuscrita.

O arquivo [exemplo_oficial.py](exemplo_oficial.py) preserva a versão anterior
à adaptação. Os commits `ae9a9b4` e `abf1638` mostram os dois passos.

O código original é distribuído sob a [licença MIT da Microsoft](https://github.com/microsoft/unilm/blob/master/LICENSE).
Veja a cópia em `licencas/unilm-MIT.txt`.

## Estrutura e evidências

```text
tec/
├── README.md                 # entrada para quem abre o link da pasta
├── tec.md                    # folha da atividade e pendências de autoria
├── exemplo_oficial.py        # exemplo anterior à adaptação
├── ler_caderno.py            # entrada e saída do Atlas do Erro
├── rodar.sh                  # comando para executar ambos
├── requirements.txt         # dependências próprias deste artefato
├── a01-122-02-00.jpg          # imagem do exemplo oficial
├── cadernos/                 # três entradas sintéticas e sua descrição
├── resultados/               # stdout/stderr reais, ambiente e diff
├── licencas/                 # aviso MIT do código reutilizado
├── ALTERACOES.md             # explicação da alteração
└── VIDEO.md                  # roteiro para a gravação exigida
```

Execução verificada em 03/11/2026: exemplo oficial em **8,21 s**; adaptação
com três imagens em **17,28 s**. São tempos de uma execução, sem download,
não um benchmark. Saídas completas: [oficial](resultados/oficial.stdout.txt)
e [adaptada](resultados/adaptado.stdout.txt), com os avisos em arquivos
`*.stderr.txt`. O caso com pauta falhou e o primeiro recebeu uma dica que
entrega o passo corrigido: veja [as limitações](ALTERACOES.md).

## Entrega

Link da pasta, depois da publicação dos commits:
[project-ai4good/tec](https://github.com/andrezacfalcao/project-ai4good/tree/main/tec).

Ainda precisam ser concluídos o vídeo real de 1–3 minutos, a justificativa
e a reflexão de autoria da aluna, a conferência pessoal dos links e a auditoria
cega em uma conversa nova. O protótipo executado não equivale à atividade inteira
concluída nem a uma validação em cadernos reais.
