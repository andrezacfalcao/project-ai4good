#!/bin/sh
# roda o baseline oficial com as 5 sementes do artigo (2021..2025); log por semente em logs/
cd "$(dirname "$0")" || exit 1
for s in 2021 2022 2023 2024 2025; do
  sh rodar_baseline.sh $s 100 > logs/baseline_semente_$s.log 2>&1
done
