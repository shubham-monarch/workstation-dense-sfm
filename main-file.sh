#!/bin/bash


# SVO_FILENAME=$1
# SVO_STEP=$4
# SVO_START_IDX=$(($2 * $4))
# SVO_END_IDX=$(($3 * $4))


SVO_FILENAME="vineyards/RJM/front_2024-06-06-09-26-19.svo"
SVO_STEP=2
SVO_START_IDX=4
SVO_END_IDX=126


echo -e "\n"
echo "==============================="
echo "[INSIDE MAIN-FILE.SH]"
echo "SVO_FILENAME: $SVO_FILENAME"
echo "SVO_START_IDX: $SVO_START_IDX"
echo "SVO_END_IDX: $SVO_END_IDX"
echo "==============================="
echo -e "\n"

# exit 0

# [GLOBAL PARAMS]
EXIT_FAILURE=1
EXIT_SUCCESS=0
COLMAP_EXE_PATH=/usr/local/bin

# [PIPELINE INTERNAL PARAMS]
PIPELINE_SCRIPT_DIR="scripts"
PIPELINE_CONFIG_DIR="config"
PIPELINE_INPUT_DIR="input-backend" 
PIPELINE_OUTPUT_DIR="output-backend"

# ==== PIPELINE EXECUTION STARTS HERE ====

# [VIRTUAL ENV CHECK]
if [[ "$VIRTUAL_ENV" == "" ]]
then
    echo "No virtual environment found. Terminating script."
    exit 1
fi

# # [PARSING CONFIG/CONFIG.PY]
# SVO_FILENAME=$(python -c '
# import config.config as cfg
# print(cfg.SVO_FILENAME)
# ')

# SVO_START_IDX=$(python -c '
# import config.config as cfg
# print(getattr(cfg, "SVO_START_IDX", -1))
# ')

# SVO_END_IDX=$(python -c '
# import config.config as cfg
# print(getattr(cfg, "SVO_END_IDX", -1))
# ')

# echo -e "\n"
# echo "==============================="
# echo "[PARSING CONFIG.JSON]"
# echo "SVO_FILENAME: $SVO_FILENAME"
# echo "SVO_START_IDX: $SVO_START_IDX"
# echo "SVO_END_IDX: $SVO_END_IDX"
# echo "==============================="
# echo -e "\n"

# folder to store results
SUB_FOLDER_NAME="${SVO_START_IDX}_to_${SVO_END_IDX}"

# [STEP #1 --> EXTRACT STEREO-IMAGES FROM SVO FILE]
SVO_INPUT_DIR="${PIPELINE_INPUT_DIR}/svo-files"
SVO_OUTPUT_DIR="${PIPELINE_OUTPUT_DIR}/stereo-images"

SVO_FILE_PATH="${SVO_INPUT_DIR}/${SVO_FILENAME}"
SVO_IMAGES_DIR="${SVO_OUTPUT_DIR}/${SVO_FILENAME}/${SUB_FOLDER_NAME}"

# extracting 1 frame per {SVO_STEP} frames
# SVO_STEP=2

# echo -e "\n"
# echo "==============================="
# echo "[SVO PROCESSING --> EXTRACTING IMAGES]"
# echo "SVO_INPUT_DIR: $SVO_INPUT_DIR"
# echo "SVO_OUTPUT_DIR: $SVO_OUTPUT_DIR"
# echo "SVO_FILE_PATH: $SVO_FILE_PATH"
# echo "SVO_IMAGES_DIR: $SVO_IMAGES_DIR"
# echo "==============================="
# echo -e "\n"

