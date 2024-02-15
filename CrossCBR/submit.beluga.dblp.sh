#!/bin/bash
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --gpus-per-node=1
#SBATCH --mem-per-cpu=32G
echo "Running DBLP on Beluga"
python train.py -g 0 -m CrossCBR -d dblp
