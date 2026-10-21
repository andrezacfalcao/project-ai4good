#!/bin/sh
# baseline "as-is": comando de moderntcn_oficial/scripts/ETTh2.sh (pred_len 96), sem alterar hiperparâmetros.
# uso: sh rodar_baseline.sh <semente> [épocas]   (o artigo reporta 5 sementes; o padrão do código é 2021)
cd "$(dirname "$0")/moderntcn_oficial" || exit 1
../../.venv/bin/python -u run.py --is_training 1 --model_id ETTh2 --model ModernTCN \
  --root_path ../data/ETT-small --data_path ETTh2.csv --data ETTh2 --features M \
  --seq_len 336 --pred_len 96 --ffn_ratio 1 --patch_size 8 --patch_stride 4 --num_blocks 1 \
  --large_size 51 --small_size 5 --dims 64 64 64 64 --head_dropout 0.0 --enc_in 7 --dropout 0.3 \
  --itr 1 --train_epochs "${2:-100}" --batch_size 512 --patience 20 --learning_rate 0.0001 \
  --des "Exp_s${1:-2021}" --lradj type3 --use_multi_scale False --small_kernel_merged False \
  --random_seed "${1:-2021}" --num_workers 0