# check if the output folder already exists
# if [ ! -d "$SVO_IMAGES_DIR" ]; then

	START_TIME=$(date +%s) 
	# python3 "${PIPELINE_SCRIPT_DIR}/svo-to-stereo-images.py" \
	# 	--svo_path=$SVO_FILE_PATH \
	# 	--start_frame=$SVO_START_IDX \
	# 	--end_frame=$SVO_END_IDX \
	# 	--output_dir=$SVO_IMAGES_DIR \
	# 	--svo_step=$SVO_STEP

	python3 -m scripts.svo-to-stereo-images \
		--svo_path=$SVO_FILE_PATH \
		--start_frame=$SVO_START_IDX \
		--end_frame=$SVO_END_IDX \
		--output_dir=$SVO_IMAGES_DIR \
		--svo_step=$SVO_STEP

	END_TIME=$(date +%s)
	DURATION=$((END_TIME - START_TIME)) 

	if [ $? -eq 0 ]; then
		echo -e "\n"
		echo "==============================="
		echo "Time taken for SVO TO STEREO-IMAGES generation: ${DURATION} seconds"
		echo "==============================="
		echo -e "\n"
	else
		echo -e "\n"
		echo "[ERROR] SVO TO STEREO-IMAGES FAILED ==> EXITING PIPELINE!"
		echo -e "\n"
		rm -rf ${SVO_IMAGES_DIR}
		exit $EXIT_FAILURE
	fi
# else
# 	echo -e "\n"
# 	echo "[WARNING] SKIPPING svo to stereo-images generation as ${SVO_IMAGES_DIR} already exists."
# 	echo "[WARNING] Delete [${SVO_IMAGES_DIR}] folder and try again!"
# 	echo -e "\n"
# fi


# [STEP #2 --> SPARSE-RECONSTRUCTION FROM STEREO-IMAGES]
SPARSE_RECON_INPUT_DIR="${PIPELINE_INPUT_DIR}/sparse-reconstruction/${SVO_FILENAME}/${SUB_FOLDER_NAME}"
SPARSE_RECON_OUTPUT_DIR="${PIPELINE_OUTPUT_DIR}/sparse-reconstruction/${SVO_FILENAME}/${SUB_FOLDER_NAME}"

echo -e "\n"
echo "==============================="
echo "[SVO STEREO IMAGES --> SPARSE RECONSTRUCTION]"
echo "SPARSE_RECON_INPUT_DIR: $SPARSE_RECON_INPUT_DIR"
echo "SPARSE_RECON_OUTPUT_DIR: $SPARSE_RECON_OUTPUT_DIR"
echo "==============================="
echo -e "\n"

if [ ! -d "$SPARSE_RECON_OUTPUT_DIR" ]; then
	START_TIME=$(date +%s) 

	python3 "${PIPELINE_SCRIPT_DIR}/sparse_reconstruction.py" \
	    --svo_images=$SVO_IMAGES_DIR \
		--input_dir=$SPARSE_RECON_INPUT_DIR \
		--output_dir=$SPARSE_RECON_OUTPUT_DIR \
		--svo_file=$SVO_FILE_PATH  

	# python3 -m scripts.sparse_reconstruction \
	#     --svo_images=$SVO_IMAGES_DIR \
	# 	--input_dir=$SPARSE_RECON_INPUT_DIR \
	# 	--output_dir=$SPARSE_RECON_OUTPUT_DIR \
	# 	--svo_file=$SVO_FILE_PATH  

	
	SPARSE_REC_EXIT_STATUS=$?
	
	echo -e "\n"
	echo "==============================="
	echo "SPARSE_REC_EXIT_STATUS: $SPARSE_REC_EXIT_STATUS"
	echo "==============================="
	echo -e "\n"


	
	END_TIME=$(date +%s)
	DURATION=$((END_TIME - START_TIME)) 
		
	
	# [SPARSE-RECONSTRUCTION CHECK]
	if [ $? -eq 0 ]; then
		echo -e "\n"
		echo "==============================="
		echo "Time taken for SPARSE-RECONSTRUCTION: ${DURATION} seconds"
		echo "==============================="
		echo -e "\n"
		# exit $EXIT_SUCCESS
	else
		echo -e "\n"
		echo "[ERROR] STEREO-RECONSTRUCTION FAILED ==> EXITING PIPELINE!"
		echo -e "\n"
		rm -rf ${SPARSE_RECON_OUTPUT_DIR}
		exit $EXIT_FAILURE
	fi

