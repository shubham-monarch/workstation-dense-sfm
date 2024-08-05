#!/bin/bash

# Parsing SVO params
svo_filename=$(python -c 'import json; config = json.load(open("config/config.json")); print(config.get("svo_filename", ""))')
svo_first_frame_idx=$(python -c 'import json; config = json.load(open("config/config.json")); print(config.get("svo_first_frame_idx", ""))')
svo_last_frame_idx=$(python -c 'import json;  = json.load(open("config/config.json")); print(config.get("svo_last_frame_idx", ""))')

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




# ========== SPARSE RECONSTRUCTION ====================

SPARSE_RECONSTRUCTION_LOC="../sparse-reconstruction"


# ========= RIG BUNDLE ADJUSTMENT =====================

COLMAP_EXE_PATH=/usr/local/bin
RIG_BUNDLE_ADJUSTER_LOC="../rig-bundle-adjuster"
RIG_INPUT_PATH="${SPARSE_RECONSTRUCTION_LOC}/output/ref_locked/"
#RIG_INPUT_PATH=$(realpath "$RIG_INPUT_PATH")

echo "RIG_INPUT_PATH: $RIG_INPUT_PATH"

RIG_OUTPUT_PATH="${RIG_BUNDLE_ADJUSTER_LOC}/output/"
RIG_CONFIG_PATH="config/rig.json"




# ====== DENSE RECONSTRUCTION =======================

rm -rf $dense_sfm_path
DENSE_RECONSTRUCTION_LOC="../dense-reconstruction"
#srun --gres=gpu:1 \
	python "$(pwd)/${DENSE_RECONSTRUCTION_LOC}/scripts/dense-reconstruction.py" \
    	--mvs_path="$dense_sfm_path" \
    	--output_path="$RIG_OUTPUT_PATH" \
	--image_dir="$SPARSE_DATA_LOC" \


echo "****************************** DONE ************************"
