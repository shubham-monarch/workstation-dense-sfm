#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --partition=dev
#SBATCH --gres=gpu:ada1 # Request one GPU


# Run your Python script using srun
srun --gres=gpu:1 --pty bash rig_ba.sh

