#!/bin/bash
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --gpus-per-node=a100:1
#SBATCH --mem-per-cpu=500G
export PYTORCH_CUDA_ALLOC_CONF='expandable_segments:True'
python3 main.py
