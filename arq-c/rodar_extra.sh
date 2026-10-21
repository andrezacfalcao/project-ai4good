#!/bin/sh
# experimentos extras do artigo (sementes 2021-2023). uso: sh rodar_extra.sh G | H1M | H1B   [sementes...]
#   G   = ablação γ0=1 (sem ReZero) na ETTh2      H1M = ETTh1 modificado      H1B = ETTh1 baseline
# cada tarefa só roda se o log correspondente ainda não tem o resultado final ("mse:").
cd "$(dirname "$0")" || exit 1
PY=../../.venv/bin/python
COMUM="--is_training 1 --model ModernTCN --features M --seq_len 336 --pred_len 96 --ffn_ratio 1 --patch_size 8 --patch_stride 4 --num_blocks 1 --large_size 51 --small_size 5 --dims 64 64 64 64 --head_dropout 0.0 --enc_in 7 --dropout 0.3 --itr 1 --train_epochs 100 --batch_size 512 --patience 20 --learning_rate 0.0001 --lradj type3 --use_multi_scale False --small_kernel_merged False --num_workers 0 --root_path ../data/ETT-small"
T=$1; shift
for s in "${@:-2021 2022 2023}"; do for s in $s; do
  case $T in
    G)   L=logs/extra_ETTh2_gamma1_s$s.log; D=moderntcn_mod;    A="ATTN_GAMMA_INIT=1"; X="--model_id ETTh2_attn_g1 --data_path ETTh2.csv --data ETTh2 --use_attn 1";;
    H1M) L=logs/extra_ETTh1_modificado_s$s.log; D=moderntcn_mod;    A="X=0"; X="--model_id ETTh1_attn --data_path ETTh1.csv --data ETTh1 --use_attn 1";;
    H1B) L=logs/extra_ETTh1_baseline_s$s.log;   D=moderntcn_oficial; A="X=0"; X="--model_id ETTh1 --data_path ETTh1.csv --data ETTh1";;
  esac
  grep -q "^mse:" $L 2>/dev/null && continue
  (cd $D && env $A $PY -u run.py $COMUM $X --des Exp_s$s --random_seed $s) > $L 2>&1
done; done
