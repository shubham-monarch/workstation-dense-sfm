#!/usr/bin/env python3

import open3d as o3d
import argparse
import logging, coloredlogs
from .p360_dataset import P360DatasetGenerator
import logging,coloredlogs

if __name__ == '__main__':
	coloredlogs.install(level='INFO', force=True)
	
	parser = argparse.ArgumentParser(description='Process some paths and bounding box.')
	parser.add_argument('--mode', type=str, choices=['RGB', 'SEGMENTED'], default="RGB", required=False, help='Specify mode: RGB or SEGMENTED')
	parser.add_argument('--bounding_box', type=int, nargs=6, required = True, help='Bounding box coordinates as six integers (min_x, max_x, min_y, max_y, min_z, max_z)')
	parser.add_argument('--dense_reconstruction_folder', type=str, required= True,  help='Path to the [cameras.bin, images.bin, points3D.bin] folder')
	parser.add_argument('--frame_to_frame_folder', type=str, required = True, help='camera-frame pointcloud directory')
	parser.add_argument('--frame_to_frame_folder_CROPPED', type=str, required = True, help='cropped camera-frame pointcloud directory')
	
	args = parser.parse_args()
	
	logging.info("=======================")
	logging.info(f"GENERATING [{args.mode}] FRAME-BY-FRAME POINTCLOUDS")
	logging.info("=======================")
	
	# bounding_box = tuple(args.bounding_box) 
	# sfm_path = args.dense_reconstruction_folder 
	# output_path = args.output_folder 


	p360_generator_ = P360DatasetGenerator(args.mode,
										   tuple(args.bounding_box), 
										   args.dense_reconstruction_folder, 
										   args.frame_to_frame_folder, 
										   args.frame_to_frame_folder_CROPPED)
	
	# cropping [1] frame every [10] frames
	frame_skip_rate = 10
	p360_generator_.generate(frame_skip_rate)

	# example usage
	# bounding_box = (-50, 50, -5, 5, -3, 3)
	# sfm_path = "/home/skumar/ext_ssd/workstation-sfm-setup/output-backend/dense-reconstruction/front_2023-11-03-11-18-57.svo/50_to_150"
	# output_path = 'framewise-ply/'  
	# p360_generator_ = P360DatasetGenerator(bounding_box, sfm_path, output_path)
	# #dataset_generator.generate()
	# p360_generator_.generate()
