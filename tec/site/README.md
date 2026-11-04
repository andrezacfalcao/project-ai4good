# Site do Atlas do Erro

Um site local para rodar o Atlas do Erro sobre as imagens de teste e ver o resultado de cada passo.
Ele não muda a entrega do `tec`: o [`ler_caderno.py`](../ler_caderno.py) e os commits `ae9a9b4` e
`abf1638` ficam como estão. O núcleo, [`atlas.py`](atlas.py), repete a mesma lógica.

## Rodar

Na raiz do repositório, com o Ollama ativo e o `qwen2.5:1.5b` instalado:

```bash
uv pip install --python tec/.venv/bin/python -r tec/site/requirements.txt   # uma vez
./tec/site/rodar_site.sh
```

O site abre em <http://localhost:8501>.

## O que tem

- **Rodar uma imagem:** escolha um dos 3 cadernos do tec, uma das 60 resoluções do piloto do
  [exp](../../exp/piloto/README.md) ou envie uma foto. O site mostra o recorte e a leitura de cada linha
  (passos 3 e 4), deixa corrigir a transcrição e rodar de novo (passo 5), aponta a quebra pelo SymPy
  (passo 6) e mostra a categoria e a pista do Qwen (passo 7). Nas imagens de teste, confere tudo com o
  gabarito.
- **Rodar o conjunto inteiro:** passa todas as imagens de um conjunto, mostra linhas lidas exatas, quebra
  certa, tipo do erro certo e tempo médio, e baixa a tabela em CSV.
- **Opções na barra lateral:** o modelo Qwen instalado, o recorte (pelos vãos, do flx, ou três faixas
  fixas, do tec) e a lista fixa de categorias (do flx) ou a categoria livre (do tec).

Uma diferença em relação ao `ler_caderno.py`: um ponto final numa linha ("x = 2.") fazia o SymPy ler
2.0, e {2.0} ≠ {2}, o que apontava quebra em resolução certa. O site lê números decimais como frações.
O defeito foi encontrado pela segunda auditoria do exp, no piloto do E2.

## Verificação, 04/11/2026

Executado no notebook Linux (WSL2, i5-13450HX, RTX 4050), com Python 3.14.6 e Streamlit 1.66.1:

- teste automático com o `AppTest` do Streamlit, sem navegador: o site abre, roda o caderno 1 do tec
  (3 de 3 linhas lidas, quebra na linha 2, categoria "troca de sinal"), aceita a transcrição corrigida
  ("sem quebra") e roda os 3 cadernos do tec (cerca de 1 s por imagem);
- servidor real em `localhost`, respondendo `ok` em `/_stcore/health`.

Não foi testado num celular nem com fotos reais.

## Tecnologia: o que foi consultado e o que foi executado

| Opção | Fonte oficial | Licença | Situação |
| --- | --- | --- | --- |
| **Streamlit 1.66.1** | [docs.streamlit.io](https://docs.streamlit.io), [PyPI](https://pypi.org/project/streamlit/) | Apache-2.0 | **escolhida e executada.** O projeto já a usa em `app_streamlit.py`; tudo fica em Python, chamando as mesmas bibliotecas do tec; e o `AppTest` permite testar o site sem navegador |
| Gradio 6.31.0 | [gradio.app/docs](https://www.gradio.app/docs), [PyPI](https://pypi.org/project/gradio/) | Apache-2.0 | só consultada: também serve para demonstrar modelos, mas seria uma segunda biblioteca de interface no repositório |
| Flask 3.1.3, com HTML próprio | [flask.palletsprojects.com](https://flask.palletsprojects.com), [PyPI](https://pypi.org/project/Flask/) | BSD-3-Clause | só consultada: daria mais controle da tela, ao custo de escrever HTML e JavaScript |

As versões e licenças foram lidas no PyPI em 04/11/2026.
