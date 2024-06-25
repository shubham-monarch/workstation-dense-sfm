#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --partition=dev
#SBATCH --gres=gpu:ada1 # Request one GPU
#SBATCH --job-name=sfm-test 


#module load sdks/cuda-11.3

#source /WorkSpaces/SFM/e33/bin/activate
source /home/skumar/e6/bin/activate

# Parsing SVO params
svo_filename=$(python -c 'import json; config = json.load(open("config/config.json")); print(config.get("svo_filename", ""))')
svo_first_frame_idx=$(python -c 'import json; config = json.load(open("config/config.json")); print(config.get("svo_first_frame_idx", ""))')
svo_last_frame_idx=$(python -c 'import json; config = json.load(open("config/config.json")); print(config.get("svo_last_frame_idx", ""))')

# Parsing pipeline params
dense_sfm_path=$(python -c 'import json; config = json.load(open("config/config.json")); print(config.get("dense_sfm_path", ""))')


# ========== SVO PROCESSING ====================
SVO_FILE_NAME="../svo-processing"
SVO_INPUT="input/$svo_filename"
SVO_OUTPUT="svo_output/"
SVO_START=$svo_first_frame_idx
SVO_END=$svo_last_frame_idx
SVO_FOLDER_LOC="../svo-processing"

echo "SVO_START: $SVO_START"
echo "SVO_END: $SVO_END"
echo "SVO_FILE_NAME: $SVO_FILE_NAME"
echo "SVO_OUTPUT: $SVO_OUTPUT"


rm -rf $SVO_OUTPUT

#srun --gres=gpu:1 \
python "$(pwd)/${SVO_FOLDER_LOC}/scripts/svo_to_pointcloud.py" \
	--svo_path=$SVO_INPUT \
	--start_frame=$SVO_START\
	--end_frame=$SVO_END\
	--output_dir="$SVO_OUTPUT"

# ========== SPARSE RECONSTRUCTION ====================

SPARSE_RECONSTRUCTION_LOC="../sparse-reconstruction"
SPARSE_DATA_LOC="${SPARSE_RECONSTRUCTION_LOC}/pixsfm_dataset/"
SPARSE_RECONSTRUCTION_INPUT="svo_output"
ZED_PATH="input/$svo_filename"


#srun --gres=gpu:1 \
python "$(pwd)/${SPARSE_RECONSTRUCTION_LOC}/scripts/sparse-reconstruction.py" \
    --svo_dir=$SPARSE_RECONSTRUCTION_INPUT \
	--zed_path=$ZED_PATH



# ========= RIG BUNDLE ADJUSTMENT =====================

COLMAP_EXE_PATH=/usr/local/bin
RIG_BUNDLE_ADJUSTER_LOC="../rig-bundle-adjuster"
RIG_INPUT_PATH="${SPARSE_RECONSTRUCTION_LOC}/output/ref_locked/"
#RIG_INPUT_PATH=$(realpath "$RIG_INPUT_PATH")

echo "RIG_INPUT_PATH: $RIG_INPUT_PATH"

RIG_OUTPUT_PATH="${RIG_BUNDLE_ADJUSTER_LOC}/output/"
RIG_CONFIG_PATH="config/rig.json"

rm -rf $RIG_OUTPUT_PATH
mkdir -p "$RIG_OUTPUT_PATH"

$COLMAP_EXE_PATH/colmap rig_bundle_adjuster \
	--input_path $RIG_INPUT_PATH \
	--output_path $RIG_OUTPUT_PATH \
	--rig_config_path $RIG_CONFIG_PATH \
	--BundleAdjustment.refine_focal_length 0 \
	--BundleAdjustment.refine_principal_point 0 \
	--BundleAdjustment.refine_extra_params 0 \
	--BundleAdjustment.refine_extrinsics 1 \
	--BundleAdjustment.max_num_iterations 500 \
	--estimate_rig_relative_poses False


# ====== DENSE RECONSTRUCTION =======================

rm -rf $dense_sfm_path
DENSE_RECONSTRUCTION_LOC="../dense-reconstruction"
#srun --gres=gpu:1 \
	python "$(pwd)/${DENSE_RECONSTRUCTION_LOC}/scripts/dense-reconstruction.py" \
    	--mvs_path="$dense_sfm_path" \
    	--output_path="$RIG_OUTPUT_PATH" \
	--image_dir="$SPARSE_DATA_LOC" \


echo "****************************** DONE ************************"
