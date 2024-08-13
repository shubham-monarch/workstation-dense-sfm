#!/bin/bash

# IMPORTANT SVO-FILES

# [CASE 1 -MEMORY CRASH]
# - /vineyards/gallo/2024_06_07_utc/svo_files/front_2024-06-04-11-34-23.svo

# [TO-DO]:
# - fix dense-reconstruction crashing
# - change cuda version to 11.0 
# - run steps after dense-reconstruction
# - failed dense-folder deletion not working
# - log the main.sh output to date-based logging
# - final folder output logging
# - update folder deletion / checking logic

# ---------------------------------------------
# [VIRTUAL ENVIRONMENT CHECK]
# ---------------------------------------------
if [[ "$VIRTUAL_ENV" == "" ]]
then
    echo "No virtual environment found. Terminating script."
    exit 1
fi

# crash
# USER_INPUT="vineyards/gallo/2024_06_07_utc/svo_files/front_2024-06-04-11-29-22.svo"


<<<<<<< HEAD
USER_INPUT="vineyards/RJM/"
=======
USER_INPUT="RJM"
>>>>>>> dev-ec2
INPUT_PATH="input-backend/svo-files/${USER_INPUT}"

echo -e "\n"
echo "==============================="	
echo "Memory usage before loading SVO_FILES"
free -m | grep Mem | awk '{print "Total: "$2"MB Used: "$3"MB Free: "$4"MB"}'
echo "==============================="
echo -e "\n"


SVO_FILES=$(python3 -c "import scripts.utils_module.bash_utils as io;  io.get_file_list('${INPUT_PATH}')")

echo -e "\n"
echo "==============================="	
echo "Memory usage after loading SVO_FILES"
free -m | grep Mem | awk '{print "Total: "$2"MB Used: "$3"MB Free: "$4"MB"}'
echo "==============================="
echo -e "\n"
	
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

