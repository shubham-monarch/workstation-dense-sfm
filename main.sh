#!/bin/bash

# [VIRTUAL ENV CHECK]
if [[ "$VIRTUAL_ENV" == "" ]]
then
    echo "No virtual environment found. Terminating script."
    exit 1
fi

# [PARSING CONFIG/CONFIG.PY]
SVO_FILENAME=$(python -c '
import config.config as cfg
print(cfg.SVO_FILENAME)
')

SVO_START_IDX=$(python -c '
import config.config as cfg
print(getattr(cfg, "SVO_START_IDX", -1))
')

SVO_END_IDX=$(python -c '
import config.config as cfg
print(getattr(cfg, "SVO_END_IDX", -1))
')


echo -e "\n"
echo "==============================="
echo "[PARSING CONFIG.JSON]"
echo "SVO_FILENAME: $SVO_FILENAME"
echo "SVO_START_IDX: $SVO_START_IDX"
echo "SVO_END_IDX: $SVO_END_IDX"
echo "==============================="
echo -e "\n"


# [GLOBAL PARAMS]
EXIT_FAILURE=1
EXIT_SUCCESS=0
COLMAP_EXE_PATH=/usr/local/bin

# [PIPELINE PARAMS]
PIPELINE_SCRIPT_DIR="scripts"
PIPELINE_CONFIG_DIR="config"
PIPELINE_INPUT_DIR="input" 
PIPELINE_OUTPUT_DIR="output"

SVO_FILENAME_WITH_IDX="${SVO_FILENAME}_${SVO_START_IDX}_${SVO_END_IDX}"

# extracting 1 frame / {SVO_STEP} frames
SVO_STEP=2


# [STEP #1 --> EXTRACT STEREO-IMAGES FROM SVO FILE]
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
	--svo_step=$SVO_STEP

# [STEP #2 --> SPARSE-RECONSTRUCTION FROM STEREO-IMAGES]
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

# [SPARSE-RECONSTRUCTION CHECK]
if [ $? -ne 0 ]; then
    echo -e "\n"
	echo "==============================="
	echo "SPARSE-RECONSTRUCTION FAILED ==> EXITING PIPELINE!"
    echo "==============================="
	echo -e "\n"
	exit $EXIT_FAILURE
fi


# [STEP #3 --> RIG-BUNDLE-ADJUSTMENT]
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

# [RBA CONVERGENCE CHECK]
if [ $? -ne 0 ]; then
    echo -e "\n"
	echo "==============================="
	echo "RBA FAILED ==> EXITING PIPELINE!"
    echo "==============================="
	echo -e "\n"
	exit $EXIT_FAILURE
fi

# [VERIFYING RBA RESULTS]
python3 "${PIPELINE_SCRIPT_DIR}/rba_check.py" \
	--rba_output=$RBA_OUTPUT_DIR

# [RBA RESULTS CHECK]
if [ $? -ne 0 ]; then
    echo -e "\n"
	echo "==============================="
	echo "RBA FAILED ==> EXITING PIPELINE!"
    echo "==============================="
	echo -e "\n"
	exit $EXIT_FAILURE
fi

# [STEP #4 --> DENSE RECONSTRUCTION]
DENSE_RECON_OUTPUT_DIR="${PIPELINE_OUTPUT_DIR}/dense-reconstruction/${SVO_FILENAME_WITH_IDX}"

START_TIME=$(date +%s) 

python3 "${PIPELINE_SCRIPT_DIR}/dense-reconstruction.py" \
  --mvs_path="$DENSE_RECON_OUTPUT_DIR" \
  --output_path="$RBA_OUTPUT_DIR" \
  --image_dir="$SPARSE_RECON_INPUT_DIR"

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME)) 

# Check the exit status
if [ $? -eq 0 ]; then
    echo -e "\n"
	echo "==============================="
	echo "Time taken for dense-reconstruction: ${DURATION/ 60} minutes"
	echo "==============================="
	echo -e "\n"
else
    echo "The program encountered an error."
fi

	
