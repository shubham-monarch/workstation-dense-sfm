#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --partition=dev
#SBATCH --gres=gpu:ada1 # Request one GPU
#SBATCH --job-name=sfm-test 


#module load sdks/cuda-11.3

#source /home/skumar/e33/bin/activate

# Parse JSON file and extract parameters


svo_path=$(python -c 'import json; config = json.load(open("config/config.json")); print(config.get("svo_path", ""))')
camera_params=$(python -c 'import json; config = json.load(open("config/config.json")); params = config.get("camera_params", []); print(",".join(str(x) for x in params))')


#echo $svo_path
#echo $camera_params


#srun --gres=gpu:1  \
#	python ../sparse-reconstruction/scripts/sparse-reconstruction.py \
#	--svo_dir="$svo_path" \
#	--camera_params="$camera_params"


source /home/skumar/e6/bin/activate
python ../sparse-reconstruction/scripts/sparse-reconstruction.py \
       --svo_dir="$svo_path" \
       --camera_params="$camera_params"

#srun --gres=gpu:1 --pty bash rig-bundle-adjuster/rig_ba.sh
#srun --gres=gpu:1 --pty python ../dense-reconstruction/scripts/dense-reconstruction.py

