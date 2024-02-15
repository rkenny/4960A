#!/bin/bash
#SBATCH --ntasks-per-node=4
#SBATCH --cpus-per-task=2
#SBATCH --gpus-per-node=2
#SBATCH --mem-per-cpu=16G
python3 main.py
