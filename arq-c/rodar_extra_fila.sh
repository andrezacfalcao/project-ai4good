#!/bin/sh
# fila sequencial (um treino por vez: vários processos MPS ao mesmo tempo travam). espera os treinos em curso terminarem.
cd "$(dirname "$0")" || exit 1
while pgrep -f "run.py --is_training" > /dev/null; do sleep 20; done
for j in "H1B 2022" "G 2021" "G 2022" "H1M 2021" "H1M 2022"; do sh rodar_extra.sh $j; done
python3 -c "print()" ; ../.venv/bin/python agregar_extra.py > /dev/null; echo done > logs/extra_FIM.txt
