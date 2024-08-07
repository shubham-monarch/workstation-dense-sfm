#! /bin/bash

JSON_FILE="output-backend/vo/vineyards/gallo/2024_06_07_utc/svo_files/front_2024-06-04-12-45-25.json"
CONFIG_FILES=$(python3 -c "import scripts.utils_module.bash_utils as io;  io.generate_config_files_from_json('${JSON_FILE}')")

echo CONFIG_FILES: $CONFIG_FILES

# exit 1

for CONFIG_FILE in $CONFIG_FILES;
do 
    echo -e "\n"
    echo "==============================="
    echo "CONFIG_FILE: $CONFIG_FILE"
    echo "==============================="
    echo -e "\n"

    

    # # Use jq to parse the JSON and extract values
    # SVO_FILENAME=$(jq -r '.SVO_FILENAME' "$CONFIG_FILE")
    # SVO_START_IDX=$(jq -r '.SVO_START_IDX' "$CONFIG_FILE")
    # SVO_END_IDX=$(jq -r '.SVO_END_IDX' "$CONFIG_FILE")

    # # echo -e "\n"
    # # echo "==============================="
    # # echo "SVO_FILENAME: $SVO_FILENAME"
    # # echo "SVO_START_IDX: $SVO_START_IDX"
    # # echo "SVO_END_IDX: $SVO_END_IDX"
    # # echo "==============================="
    # # echo -e "\n"

    # response=$(./main-file.sh "$SVO_FILENAME" "$SVO_START_IDX" "$SVO_END_IDX")
    
    #     if [ $response -eq 0 ]; then
    #     echo "main-file.sh executed successfully."
    #     break # Exit the loop if main-file.sh was successful
    # else
    #     echo "main-file.sh failed. Continuing to the next CONFIG_FILE..."
    #     # Optionally, you can add an exit statement here to stop the script on failure
    #     # exit 1
    # fi
    # echo -e "\n"
    # echo "==============================="
    # echo "SVO_FILENAME: $SVO_FILENAME"
    # echo "SVO_START_IDX: $SVO_START_IDX"
    # echo "SVO_END_IDX: $SVO_END_IDX"
    # echo "response: $response"
    # echo "==============================="
    # echo -e "\n"

    # exit 1
done


