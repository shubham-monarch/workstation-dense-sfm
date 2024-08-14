#!/bin/bash


# SVO_FILENAME=$1
# SVO_STEP=$4
# SVO_START_IDX=$(($2 * $4))
# SVO_END_IDX=$(($3 * $4))
# FARM_TYPE=$5	

# testing
SVO_FILENAME="RJM/2024_06_06_utc/svo_files/front_2024-06-05-09-09-54.svo"
SVO_STEP=2
SVO_START_IDX=296
SVO_END_IDX=438
FARM_TYPE="vineyards"	

# redirecting all output to a log.main 
exec > logs/main.log 2>&1

echo -e "\n"
echo "==============================="
echo "[INSIDE MAIN-FILE.SH]"
echo "SVO_FILENAME: $SVO_FILENAME"
echo "SVO_START_IDX: $SVO_START_IDX"
echo "SVO_END_IDX: $SVO_END_IDX"
echo "SVO_STEP: $SVO_STEP"	
echo "==============================="
echo -e "\n"


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

# folder to store results
SUB_FOLDER_NAME="${SVO_START_IDX}_to_${SVO_END_IDX}"

# =====================================
# [STEP 1 --> EXTRACT STEREO-IMAGES FROM SVO FILE]
# =====================================

SVO_INPUT_DIR="${PIPELINE_INPUT_DIR}/svo-files"
SVO_OUTPUT_DIR="${PIPELINE_OUTPUT_DIR}/stereo-images"

SVO_FILE_PATH="${SVO_INPUT_DIR}/${SVO_FILENAME}"
SVO_IMAGES_DIR="${SVO_OUTPUT_DIR}/${SVO_FILENAME}/${SUB_FOLDER_NAME}"

START_TIME=$(date +%s) 

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


# =====================================
# [STEP 2 --> SPARSE-RECONSTRUCTION FROM STEREO-IMAGES]
# =====================================

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

	python3 -m ${PIPELINE_SCRIPT_DIR}.sparse_reconstruction \
	    --svo_images=$SVO_IMAGES_DIR \
		--input_dir=$SPARSE_RECON_INPUT_DIR \
		--output_dir=$SPARSE_RECON_OUTPUT_DIR \
		--svo_file=$SVO_FILE_PATH  
	
	
	# [SPARSE-RECONSTRUCTION CHECK]
	if [ $? -eq 0 ]; then
		
		END_TIME=$(date +%s)
		DURATION=$((END_TIME - START_TIME)) 
		
		echo -e "\n"
		echo "==============================="
		echo "Time taken for SPARSE-RECONSTRUCTION: ${DURATION} seconds"
		echo "==============================="
		echo -e "\n"
		# exit $EXIT_SUCCESS
	else
		echo -e "\n"
		echo "[ERROR] STEREO-RECONSTRUCTION FAILED ==> EXITING PIPELINE!"
		echo "Deleting ${SPARSE_RECON_OUTPUT_DIR}"
		rm -rf ${SPARSE_RECON_OUTPUT_DIR}
		echo -e "\n"
		exit $EXIT_FAILURE
	fi

else 
	echo -e "\n"
	echo "[WARNING] SKIPPING SPARSE-RECONSTTRUCTION as ${SPARSE_RECON_OUTPUT_DIR} already exists."
	echo "[WARNING] Delete [${SPARSE_RECON_OUTPUT_DIR}] folder and try again!"
	echo -e "\n"
fi


# =====================================
# [STEP 3 --> RIG-BUNDLE-ADJUSTMENT]
# =====================================

RBA_INPUT_DIR="${SPARSE_RECON_OUTPUT_DIR}/ref_locked/"
RBA_OUTPUT_DIR="${PIPELINE_OUTPUT_DIR}/rig-bundle-adjustment/${SVO_FILENAME}/${SUB_FOLDER_NAME}"
RBA_CONFIG_PATH="${PIPELINE_CONFIG_DIR}/rig.json"

if [ ! -d "$RBA_OUTPUT_DIR" ]; then

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


	# [RBA CONVERGENCE CHECK]
	if [ $? -ne 0 ]; then
		END_TIME=$(date +%s)
		DURATION=$((END_TIME - START_TIME)) 

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
else
	echo -e "\n"
	echo "[WARNING] SKIPPING RIG-BUNDLE-ADJUSTMENT as ${RBA_OUTPUT_DIR} already exists."
	echo "[WARNING] Delete [${RBA_OUTPUT_DIR}] folder and try again!"
	echo -e "\n"
