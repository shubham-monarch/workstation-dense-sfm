#!/bin/bash


# [VIRTUAL ENV CHECK]
if [[ "$VIRTUAL_ENV" == "" ]]
then
    echo "No virtual environment found. Terminating script."
    exit 1
fi

# [PARSING CONFIG/CONFIG.JSON]
SVO_FILENAME=$(python -c '
import json
config = json.load(open("config/config.json"))
print(config.get("svo_filename", ""))
')

SVO_START_IDX=$(python -c '
import json
config = json.load(open("config/config.json"))
print(config.get("svo_first_frame_idx", ""))
')

SVO_END_IDX=$(python -c '
import json
config = json.load(open("config/config.json"))
print(config.get("svo_last_frame_idx", ""))
')


echo -e "\n"
echo "==============================="
echo "[PARSING CONFIG.JSON]"
echo "SVO_FILENAME: $SVO_FILENAME"
echo "SVO_START_IDX: $SVO_START_IDX"
echo "SVO_END_IDX: $SVO_END_IDX"
echo "==============================="
echo -e "\n"

INPUT_DIR="input" 
OUTPUT_DIR="output"
PIPELINE_SCRIPTS_DIR="scripts"

# [SVO -> STEOREO IMAGES]

SVO_INPUT_DIR="${INPUT_DIR}/svo-files"
SVO_OUTPUT_DIR="${OUTPUT_DIR}/stereo-images"

SVO_INPUT_PATH="${SVO_INPUT_DIR}/${SVO_FILENAME}"
SVO_OUTPUT_PATH="${SVO_OUTPUT_DIR}/${SVO_FILENAME}_${SVO_START_IDX}_${SVO_END_IDX}"
# SVO_OUTPUT_PATH="${SVO_OUTPUT_DIR}/${SVO_FILENAME}_${SVO_START_IDX}_${SVO_END_IDX}"

echo -e "\n"
echo "==============================="
echo "[SVO PROCESSING --> EXTRACTING IMAGES]"
echo "SVO_INPUT_DIR: $SVO_INPUT_DIR"
echo "SVO_OUTPUT_DIR: $SVO_OUTPUT_DIR"
echo "SVO_INPUT_PATH: $SVO_INPUT_PATH"
echo "SVO_OUTPUT_PATH: $SVO_OUTPUT_PATH"
echo "==============================="
echo -e "\n"


python "${PIPELINE_SCRIPTS_DIR}/svo_to_pointcloud.py" \
	--svo_path=$SVO_INPUT_PATH\
	--start_frame=$SVO_START_IDX\
	--end_frame=$SVO_END_IDX\
	--output_dir=$SVO_OUTPUT_PATH




exit 1

# ========== SPARSE RECONSTRUCTION ====================

# SPARSE_RECONSTRUCTION_LOC="../sparse-reconstruction"
# SPARSE_DATA_LOC="${SPARSE_RECONSTRUCTION_LOC}/pixsfm_dataset/"
# SPARSE_RECONSTRUCTION_INPUT="svo_output"
# ZED_PATH="input/$svo_filename"

# SPARSE_RECON_INPUT_DIR="${SVO_OUTPUT_PATH}"
SPARSE_RECON_DIR="${INPUT_DIR}/sparse-reconstruction/${SVO_FILENAME}_${SVO_START_IDX}_${SVO_END_IDX}"
SPARSE_RECON_INPUT_DIR="${SVO_OUTPUT_PATH}"
SPARSE_RECON_OUTPUT_DIR="${OUTPUT_DIR}/sparse-reconstruction/${SVO_FILENAME}_${SVO_START_IDX}_${SVO_END_IDX}"



# #srun --gres=gpu:1 \
# python "$(pwd)/${SPARSE_RECONSTRUCTION_LOC}/scripts/sparse-reconstruction.py" \
#     --svo_dir=$SPARSE_RECONSTRUCTION_INPUT \
# 	--zed_path=$ZED_PATH

python "$(pwd)/${SPARSE_RECONSTRUCTION_LOC}/scripts/sparse-reconstruction.py" \
    --workspace=$SPARSE_RECON_DIR \
	--input=$SPARSE_RECON_INPUT_DIR \
	--output=$SPARSE_RECON_OUTPUT_DIR \
	--svo_file=$SVO_INPUT_PATH 

exit 1

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
