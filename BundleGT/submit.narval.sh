#!/bin/bash
#SBATCH --ntasks-per-node=5
#SBATCH --cpus-per-task=3
#SBATCH --gpus-per-node=4
#SBATCH --mem-per-cpu=32G
python3 main.py -g 0 -m BundleGT -d imdb --info="" --batch_size_test=8192 --batch_size_train=8192 --lr=1e-3 --l2_reg=1e-5 --num_ui_layer=4 --gcn_norm=0 --num_trans_layer=3 --num_token=70 --folder="train" --early_stopping=0 --ub_alpha=0.5 --bi_alpha=0.5
