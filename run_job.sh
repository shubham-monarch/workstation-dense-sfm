#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --partition=dev
#SBATCH --gres=gpu:ada1 # Request one GPU

module-load sdks/cuda-11.3

source /home/skumar/e33/bin/activate

# Run your Python script using srun
srun --gres=gpu:1 --pty python sparse-reconstruction/scripts/sparse-reconstruction.py
srun --gres=gpu:1 --pty bash rig-bundle-adjuster/rig_ba.sh
srun --gres=gpu:1 --pty python dense-recontruction/scripts/dense-reconstruction.py

