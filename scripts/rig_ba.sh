#! /bin/bash
COLMAP_EXE_PATH=/usr/local/bin

# Record the start time
start_time=$(date +%s)


echo "INPUT_PATH ===> $INPUT_PATH"
echo "OUTPUT_PATH ===>  $OUTPUT_PATH"
echo "RIG_CONFIG_PATH ===> $RIG_CONFIG_PATH"

rm -rf $OUTPUT_PATH
mkdir -p "$OUTPUT_PATH"

output = $COLMAP_EXE_PATH/colmap rig_bundle_adjuster \
	--input_path $INPUT_PATH \
	--output_path $OUTPUT_PATH \
	--rig_config_path $RIG_CONFIG_PATH \
	--BundleAdjustment.refine_focal_length 0 \
	--BundleAdjustment.refine_principal_point 0 \
	--BundleAdjustment.refine_extra_params 0 \
	--BundleAdjustment.refine_extrinsics 1 \
	--BundleAdjustment.max_num_iterations 100 \
	--estimate_rig_relative_poses False

echo "================================"
echo "====== OUTPUT ===> $output ====="
echo "================================"

# Record the end time
end_time=$(date +%s)

# Calculate the completion time
completion_time=$((end_time - start_time))


# Get the exit status of the last command
exit_status=$?

# Print the exit status
echo "Exit status: $exit_status"

# Check the exit status
if [ $exit_status -ne 0 ]; then
    echo "colmap rig_bundle_adjuster command failed."
    exit 1
else
    echo "colmap rig_bundle_adjuster command succeeded."
fi