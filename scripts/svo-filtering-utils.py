#! /usr/bin/env python 

import pyzed.sl as sl
import logging, coloredlogs
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
import utils
import os
from typing import List, Tuple
import time


# CASES
# 1. low lighting
# 2. sharp turns
# 3. no movement
# 4. negative velocity

# project directories
PROJECT_DIR=f"../"
PROJECT_INPUT_FOLER=f"{PROJECT_DIR}/input/"
PROJECT_OUTPUT_FOLDER=f"{PROJECT_DIR}/output"



# Define filter functions
def low_light_filter(frame_sequences):
	# Implement low light filtering logic
	# return filtered_sequences
	pass

def no_camera_movement_filter(frame_sequences):
	# Implement no camera movement filtering logic
	# return filtered_sequences
	pass

def camera_moving_back_filter(frame_sequences):
	# Implement camera moving back filtering logic
	# return filtered_sequences
	pass

def sharp_movements_filter(frame_sequences):
	# Implement sharp/sudden movements filtering logic
	# return filtered_sequences
	pass

# Initialize the filter pipeline
filter_pipeline = [
	low_light_filter,
	no_camera_movement_filter,
	camera_moving_back_filter,
	sharp_movements_filter
]

def apply_filters(frame_sequences, filters):
	for filter_func in filters:
		frame_sequences = filter_func(frame_sequences)
	return frame_sequences

 
def plot_data(data, output_folder=None, labels=None, x_range=None, y_range=None, x_tivcks=None, y_ticks=None):
	# Determine the number of dimensions
	num_dimensions = len(data[0])
	
	# Create a figure
	plt.figure(figsize=(10, num_dimensions * 2))
	
	for dim in range(num_dimensions):
		# Extract values for the current dimension
		dim_values = [point[dim] for point in data]
		
		# Plot values for the current dimension
		ax = plt.subplot(num_dimensions, 1, dim + 1)
		ax.plot(dim_values, label=f'Dimension {dim + 1}')
		ax.set_title(f'Dimension {dim + 1} Values')
		
		if labels is None:
			ax.set_ylabel(f'Dim {dim + 1}')
		else: 
			ax.set_ylabel(labels[dim])
		
		ax.grid(True)
		
		# Set x-axis and y-axis range if specified
		if x_range:
			ax.set_xlim(x_range)
		if y_range:
			ax.set_ylim(y_range)
			ax.set_yticks(np.linspace(y_range[0], y_range[1], y_ticks))

	
	plt.xlabel('Data Point Index')
	plt.tight_layout()

	if output_folder is not None:
		# plt.show()
		utils.delete_folders([output_folder])
		utils.create_folders([output_folder])
		plt.savefig(f"{output_folder}/trajectory.png")
	
	plt.show()
	plt.close()


def get_camera_poses(svo_file_path):
	init_params = sl.InitParameters(camera_resolution=sl.RESOLUTION.HD720,
								 coordinate_units=sl.UNIT.METER,
								 coordinate_system=sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP)
	
	init_params.set_from_svo_file(svo_file_path)
	init_params.svo_real_time_mode = False
	
	zed = sl.Camera()
	status = zed.open(init_params)
	if status != sl.ERROR_CODE.SUCCESS:
		print("Camera Open", status, "Exit program.")
		exit(1)

	# if len(opt.roi_mask_file) > 0:
	# 	mask_roi = sl.Mat()
	# 	err = mask_roi.read(opt.roi_mask_file)
	# 	if err == sl.ERROR_CODE.SUCCESS:
	# 		zed.set_region_of_interest(mask_roi, [sl.MODULE.ALL])
	# 	else:
	# 		print(f"Error loading Region of Interest file {opt.roi_mask_file}. Please check the path.")

	tracking_params = sl.PositionalTrackingParameters() #set parameters for Positional Tracking
	tracking_params.enable_imu_fusion = True
	tracking_params.mode = sl.POSITIONAL_TRACKING_MODE.GEN_1
	status = zed.enable_positional_tracking(tracking_params) #enable Positional Tracking
	if status != sl.ERROR_CODE.SUCCESS:
		print("[Sample] Enable Positional Tracking : "+repr(status)+". Exit program.")
		zed.close()
		exit()

	runtime = sl.RuntimeParameters()
	camera_pose = sl.Pose()

	
	camera_info = zed.get_camera_information()
	py_translation = sl.Translation()
	pose_data = sl.Transform()
	cam_poses = []
	
	total_frames = zed.get_svo_number_of_frames()
	for i in range(0, total_frames - 1):
		if zed.grab(runtime) == sl.ERROR_CODE.SUCCESS:
			tracking_state = zed.get_position(camera_pose,sl.REFERENCE_FRAME.WORLD) #Get the position of the camera in a fixed reference frame (the World Frame)
			tracking_status = zed.get_positional_tracking_status()

			#Get rotation and translation and displays it
			if tracking_state == sl.POSITIONAL_TRACKING_STATE.OK:
				rotation = camera_pose.get_rotation_vector()
				translation = camera_pose.get_translation(py_translation)
				cam_poses.append(translation.get())
				logging.info(f"{i} {translation.get()}")
				# text_rotation = str((round(rotation[0], 2), round(rotation[1], 2), round(rotation[2], 2)))
				# text_translation = str((round(translation.get()[0], 2), round(translation.get()[1], 2), round(translation.get()[2], 2)))

			pose_data = camera_pose.pose_data(sl.Transform())
			# Update rotation, translation and tracking state values in the OpenGL window
			
		else : 
			time.sleep(0.001)
	# viewer.exit()
	zed.close()
	cam_poses = np.array(cam_poses)
	logging.info(f"cam_poses.shape: {cam_poses.shape}")
	return cam_poses

# TO-DO -> 
# - add roi auto detection
# - read documentation

if __name__ == "__main__":
	
	coloredlogs.install(level="INFO", force=True)  
	# initial_frame_sequences = [(0, 20), (32, 89)]  # Example initial frame sequences
	# viable_frame_sequences = apply_filters(initial_frame_sequences, filter_pipeline)
	# process_viable_frame_sequences(viable_frame_sequences)   
	
	# svo-filtering directories
	INPUT_FOLDER = f"{PROJECT_INPUT_FOLER}/svo-files"
	OUTPUT_FOLER=f"{PROJECT_OUTPUT_FOLDER}/filtered-svo-files"
	SVO_FILE = "front_2023-11-03-10-51-17.svo"
	SVO_PATH=f"{INPUT_FOLDER}/{SVO_FILE}"   
	
	logging.info(f"output_folder: {OUTPUT_FOLER}")

	# utils.delete_folders([OUTPUT_FOLER])
	# utils.create_folders([OUTPUT_FOLER])

	# cam_poses = extract_camera_poses(SVO_PATH, OUTPUT_FOLER)
	# logging.info(f"len(cam_poses): {len(cam_poses)}")

	# segments = extract_forward_moving_segments(SVO_PATH)
	# logging.info(f"len(segments): {len(segments)}") 
	
	translation_poses = get_camera_poses(SVO_PATH)
	plot_data(translation_poses)
	# for segment in segments:
	# 	logging.info(f"segment: {segment}")
	
	# project directories
	
	
	