else 
	echo -e "\n"
	echo "[WARNING] SKIPPING stereo-images to sparse-reconstruction as ${SPARSE_RECON_OUTPUT_DIR} already exists."
	echo "[WARNING] Delete [${SPARSE_RECON_OUTPUT_DIR}] folder and try again!"
	echo -e "\n"
fi

# return $EXIT_SUCCESS

# [STEP #3 --> RIG-BUNDLE-ADJUSTMENT]
RBA_INPUT_DIR="${SPARSE_RECON_OUTPUT_DIR}/ref_locked/"
RBA_OUTPUT_DIR="${PIPELINE_OUTPUT_DIR}/rig-bundle-adjustment/${SVO_FILENAME}/${SUB_FOLDER_NAME}"
RBA_CONFIG_PATH="${PIPELINE_CONFIG_DIR}/rig.json"

# python3 -c "import scripts.utils_module.zed_utils as zu;  zu.generate_rig_json('${$RBA_CONFIG_PATH}','${SVO_FILE_NAME}')"
python3 -c "import scripts.utils_module.zed_utils as zu;  zu.generate_rig_json('${RBA_CONFIG_PATH}','${SVO_FILENAME}')"


echo -e "\n"
echo "==============================="
echo "[RIG BUNDLE ADJUSTMENT]"
echo "RBA_INPUT_DIR: $RBA_INPUT_DIR"
echo "RBA_OUTPUT_DIR: $RBA_OUTPUT_DIR"
echo "RBA_CONFIG_PATH: $RBA_CONFIG_PATH"
echo "==============================="
echo -e "\n"

# if [ ! -d "$RBA_OUTPUT_DIR" ]; then

	rm -rf "${RBA_OUTPUT_DIR}"
	mkdir -p "${RBA_OUTPUT_DIR}"

	START_TIME=$(date +%s) 

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

	END_TIME=$(date +%s)
	DURATION=$((END_TIME - START_TIME)) 

	# [RBA CONVERGENCE CHECK]
	if [ $? -ne 0 ]; then
		echo -e "\n"
		echo "==============================="
		echo "RBA FAILED ==> EXITING PIPELINE!"
		echo "==============================="
		echo -e "\n"
		rm -rf "${RBA_OUTPUT_DIR}"
		exit $EXIT_FAILURE
	fi

	# ZED_BASELINE
	ZED_BASELINE=$(python3 -c "import scripts.utils_module.bash_utils as bu;  bu.get_baseline('${SVO_FILENAME}')")

	echo -e "\n"
	echo "==============================="
	echo "ZED_BASELINE: ${ZED_BASELINE}"
	echo "==============================="
	echo -e "\n"

	# [VERIFYING RBA RESULTS]
	
	
	
	# python3 "${PIPELINE_SCRIPT_DIR}/rba_check.py" \
	# 	--rba_output=$RBA_OUTPUT_DIR

	python3 -m scripts.rba_check \
		--rba_output=$RBA_OUTPUT_DIR \
		--baseline=$ZED_BASELINE

	# [RBA RESULTS CHECK]
	if [ $? -eq 0 ]; then
		echo -e "\n"
		echo "==============================="
		echo "Time taken for RIG-BUNDLE-ADJUSTMENT: ${DURATION} seconds"
		echo "==============================="
		echo -e "\n"
	else
		echo -e "\n"
		echo "[ERROR] RIG-BUNDLE-ADJUSTMENT FAILED ==> EXITING PIPELINE!"
		echo -e "\n"
		rm -rf "${RBA_OUTPUT_DIR}"
		exit $EXIT_FAILURE
	fi

# else
# 	echo -e "\n"
# 	echo "[WARNING] SKIPPING rig-bundle-adjustment as ${RBA_OUTPUT_DIR} already exists."
# 	echo "[WARNING] Delete [${RBA_OUTPUT_DIR}] folder and try again!"
# 	echo -e "\n"
# fi

