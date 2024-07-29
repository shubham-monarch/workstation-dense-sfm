#! /usr/bin/bash

ROOT_FOLDER="/home/skumar/ssd/workstation-recon-setup"
DENSE_SFM_PATH="${ROOT_FOLDER}/pipeline-dense-sfm"
RIG_OUTPUT_PATH="${ROOT_FOLDER}/rig-bundle-adjuster/output"


DENSE_RECONSTRUCTION_LOC="pipeline-dense-sfm
#srun --gres=gpu:1 \
	python "$(pwd)/${DENSE_RECONSTRUCTION_LOC}/scripts/dense-reconstruction.py" \
    	--mvs_path="$DENSE_SFM_PATH" \
    	--output_path="$RIG_OUTPUT_PATH" \
	--image_dir="$SPARSE_DATA_LOC" \
