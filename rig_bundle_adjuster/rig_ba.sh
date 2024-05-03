#You must set $COLMAP_EXE_PATH to
#the directory containing the COLMAP executables
COLMAP_EXE_PATH=/usr/local/bin
INPUT_PATH=../sparse-reconstruction/output/ref_locked
OUTPUT_PATH=output/
RIG_CONFIG_PATH=config.json

echo "INPUT_PATH ===> $INPUT_PATH"
echo "OUTPUT_PATH ===>  $OUTPUT_PATH"
echo "RIG_CONFIG_PATH ===> $RIG_CONFIG_PATH"

rm -rf $OUTPUT_PATH
mkdir -p "$OUTPUT_PATH"

$COLMAP_EXE_PATH/colmap rig_bundle_adjuster \
	--input_path $INPUT_PATH \
	--output_path $OUTPUT_PATH \
	--rig_config_path $RIG_CONFIG_PATH \
	--BundleAdjustment.refine_focal_length 0 \
	--BundleAdjustment.refine_principal_point 0 \
	--BundleAdjustment.refine_extra_params 0 \
	--BundleAdjustment.refine_extrinsics 1 \
	--BundleAdjustment.max_num_iterations 100 \
	--estimate_rig_relative_poses False


