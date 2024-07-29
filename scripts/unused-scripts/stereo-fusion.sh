#! /usr/bin/bash 

COLMAP_EXE_PATH=/usr/local/bin
DENSE_SFM_FOLDER="front_2023-11-03-10-51-17.svo"
OUTPUT="output"

rm -rf $OUTPUT
mkdir $OUTPUT

$COLMAP_EXE_PATH/colmap stereo_fusion \
    --workspace_path=${DENSE_SFM_FOLDER} \
    --output_type=PLY \
    --output_path=${OUTPUT}/dense.ply \
