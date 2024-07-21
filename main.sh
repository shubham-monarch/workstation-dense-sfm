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


# [PIPELINE PARAMS]
SVO_FILENAME_WITH_IDX="${SVO_FILENAME}_${SVO_START_IDX}_${SVO_END_IDX}"
COLMAP_EXE_PATH=/usr/local/bin

PIPELINE_SCRIPT_DIR="scripts"
PIPELINE_CONFIG_DIR="config"
PIPELINE_INPUT_DIR="input" 
PIPELINE_OUTPUT_DIR="output"



# [SVO FILE ==> STEREO IMAGES]
SVO_INPUT_DIR="${PIPELINE_INPUT_DIR}/svo-files"
SVO_OUTPUT_DIR="${PIPELINE_OUTPUT_DIR}/stereo-images"

SVO_FILE_PATH="${SVO_INPUT_DIR}/${SVO_FILENAME}"
SVO_IMAGES_DIR="${SVO_OUTPUT_DIR}/${SVO_FILENAME_WITH_IDX}"

echo -e "\n"
echo "==============================="
echo "[SVO PROCESSING --> EXTRACTING IMAGES]"
echo "SVO_INPUT_DIR: $SVO_INPUT_DIR"
echo "SVO_OUTPUT_DIR: $SVO_OUTPUT_DIR"
echo "SVO_FILE_PATH: $SVO_FILE_PATH"
echo "SVO_IMAGES_DIR: $SVO_IMAGES_DIR"
echo "==============================="
echo -e "\n"


python3 "${PIPELINE_SCRIPT_DIR}/svo-to-stereo-images.py" \
	--svo_path=$SVO_FILE_PATH \
	--start_frame=$SVO_START_IDX \
	--end_frame=$SVO_END_IDX \
	--output_dir=$SVO_IMAGES_DIR \
	--svo_step=2


# [SVO STEREO IMAGES ==> SPARSE RECONSTRUCTION]
SPARSE_RECON_INPUT_DIR="${PIPELINE_INPUT_DIR}/sparse-reconstruction/${SVO_FILENAME_WITH_IDX}"
SPARSE_RECON_OUTPUT_DIR="${PIPELINE_OUTPUT_DIR}/sparse-reconstruction/${SVO_FILENAME_WITH_IDX}"


echo -e "\n"
echo "==============================="
echo "[SVO STEREO IMAGES --> SPARSE RECONSTRUCTION]"
echo "SPARSE_RECON_INPUT_DIR: $SPARSE_RECON_INPUT_DIR"
echo "SPARSE_RECON_OUTPUT_DIR: $SPARSE_RECON_OUTPUT_DIR"
echo "==============================="
echo -e "\n"

python3 "${PIPELINE_SCRIPT_DIR}/sparse-reconstruction.py" \
    --svo_images=$SVO_IMAGES_DIR \
	--input_dir=$SPARSE_RECON_INPUT_DIR \
	--output_dir=$SPARSE_RECON_OUTPUT_DIR \
	--svo_file=$SVO_FILE_PATH  


# [RIG BUNDLE ADJUSTMENT]
RBA_INPUT_DIR="${SPARSE_RECON_OUTPUT_DIR}/ref_locked/"
RBA_OUTPUT_DIR="${PIPELINE_OUTPUT_DIR}/rig-bundle-adjustment/${SVO_FILENAME_WITH_IDX}"
RBA_CONFIG_PATH="${PIPELINE_CONFIG_DIR}/rig.json"

echo -e "\n"
echo "==============================="
echo "[RIG BUNDLE ADJUSTMENT]"
echo "RBA_INPUT_DIR: $RBA_INPUT_DIR"
echo "RBA_OUTPUT_DIR: $RBA_OUTPUT_DIR"
echo "RBA_CONFIG_PATH: $RBA_CONFIG_PATH"
echo "==============================="
echo -e "\n"

rm -rf "${RBA_OUTPUT_DIR}"
mkdir -p "${RBA_OUTPUT_DIR}"

$COLMAP_EXE_PATH/colmap rig_bundle_adjuster \
	--input_path $RBA_INPUT_DIR \
	--output_path $RBA_OUTPUT_DIR \
	--rig_config_path $RBA_CONFIG_PATH \
	--BundleAdjustment.refine_focal_length 0 \
	--BundleAdjustment.refine_principal_point 0 \
	--BundleAdjustment.refine_extra_params 0 \
	--BundleAdjustment.refine_extrinsics 1 \
	--BundleAdjustment.max_num_iterations 500 \
	--estimate_rig_relative_poses False


# TODO: [ADD RBA FAILURE-CHECK]

# [DENSE RECONSTRUCTION]

DENSE_RECON_OUTPUT_DIR="${PIPELINE_OUTPUT_DIR}/dense-reconstruction/${SVO_FILENAME_WITH_IDX}"

python "${PIPELINE_SCRIPT_DIR}/dense-reconstruction.py" \
	--mvs_path="$DENSE_RECON_OUTPUT_DIR" \
	--output_path="$RBA_OUTPUT_DIR" \
	--image_dir="$SPARSE_RECON_INPUT_DIR" \