fi

# =====================================
# [STEP 4 --> DENSE RECONSTRUCTION]
# =====================================

DENSE_RECON_OUTPUT_DIR="${PIPELINE_OUTPUT_DIR}/dense-reconstruction/${SVO_FILENAME}/${SUB_FOLDER_NAME}"

if [ ! -d "$DENSE_RECON_OUTPUT_DIR" ]; then

	START_TIME=$(date +%s) 

	python3 -m ${PIPELINE_SCRIPT_DIR}.dense-reconstruction \
	--mvs_path="$DENSE_RECON_OUTPUT_DIR" \
	--output_path="$RBA_OUTPUT_DIR" \
	--image_dir="$SPARSE_RECON_INPUT_DIR"

	
	if [ $? -eq 0 ]; then
		
		END_TIME=$(date +%s)
		DURATION=$((END_TIME - START_TIME)) 
		
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
		exit $EXIT_FAILURE
	fi

else 
	echo -e "\n"
	echo "[WARNING] SKIPPING DENSE-RECONSTRUCTION as ${DENSE_RECON_OUTPUT_DIR} already exists."
	echo "[WARNING] Delete [${DENSE_RECON_OUTPUT_DIR}] folder and try again!"
	echo -e "\n"
fi

# =====================================
# [STEP 5 --> FRAME-TO-FRAME [RGB] POINTCLOUD GENERATION]
# =====================================

P360_MODULE="p360"
BOUNDING_BOX="-5 5 -1 1 -1 1"
FRAME_TO_FRAME_RGB_FOLDER="${PIPELINE_OUTPUT_DIR}/frame-to-frame-rgb/${SVO_FILENAME}/${SUB_FOLDER_NAME}"
FRAME_TO_FRAME_RGB_CROPPED_FOLDER="${PIPELINE_OUTPUT_DIR}/frame-to-frame-rgb-cropped/${SVO_FILENAME}/${SUB_FOLDER_NAME}"

START_TIME=$(date +%s) 

python3 -m ${PIPELINE_SCRIPT_DIR}.${P360_MODULE}.main \
--bounding_box $BOUNDING_BOX \
--dense_reconstruction_folder="${DENSE_RECON_OUTPUT_DIR}" \
--frame_to_frame_folder="${FRAME_TO_FRAME_RGB_FOLDER}" \
--frame_to_frame_folder_CROPPED="${FRAME_TO_FRAME_RGB_CROPPED_FOLDER}"

if [ $? -eq 0 ]; then
	END_TIME=$(date +%s)
	DURATION=$((END_TIME - START_TIME)) 
	
	echo -e "\n"
	echo "==============================="
	echo "Time taken for generating frame-wise pointclouds: ${DURATION} seconds"
	echo "==============================="
	echo -e "\n"
else
	echo -e "\n"
	echo "[ERROR] FRAME-BY-FRAME [RGB] POINTCLOUD GENERATION FAILED ==> EXITING PIPELINE!"
	echo -e "\n"
	rm -rf ${CAMERA_FRAME_PCL}
	rm -rf ${CAMERA_FRAME_PCL_CROPPED}
	exit $EXIT_FAILURE
fi

# =====================================
# [STEP 6 --> GENERATE DENSE-SEGMENTED-RECONSTRUCTION]
# =====================================

DENSE_SEGMENTED_INPUT_FOLDER=${DENSE_RECON_OUTPUT_DIR}
DENSE_SEGMENTED_OUTPUT_FOLDER=${PIPELINE_OUTPUT_DIR}/dense-segmented-reconstruction/${SVO_FILENAME}/${SUB_FOLDER_NAME}

python3 -m ${PIPELINE_SCRIPT_DIR}.segFusion.segFusion \
	--input_folder="${DENSE_SEGMENTED_INPUT_FOLDER}" \
	--output_folder="${DENSE_SEGMENTED_OUTPUT_FOLDER}" \
	--farm_type="${FARM_TYPE}" 

