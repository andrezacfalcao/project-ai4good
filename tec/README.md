# tec · tecnologia base demonstrável

Artefato do **Atlas do Erro**, separado das outras atividades da disciplina.

## Exemplo oficial

Origem: [model card do TrOCR-small-printed](https://huggingface.co/microsoft/trocr-small-printed#how-to-use).
O carregamento, processamento, geração e decodificação seguem o exemplo oficial.
A imagem IAM do exemplo foi disponibilizada localmente e a transcrição é impressa
no terminal. O checkpoint é voltado a texto impresso; este teste não comprova
reconhecimento de matemática manuscrita.

Na raiz do repositório:

```bash
cd tec
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python ler_caderno.py
```

Na primeira execução, o Transformers baixa os pesos do Hugging Face.
Depois do download, é possível executar com `HF_HUB_OFFLINE=1`.

O código original é distribuído sob a [licença MIT da Microsoft](https://github.com/microsoft/unilm/blob/master/LICENSE).
Veja a cópia em `licencas/unilm-MIT.txt`.
