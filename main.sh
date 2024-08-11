#!/bin/bash

<<comment
[TO-DO]

- aws api integration
- aws / local input detection

- output-backend -> output folder
- aws instance setup
	- add colmap cmake update to s pycolmap installtion 
	- retag colmap , pycolmap
	- update requirements.txt
	- update pipeline tag
- processed/unprocessed folders
	- add svo files
	- cleanup before running the pipelines
- documentation
	- update release notes
	- update installation steps
	- add + update setup.mds
	- add readme.md
	- update colmap installation steps in setup.md
- add segmentation inference script

- check if script is being executed from the project root
- dense reconstruction support for multiple gpus
- [error-handling / folder deletion] for Ctrl-C / unexpected script termination 
- update default bb params for pointcloud cropping
- return -1 for failed jsons
- add colmap cmake update to support pycolmap installtion 
- retag colmap , pycolmap
- update COLMAP tags with pycolmap bindings integration
- update requirements.txt
- update pipeline tag
- cleanup for all the modules
- aws integration 
- segmentation module integration
- ply to labelled ply
- add main-ws.sh, main-aws.sh
- aws integration
- move all files inside input to a folder
- add status-processed / unprocessed folders for user feeback
- move output-backend ---> output script
- output/input-backend clean-up
- add images  support
- check if script is being executed from the project root
- dense reconstruction support for multiple gpus
- [error-handling / folder deletion] for Ctrl-C / unexpected script termination 
- update default bb params for pointcloud cropping
- user feedback mechanism 
- module post-processing cleaning => [vo / dense ]
- fix script kill issue
- modularize python script calls in main-file.sh 
- change output-dir name for p360 module
- tracking weight files
- check with p360 module works with updated PLY fsiles
- fix number of points in different in ply-rgb and ply-seg
- add labels to colmap points3d 


- update segmention module for better integration with p360
- add step by step error-handling in main-file.sh



comment

# SCRIPT [TO-DO]
# - sparse-reconstruction bash-based failure check not working
# - add RBA value check

# IMPORTANT SVO-FILES

# [CASE 1 -MEMORY CRASH]
# - /vineyards/gallo/2024_06_07_utc/svo_files/front_2024-06-04-11-34-23.svo


# ---------------------------------------------
# [VIRTUAL ENVIRONMENT CHECK]
# ---------------------------------------------
if [[ "$VIRTUAL_ENV" == "" ]]
then
    echo "No virtual environment found. Terminating script."
    exit 1
fi

# USER_INPUT="vineyards"
USER_INPUT="vineyards/gallo/2024_06_07_utc/svo_files/front_2024-06-04-11-34-23.svo"

INPUT_PATH="input-backend/svo-files/${USER_INPUT}"

SVO_FILES=$(python3 -c "import scripts.utils_module.bash_utils as io;  io.get_file_list('${INPUT_PATH}')")

for SVO_FILE in $SVO_FILES;
do
    echo -e "\n"
	echo "==============================="
	echo "SVO_FILE: $SVO_FILE"
	echo "==============================="
	echo -e "\n"
	
	SVO_STEP=2
	python3 -m scripts.vo.main \
	--i=$SVO_FILE \
	--svo_step=$SVO_STEP

	# generate the JSON containing viable svo segments ==> 
	# [[2, 93], 
	# [263, 364], 
	# [365, 431]]
	JSON_FILE=$(python3 -c "import scripts.vo.main as vo;  vo.get_json_path('${SVO_FILE}')")

	echo -e "\n"
	echo "==============================="
	echo "JSON_FILE: $JSON_FILE"
	echo "==============================="
	echo -e "\n"
	

	# generate multiple config files using the (above)JSON_FILE 
	# CONFIG_FILES => list of generated config files
	# config file => 
	# {
    # "SVO_FILENAME": "front_2023-11-03-11-18-57.svo",
    # "SVO_START_IDX": 126,
    # "SVO_END_IDX": 208
	# }
	CONFIG_FILES=$(python3 -c "import scripts.utils_module.bash_utils as io;  io.generate_config_files_from_json('${JSON_FILE}')")
	
	idx=1

	# looping main-file.sh with [CONFIG_FILE in CONFIG_FILES]
	for CONFIG_FILE in $CONFIG_FILES;
	do 
		echo -e "\n"
		echo "==============================="
		echo "idx: $idx"
		echo "CONFIG_FILE: $CONFIG_FILE"
		echo "==============================="
		echo -e "\n"

		# break

		# Use jq to parse the JSON and extract values
		SVO_FILENAME=$(jq -r '.SVO_FILENAME' "$CONFIG_FILE")
		SVO_START_IDX=$(jq -r '.SVO_START_IDX' "$CONFIG_FILE")
		SVO_END_IDX=$(jq -r '.SVO_END_IDX' "$CONFIG_FILE")
		FARM_TYPE="vineyards"

		echo -e "\n"
		echo "==============================="
		echo "SVO_FILENAME: $SVO_FILENAME"
		echo "SVO_START_IDX: $SVO_START_IDX"
		echo "SVO_END_IDX: $SVO_END_IDX"
		echo "==============================="
		echo -e "\n"

		# response=$(./main-file.sh "$SVO_FILENAME" "$SVO_START_IDX" "$SVO_END_IDX" "$SVO_STEP")
		./main-file.sh "$SVO_FILENAME" "$SVO_START_IDX" "$SVO_END_IDX" "$SVO_STEP" "$FARM_TYPE"
		exit_status=$?

		echo -e "\n"
		echo "==============================="
		echo "exit_status: $exit_status"
		echo "==============================="
		echo -e "\n"

		if [ $exit_status -eq 0 ]; then
        	echo "$CONFIG_FILE" >> end_to_end.log
    	fi


		((idx++))
	done

	# break
done

