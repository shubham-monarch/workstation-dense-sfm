SVO_PATH=/home/skumar/front_svo/front_2023-11-03-10-51-17.svo
NUM_FRAMES=40
OUTPUT_DIR=/home/skumar/svo_output/

echo $SVO_PATH
echo $NUM_FRAMES   


python3 svo_to_pointcloud.py \
    --svo_path=$SVO_PATH \
    --num_frames=$NUM_FRAMES \
    --output_dir=$OUTPUT_DIR
