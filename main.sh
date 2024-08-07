#!/bin/bash

<<comment
[TO-DO]

- aws api integration
- aws / local input detection
- pointcloud labelling
- pointcloud cropping script
- output-backend -> output folder
- aws instance setup
	- add colmap cmake update to sssssssssupport pycolmap installtion 
	- retag colmap , pycolmap
	- update requirements.txt
	- update pipeline tag
- processed/unprocessed folders
	- add svo files
	- cleanup before running the pipeline
- documentation
	- update release notes
	- update installation steps
	- add + update setup.md
	- add readme.md
	- update colmap installation steps in setup.md
- add segmentation inference script
- output/input-backend clean-up
- add images support
- check if script is being executed from the project root
- dense reconstruction support for multiple gpus
- [error-handling / folder deletion] for Ctrl-C / unexpected script termination 
- update default bb params for pointcloud cropping
- return -1 for failed jsons
- implement svo-filter.py
- integrate svo-filter.py with main.sh	

[LATER]
- add colmap cmake update to support pycolmap installtion 
- retag colmap , pycolmap
- update requirements.txt
- update pipeline tag
- cleanup for all the modules
- documentation
	- update release notes
	- update installation steps
	- add + update setup.md
	- add readme.md
	- update colmap installation steps in setup.md
- refactoring
	- add python-scripts / bash-scripts
	- refactor script folders into separate modules
- new scripts
	- add main-ws.sh, main-aws.sh
	- aws integration
	- add status-processed / unprocessed folders for user feeback
	- add segmentation inference script
	- move output-backend ---> output script
	- add folder / file support
	- add parent + child config file/script
	- python for config parsing
	- output/input-backend clean-up
- add images  support
- check if script is being executed from the project root
- dense reconstruction support for multiple gpus
- [error-handling / folder deletion] for Ctrl-C / unexpected script termination 
- update default bb params for pointcloud cropping
- user feedback mechanism 
- temp file deletion sttrategy
- include zed baseline extraction
- sync frame extraction

comment

# ---------------------------------------------
# [VIRTUAL ENVIRONMENT CHECK]
# ---------------------------------------------
if [[ "$VIRTUAL_ENV" == "" ]]
then
    echo "No virtual environment found. Terminating script."
    exit 1
fi

USER_INPUT="vineyards"
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

	JSON_FILE=$(python3 -c "import scripts.vo.main as vo;  vo.get_json_path('${SVO_FILE}')")

	echo -e "\n"
	echo "==============================="
	echo "JSON_FILE: $JSON_FILE"
	echo "==============================="
	echo -e "\n"
	
	CONFIG_FILES=$(python3 -c "import scripts.utils_module.bash_utils as io;  io.generate_config_files_from_json('${JSON_FILE}')")
	
	idx=1
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

		echo -e "\n"
		echo "==============================="
		echo "SVO_FILENAME: $SVO_FILENAME"
		echo "SVO_START_IDX: $SVO_START_IDX"
		echo "SVO_END_IDX: $SVO_END_IDX"
		echo "==============================="
		echo -e "\n"

		# response=$(./main-file.sh "$SVO_FILENAME" "$SVO_START_IDX" "$SVO_END_IDX" "$SVO_STEP")
		./main-file.sh "$SVO_FILENAME" "$SVO_START_IDX" "$SVO_END_IDX" "$SVO_STEP"
		exit_status=$?
		
		echo -e "\n"
		echo "==============================="
		echo "exit_status: $exit_status"
		echo "==============================="
		echo -e "\n"

		((idx++))
	done

	break
done

