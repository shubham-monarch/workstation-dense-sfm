#!/usr/bin/env python3

import open3d as o3d
import argparse
import logging, coloredlogs
from .p360_dataset import P360DatasetGenerator
import logging,coloredlogs

if __name__ == '__main__':
	coloredlogs.install(level='INFO', force=True)
	
	parser = argparse.ArgumentParser(description='Process some paths and bounding box.')
	# parser.add_argument('--mode', type=str, choices=['RGB', 'SEGMENTED'], default="RGB", required=False, help='Specify mode: RGB or SEGMENTED')
	parser.add_argument('--bounding_box', type=int, nargs=6, required = True, help='Bounding box coordinates as six integers (min_x, max_x, min_y, max_y, min_z, max_z)')
	parser.add_argument('--dense_reconstruction_folder', type=str, required= True,  help='Path to the [cameras.bin, images.bin, points3D.bin] folder')
	parser.add_argument('--frame_to_frame_folder', type=str, required = True, help='camera-frame pointcloud directory')
	parser.add_argument('--frame_to_frame_folder_CROPPED', type=str, required = True, help='cropped camera-frame pointcloud directory')
	
	args = parser.parse_args()
	
	# Assuming args is the Namespace object returned by parser.parse_args()
	
	logging.info("=======================")
	logging.info(f"GENERATING FRAME-BY-FRAME POINTCLOUDS")
	logging.info("=======================\n")

	for arg, value in vars(args).items():
		logging.info(f"{arg}: {value}")
	
	p360_generator_ = P360DatasetGenerator(tuple(args.bounding_box), 
										   args.dense_reconstruction_folder, 
										   args.frame_to_frame_folder, 
										   args.frame_to_frame_folder_CROPPED)
	
	# generating camera-frame PLY for every [1 out of 5] frames
	# frame_skip_rate = 5
	frame_skip_rate = 1
	
	p360_generator_.generate(frame_skip_rate)