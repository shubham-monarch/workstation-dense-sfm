#! /usr/bin/env python3

import sys
import pyzed.sl as sl
import numpy as np
import cv2
import os
import shutil
import coloredlogs, logging
import time
from tqdm import tqdm
import matplotlib.pyplot as plt
import utils
import random
import argparse
import random





def run_zed_pipeline(svo_file): 	

	# FOLDER CREATION / DELETION FOR SVO FILE
	# svo_filename = os.path.basename(svo_file)
	ZED_BASE_FOLDER = "svo_images"
	ZED_IMAGES_DIR = f"{ZED_BASE_FOLDER}/{svo_file}"
	# ZED_LEFT_IMAGES_DIR = f"{ZED_IMAGES_DIR}/left"
	# ZED_RIGHT_IMAGES_DIR = f"{ZED_IMAGES_DIR}/right"
	PIPELINE_FOLDERS = [ZED_IMAGES_DIR]
	# deleting the old folders
	utils.delete_folders(PIPELINE_FOLDERS)
	# creating the new folders
	utils.create_folders(PIPELINE_FOLDERS)

	# return
	
	# ZED PROCESSING
	input_type = sl.InputType()
	input_type.set_from_svo_file(svo_file)
	
	init_params = sl.InitParameters(input_t=input_type, svo_real_time_mode=False)
	init_params.depth_mode = sl.DEPTH_MODE.ULTRA # Use ULTRA depth mode
	init_params.coordinate_units = sl.UNIT.METER # Use millimeter units (for depth measurements)
	
	zed = sl.Camera()
	status = zed.open(init_params)
	
	image_l = sl.Mat()
	image_r = sl.Mat()
	depth_map = sl.Mat()

	runtime_parameters = sl.RuntimeParameters()
	runtime_parameters.enable_fill_mode	= True
	
	total_svo_frames = zed.get_svo_number_of_frames()
	for i in tqdm(range(0, total_svo_frames - 1)):
		if zed.grab(runtime_parameters) == sl.ERROR_CODE.SUCCESS:
			
			# logging.debug(f"Processing {i}th frame!s")
			zed.set_svo_position(i)	
			zed.retrieve_image(image_l, sl.VIEW.LEFT) # Retrieve left image
			image_l.write( os.path.join(ZED_IMAGES_DIR , f'left_{i}.png') )
	zed.close()


if __name__ == '__main__':

	coloredlogs.install(level="DEBUG", force=True)  # install a handler on the root logger
	
	svo_files = []
	svo_folder = "escalon"
	num_svo_files_to_process = 10

	# Recursively iterate over all the files in the directory and its subdirectories
	for root, dirs, files in os.walk(svo_folder):
		for filename in files:
			svo_files.append(os.path.join(root, filename))

	random.shuffle(svo_files)			

	for file in svo_files:	
		try:
			run_zed_pipeline(file)
		except Exception as e:
			logging.error(f"Error in processing {file} : {e}")
			continue

