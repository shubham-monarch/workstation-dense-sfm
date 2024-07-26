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
			# ax.set_yticks(np.linspace(y_range[0], y_range[1], y_ticks))

	
	plt.xlabel('Data Point Index')
	plt.tight_layout()

	if output_folder is not None:
		# plt.show()
		utils.delete_folders([output_folder])
		utils.create_folders([output_folder])
		plt.savefig(f"{output_folder}/trajectory.png")
	
	plt.show()
	plt.close()


def get_imu_poses(svo_file_path):
	init_params = sl.InitParameters(camera_resolution=sl.RESOLUTION.HD720,
								 coordinate_units=sl.UNIT.METER)
	
	init_params.set_from_svo_file(svo_file_path)
	init_params.svo_real_time_mode = False
	
	zed = sl.Camera()
	status = zed.open(init_params)
	if status != sl.ERROR_CODE.SUCCESS:
		print("Camera Open", status, "Exit program.")
		exit(1)
	
	runtime = sl.RuntimeParameters()

	sensors_data = sl.SensorsData()

	total_frames = zed.get_svo_number_of_frames()
	imu_poses = []

	for i in tqdm(range(0, total_frames - 1)):
		if zed.grab(runtime) == sl.ERROR_CODE.SUCCESS:
			# tracking_state_camera = zed.get_position(pose_CAMERA_frame,sl.REFERENCE_FRAME.CAMERA)
	
			zed.get_sensors_data(sensors_data, sl.TIME_REFERENCE.IMAGE) #  Get frame synchronized sensor data

		# Extract multi-sensor data
			imu_data = sensors_data.get_imu_data()

			# logging.info(f"dir(imu_data): {dir(imu_data)}")
			# logging.info(f"pose: {imu_data.get_pose()}")
			
			imu_pose = imu_data.get_pose()
			translation = imu_pose.get_translation().get()
			rotation = imu_pose.get_rotation_matrix()

			imu_poses.append(translation)

			# logging.info(f"type(pose): {type(imu_pose)}")
			# logging.info(f"translation: {translation} type: {type(translation)}")
			# logging.info(f"rotation: {rotation} type: {type(rotation)}") 
			# break
	return imu_poses

def get_camera_poses(svo_file_path):
	init_params = sl.InitParameters(camera_resolution=sl.RESOLUTION.HD720,
								 coordinate_units=sl.UNIT.METER)
	
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

	tracking_params = sl.PositionalTrackingParameters(_enable_memory=True) #set parameters for Positional Tracking
	tracking_params.enable_imu_fusion = True
	tracking_params.mode = sl.POSITIONAL_TRACKING_MODE.GEN_1
	status = zed.enable_positional_tracking(tracking_params) #enable Positional Tracking
	if status != sl.ERROR_CODE.SUCCESS:
		print("[Sample] Enable Positional Tracking : "+repr(status)+". Exit program.")
		zed.close()
		exit()

	# logging.warning(f"tracking_params._enable_memory: {tracking_params._enable_memory}")

	runtime = sl.RuntimeParameters()
	
	pose_CAMERA_frame = sl.Pose()
	pose_WORLD_frame = sl.Pose()
	
	camera_info = zed.get_camera_information()
	py_translation = sl.Translation()
	
	poses_CAMERA_frame = []
	poses_WORLD_frame = []

	translation_WORLD_frame = sl.Translation()
	rotation_WORLD_frame = sl.Rotation()

	# translation_CAMERA_frame = sl.Translation()
	# rotation_CAMERA_frame = sl.Orientation()

	total_frames = zed.get_svo_number_of_frames()
	for i in range(0, total_frames - 1):
		
		if zed.grab(runtime) == sl.ERROR_CODE.SUCCESS:
			# tracking_state_camera = zed.get_position(pose_CAMERA_frame,sl.REFERENCE_FRAME.CAMERA)
			tracking_state_world = zed.get_position(pose_WORLD_frame,sl.REFERENCE_FRAME.WORLD) 
			tracking_status = zed.get_positional_tracking_status()

			if tracking_state_world == sl.POSITIONAL_TRACKING_STATE.OK:
			# if tracking_state_camera == sl.POSITIONAL_TRACKING_STATE.OK:
				# rotation_CAMERA_frame = pose_CAMERA_frame.get_rotation_matrix()
				# translation_CAMERA_frame = pose_CAMERA_frame.get_translation(py_translation)
				
				rotation_WORLD_frame = pose_WORLD_frame.get_rotation_matrix()
				# logging.info(f"type(rotation_WORLD_frame): {type(rotation_WORLD_frame)}")
				translation_WORLD_frame = pose_WORLD_frame.get_translation()
				
				# poses_CAMERA_frame.append(translation_CAMERA_frame.get())
				poses_WORLD_frame.append(translation_WORLD_frame.get())
				# logging.info(f"{i} {tracking_state_camera} {tracking_state_world}")
				logging.info(f"{i} {tracking_state_world}")
			else:
				logging.error(f"{i} {tracking_state_world}")	
			
			if i % 400 == 0:
				# logging.error(f"{i} {tracking_state_camera} {tracking_state_world}")
				logging.error(f"{i} {tracking_state_world}")
				logging.info("TRYING TO RESET POSITIONAL TRACKING")
				
				# generating world transform
				world_transform = sl.Transform()
				world_transform.set_translation(translation_WORLD_frame)
				world_transform.set_rotation_matrix(rotation_WORLD_frame)
				# world_transform.set_translation(sl.Translation(0, 0, 0))
				# world_transform.set_rotation_matrix(sl.Rotation(0, 0, 0))

				status = zed.reset_positional_tracking(world_transform)
				logging.info(f"status: {status}")
				if status != sl.ERROR_CODE.SUCCESS:
					logging.error("FAILED TO RESET POSITIONAL TRACKING")
				time.sleep(1)
				
		else : 
			time.sleep(0.001)
	
	zed.close()
	# poses_CAMERA_frame = np.array(poses_CAMERA_frame)
	# return poses_CAMERA_frame

	poses_WORLD_frame = np.array(poses_WORLD_frame)
	return poses_WORLD_frame

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
	# SVO_FILE = "front_2023-11-03-10-51-17.svo"
	# SVO_FILE = "front_2023-11-03-11-13-52.svo"
	# SVO_FILE = "front_2023-11-03-10-46-17.svo" --> FAILING
	SVO_FILE = "front_2024-05-15-18-59-18.svo"

	SVO_PATH=f"{INPUT_FOLDER}/{SVO_FILE}"   
	
	logging.info(f"output_folder: {OUTPUT_FOLER}")

	# utils.delete_folders([OUTPUT_FOLER])
	# utils.create_folders([OUTPUT_FOLER])

	# cam_poses = extract_camera_poses(SVO_PATH, OUTPUT_FOLER)
	# logging.info(f"len(cam_poses): {len(cam_poses)}")

	# segments = extract_forward_moving_segments(SVO_PATH)
	# logging.info(f"len(segments): {len(segments)}") 
	
	# translation_poses = get_camera_poses(SVO_PATH)
	# plot_data(translation_poses, y_range=(-20,1))
	# # for segment in segments:
	# # 	logging.info(f"segment: {segment}")
	
	imu_poses = get_imu_poses(SVO_PATH)
	logging.info(f"type(imu_poses): {type(imu_poses)}")
	plot_data(imu_poses)

	# project directories
	
	
	
