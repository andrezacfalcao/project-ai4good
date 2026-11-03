"""Exemplo 01 do LAYA, com checkpoint publicado multilingual e revisao fixa.

Origem: examples/01_first_call_minimal.py do commit 462c2644e654add83516e53c7a65909f8072d529.
A entrada e a pergunta oficiais permanecem; a escolha do checkpoint e CPU e explicita.
"""
import os
from pathlib import Path

os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("USE_TORCH", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("HF_HOME", str(Path(__file__).resolve().parent / ".cache" / "huggingface"))

import laya

MODEL = "convaiinnovations/laya-multilingual"
REVISION = "e4e9ddf21a7b1903b7acffd8814ad4307bf63a67"


def carregar():
    return laya.load(MODEL, device="cpu", revision=REVISION)


def exemplo(agent):
    result = agent.predict(
        {"body": "Hi, we were billed twice for March. Please refund the duplicate today."},
        {"refund_requested": {
            "type": "noul",
            "instructions": "Does the user explicitly request a refund?",
        }},
    )
    answer = result["answers"]["refund_requested"]
    print("P(refund requested) = %.4f  (confidence %.4f)" % (answer["noul"], answer["confidence"]))
    return result


if __name__ == "__main__":
    exemplo(carregar())