if [ $? -eq 0 ]; then

	END_TIME=$(date +%s)
	DURATION=$((END_TIME - START_TIME)) 
	
	echo -e "\n"
	echo "==============================="
	echo "Time taken for dense-segmented-reconstruction: ${DURATION} seconds"
	echo "==============================="
	echo -e "\n"

else
	echo -e "\n"
	echo "[ERROR] DENSE-SEGMENTED-RECONSTRUCTION FAILED ==> EXITING PIPELINE!"
	echo -e "\n"
	exit $EXIT_FAILURE
fi

# =====================================
# [STEP 7 --> FRAME-TO-FRAME SEGMENTED-POINTCLOUD GENERATION]
# =====================================

P360_MODULE="p360"
BOUNDING_BOX="-5 5 -1 1 -1 1"
FRAME_TO_FRAME_SEGMENTED_FOLDER="${PIPELINE_OUTPUT_DIR}/frame-to-frame-segmented/${SVO_FILENAME}/${SUB_FOLDER_NAME}"
FRAME_TO_FRAME_SEGMENTED_CROPPED_FOLDER="${PIPELINE_OUTPUT_DIR}/frame-to-frame-segmented-cropped/${SVO_FILENAME}/${SUB_FOLDER_NAME}"

START_TIME=$(date +%s) 

python3 -m ${PIPELINE_SCRIPT_DIR}.${P360_MODULE}.main \
--bounding_box $BOUNDING_BOX \
--dense_reconstruction_folder="${DENSE_SEGMENTED_OUTPUT_FOLDER}" \
--frame_to_frame_folder="${FRAME_TO_FRAME_SEGMENTED_FOLDER}" \
--frame_to_frame_folder_CROPPED="${FRAME_TO_FRAME_SEGMENTED_CROPPED_FOLDER}"

if [ $? -eq 0 ]; then
	END_TIME=$(date +%s)
	DURATION=$((END_TIME - START_TIME)) 
	
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

# =====================================
# [STEP 8 --> LABEL THE DENSE-SEGMENTED-POINTCLOUD]
# =====================================

SEG_FUSION_DIR="${PIPELINE_SCRIPT_DIR}/segFusion"
PLY_FOLDER="${FRAME_TO_FRAME_SEGMENTED_FOLDER}"
PLY_FOLDER_LABELLED="${PIPELINE_OUTPUT_DIR}/labelled-pointclouds/${SVO_FILENAME}/${SUB_FOLDER_NAME}"

START_TIME=$(date +%s) 

python3 -m scripts.segFusion.label_PLY \
	--PLY_folder="${PLY_FOLDER}" \
	--output_folder="${PLY_FOLDER_LABELLED}" \
	--mavis="${SEG_FUSION_DIR}/Mavis.yaml"

if [ $? -eq 0 ]; then
		
	END_TIME=$(date +%s)
	DURATION=$((END_TIME - START_TIME)) 
	
	echo -e "\n"
	echo "==============================="
	echo "Time taken for labelling dense-segmented-pointcloud: ${DURATION} seconds"
	echo "==============================="
	echo -e "\n"

else
	echo -e "\n"
	echo "[ERROR] LABELLING DENSE-SEGMENTATION-POINTCLOUD FAILED ==> EXITING PIPELINE!"
	echo -e "\n"
	exit $EXIT_FAILURE
fi


# =====================================
# [STEP 9 --> GENERATE OUTPUT FOLDER]
# =====================================

START_TIME=$(date +%s) 

python3 -m scripts.segFusion.generate_occ_dataset \
	--f2f_RGB="${FRAME_TO_FRAME_RGB_FOLDER}" \
	--f2f_SEG="${FRAME_TO_FRAME_SEGMENTED_FOLDER}" \
	--f2f_LABELLED="${PLY_FOLDER_LABELLED}" \
	--o="output/occ-dataset/${SVO_FILENAME}/${SUB_FOLDER_NAME}"

if [ $? -eq 0 ]; then
		
	END_TIME=$(date +%s)
	DURATION=$((END_TIME - START_TIME)) 
	
	echo -e "\n"
	echo "==============================="
	echo "Time taken for generating OUTPUT folder: ${DURATION} seconds"
	echo "==============================="
	echo -e "\n"

else
	echo -e "\n"
	echo "[ERROR] OUTPUT FOLDER generation failed ==> EXITING PIPELINE!"
	echo -e "\n"
	exit $EXIT_FAILURE
fi
