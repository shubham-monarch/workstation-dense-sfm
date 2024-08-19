#!/bin/bash

# redirecting all output to a log.main 
# exec >> logs/main.log 2>&1


# ---------------------------------------------
# [VIRTUAL ENVIRONMENT CHECK]
# ---------------------------------------------
if [[ "$VIRTUAL_ENV" == "" ]]
then
    echo "No virtual environment found. Terminating script."
    exit 1
fi



INPUT_PATH=input-backend/svo-files
INDEX_FILE=index/svo_index.json

echo -e "\n"
echo "==============================="	
echo "INPUT_PATH: $INPUT_PATH"
echo "==============================="
echo -e "\n"


SVO_FILES=$(python3 -c "import scripts.utils_module.bash_utils as io;  io.get_file_list('${INPUT_PATH}')")

counter=1
for SVO_FILE in $SVO_FILES;
do
    echo -e "\n"
	echo "==============================="
	echo "Processing #$counter: $SVO_FILE"
	echo "==============================="
	echo -e "\n"
	
	python3 -m scripts.utils_module.bash_modules.update_svo_index \
		--svo_file $SVO_FILE \
		--index_file $INDEX_FILE
	
	counter=$((counter + 1))
done