exit $EXIT_SUCCESS

# [STEP #4 --> DENSE RECONSTRUCTION]
DENSE_RECON_OUTPUT_DIR="${PIPELINE_OUTPUT_DIR}/dense-reconstruction/${SVO_FILENAME}/${SUB_FOLDER_NAME}"

if [ ! -d "$DENSE_RECON_OUTPUT_DIR" ]; then

	START_TIME=$(date +%s) 

	python3 "${PIPELINE_SCRIPT_DIR}/dense-reconstruction.py" \
	--mvs_path="$DENSE_RECON_OUTPUT_DIR" \
	--output_path="$RBA_OUTPUT_DIR" \
	--image_dir="$SPARSE_RECON_INPUT_DIR"

	END_TIME=$(date +%s)
	DURATION=$((END_TIME - START_TIME)) 

	if [ $? -eq 0 ]; then
		echo -e "\n"
		echo "==============================="
		echo "Time taken for dense-reconstruction: ${DURATION} seconds"
		echo "==============================="
		echo -e "\n"
	else
		echo -e "\n"
		echo "[ERROR] DENSE-RECONSTRUCTION FAILED ==> EXITING PIPELINE!"
		echo -e "\n"
		rm -rf ${DENSE_RECON_OUTPUT_DIR}
		return $EXIT_FAILURE
	fi

else 
	echo -e "\n"
	echo "[WARNING] SKIPPING dense-reconstruction as ${DENSE_RECON_OUTPUT_DIR} already exists."
	echo "[WARNING] Delete [${DENSE_RECON_OUTPUT_DIR}] folder and try again!"
	echo -e "\n"
fi

# [STEP #5 --> FRAME-TO-FRAME (CROPPED) POINTCLOUD GENERATION]
P360_MODULE="p360"
BOUNDING_BOX="-5 5 -1 1 -1 1"
CAMERA_FRAME_PCL="${PIPELINE_OUTPUT_DIR}/pointcloud-camera-frame/${SVO_FILENAME}/${SUB_FOLDER_NAME}"
CAMERA_FRAME_PCL_CROPPED="${PIPELINE_OUTPUT_DIR}/pointcloud-cropped-camera-frame/${SVO_FILENAME}/${SUB_FOLDER_NAME}"

if [ -d "$CAMERA_FRAME_PCL" ] && [ -d "$CAMERA_FRAME_PCL_CROPPED" ]; then
	echo -e "\n"
	echo "[WARNING] SKIPPING frame-wise pointcloud generation as ${CAMERA_FRAME_PCL} and ${CAMERA_FRAME_PCL_CROPPED} already exist."
	echo "[WARNING] Delete [${CAMERA_FRAME_PCL}] or [${CAMERA_FRAME_PCL_CROPPED}] and try again!"
	echo -e "\n"
else 
	START_TIME=$(date +%s) 

	python3 -m ${PIPELINE_SCRIPT_DIR}.${P360_MODULE}.main \
	--bounding_box $BOUNDING_BOX \
	--dense_reconstruction_folder="${DENSE_RECON_OUTPUT_DIR}" \
	--pcl_folder="${CAMERA_FRAME_PCL}" \
	--pcl_cropped_folder="${CAMERA_FRAME_PCL_CROPPED}"
	
	END_TIME=$(date +%s)
	DURATION=$((END_TIME - START_TIME)) 

	if [ $? -eq 0 ]; then
		echo -e "\n"
		echo "==============================="
		echo "Time taken for generating frame-wise pointclouds: ${DURATION} seconds"
		echo "==============================="
		echo -e "\n"
	else
		echo -e "\n"
		echo "[ERROR] FRAME-BY-FRAME POINTCLOUD GENERATION FAILED ==> EXITING PIPELINE!"
		echo -e "\n"
		rm -rf ${CAMERA_FRAME_PCL}
		rm -rf ${CAMERA_FRAME_PCL_CROPPED}
		exit $EXIT_FAILURE
	fi
fi

exit $EXIT_SUCCESS