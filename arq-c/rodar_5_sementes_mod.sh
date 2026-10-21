#!/bin/sh
# espera o baseline terminar (a GPU é compartilhada) e roda o modificado com as mesmas 5 sementes
cd "$(dirname "$0")" || exit 1
while pgrep -f rodar_5_sementes.sh > /dev/null; do sleep 30; done
for s in 2021 2022 2023 2024 2025; do
  sh rodar_modificado.sh $s 100 > logs/modificado_semente_$s.log 2>&1
done
