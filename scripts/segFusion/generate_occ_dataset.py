#! /usr/bin/env python3

import os
import logging, coloredlogs
from scripts.utils_module import io_utils
from tqdm import tqdm
import sys
import argparse


def count_directories(path):
	return len([name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))])


if __name__ == "__main__":
	coloredlogs.install(level='INFO', force=True)

	logging.info("=======================")
	logging.info("GENERATING OCC DATASET")
	logging.info("=======================\n")
	
	parser = argparse.ArgumentParser()
	parser.add_argument("--f2f_RGB", type=str, required= True, help="Folder with frame-to-frame RGB PLY files")
	parser.add_argument("--f2f_SEG", type=str, required= True, help="Folder with frame-to-frame SEG PLY files")
	parser.add_argument("--f2f_LABELLED", type=str, required=True, help="Folder with frame-to-frame labeslled PLY files")
	parser.add_argument("--o", type=str, required=True, help="Output folder for the labelled PLY files")
	args = parser.parse_args()


	# frame_to_frame_RGB = "output-backend/frame-to-frame-rgb/RJM/2024_06_06_utc/svo_files/front_2024-06-05-09-09-54.svo/296_to_438"
	# frame_to_frame_SEGMENTED = "output-backend/frame-to-frame-segmented/RJM/2024_06_06_utc/svo_files/front_2024-06-05-09-09-54.svo/296_to_438"
	# labelled_pointclouds_SEGMENTED = "output-backend/labelled-pointclouds/RJM/2024_06_06_utc/svo_files/front_2024-06-05-09-09-54.svo/296_to_438"
	# output_folder="output/RJM/2024_06_06_utc/svo_files/front_2024-06-05-09-09-54.svo/296_to_438"

	frame_to_frame_RGB = args.f2f_RGB
	# frame_to_frame_SEGMENTED = args.f2f_SEG
	frame_to_frame_LABELLED = args.f2f_LABELLED
	
	output_folder= args.o

	rgb_count = count_directories(frame_to_frame_RGB)
	# segmented_count = count_directories(frame_to_frame_SEGMENTED)
	pointclouds_count = count_directories(frame_to_frame_LABELLED)

	# clear the output folder
	io_utils.delete_folders([output_folder])

	# if(rgb_count == segmented_count == pointclouds_count):
	if(rgb_count == pointclouds_count):
		
		# List directories in each path
		rgb_dirs = sorted([d for d in os.listdir(frame_to_frame_RGB) if os.path.isdir(os.path.join(frame_to_frame_RGB, d))])
		# segmented_dirs = sorted([d for d in os.listdir(frame_to_frame_SEGMENTED) if os.path.isdir(os.path.join(frame_to_frame_SEGMENTED, d))])
		pointclouds_dirs = sorted([d for d in os.listdir(frame_to_frame_LABELLED) if os.path.isdir(os.path.join(frame_to_frame_LABELLED, d))])

		
		for rgb_dir, labelled_dir in tqdm(zip(rgb_dirs,pointclouds_dirs), total=len(rgb_dirs)):
			# logging.info(f"rgb_dir: {rgb_dir}") 
			# logging.info(f"segmented_dir: {segmented_dir}")
			# logging.info(f"pointclouds_dir: {pointclouds_dir}")
			
			# generating [output/frame-334] folder
			frame_folder = os.path.join(output_folder, rgb_dir)
			io_utils.create_folders([frame_folder])
			
			# copying left RGB pointcloud to [frame_folder]
			ply_left_RGB = os.path.join(frame_to_frame_RGB, rgb_dir, "left.ply")
			io_utils.copy_file(ply_left_RGB, frame_folder, "left-rgb.ply")

			# # copying left segmented pointcloud to [frame_folder]
			# ply_left_SEGMENTED = os.path.join(frame_to_frame_SEGMENTED, segmented_dir, "left.ply")
			# io_utils.copy_file(ply_left_SEGMENTED, frame_folder, "left-segmented-labelled.ply")  
			
			# copying left labelled segmented pointcloud to [frame_folder]
			ply_left_LABELLED = os.path.join(frame_to_frame_LABELLED, labelled_dir, "left.ply")
			io_utils.copy_file(ply_left_LABELLED, frame_folder, "left-segmented-labelled.ply")  
			
			
			# copying left /right RGB images to [frame_folder]
			img_left_RGB = os.path.join(frame_to_frame_RGB, rgb_dir, "left.jpg")
			img_right_RGB = os.path.join(frame_to_frame_RGB, rgb_dir, "right.jpg")
			
			io_utils.copy_file(img_left_RGB, frame_folder)
			io_utils.copy_file(img_right_RGB, frame_folder)

	else:
		logging.error("The number of folders is not the same in all directories.")  
		sys.exit(1)