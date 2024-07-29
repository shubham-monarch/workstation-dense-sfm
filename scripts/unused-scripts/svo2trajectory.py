#! /usr/bin/env python3 

import pyzed.sl as sl
import numpy as np
import cv2
import os
import matplotlib.pyplot as plt
import logging, coloredlogs
from tqdm import tqdm

import matplotlib.pyplot as plt

def plot_multidimensional_data(data):
    # Determine the number of dimensions
    num_dimensions = len(data[0])
    
    # Create a figure
    plt.figure(figsize=(10, num_dimensions * 2))
    
    for dim in range(num_dimensions):
        # Extract values for the current dimension
        dim_values = [point[dim] for point in data]
        
        # Plot values for the current dimension
        plt.subplot(num_dimensions, 1, dim + 1)
        plt.plot(dim_values, label=f'Dimension {dim + 1}')
        plt.title(f'Dimension {dim + 1} Values')
        plt.ylabel(f'Dim {dim + 1}')
        plt.grid(True)
    
    plt.xlabel('Data Point Index')
    plt.tight_layout()
    plt.show()

# def get_frame_count(svo_file_path: str) -> int:
    
#     init_params = sl.InitParameters(camera_resolution=sl.RESOLUTION.HD720,
#                                  coordinate_units=sl.UNIT.METER)
#                                 #  coordinate_system=sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP)
#     init_params.set_from_svo_file(svo_file_path)

    
#     zed = sl.Camera()
#     status = zed.open(init_params)
#     if status != sl.ERROR_CODE.SUCCESS:
#         print("Camera Open", status, "Exit program.")
#         exit(1)

    
#     tracking_params = sl.PositionalTrackingParameters() #set parameters for Positional Tracking
#     tracking_params.enable_imu_fusion = True
#     tracking_params.mode = sl.POSITIONAL_TRACKING_MODE.GEN_1
    
#     status = zed.enable_positional_tracking(tracking_params) #enable Positional Tracking
#     if status != sl.ERROR_CODE.SUCCESS:
#         print("[Sample] Enable Positional Tracking : "+repr(status)+". Exit program.")
#         zed.close()
#         exit()

    
#     runtime = sl.RuntimeParameters()
#     camera_pose = sl.Pose()
    
#     camera_info = zed.get_camera_information()
    
#     py_translation = sl.Translation()
#     pose_data = sl.Transform()

#     total_frames = zed.get_svo_number_of_frames()
    
#     ROTATION = []
#     TRANSLATION = []

#     for i in (range(0, total_frames - 1, 1)):
#         if zed.grab(runtime) == sl.ERROR_CODE.SUCCESS:
#             tracking_state = zed.get_position(camera_pose,sl.REFERENCE_FRAME.WORLD) #Get the position of the camera in a fixed reference frame (the World Frame)
#             # tracking_state = zed.get_position(camera_pose,sl.REFERENCE_FRAME.CAMERA) #Get the position of the camera in a fixed reference frame (the World Frame)
#             tracking_status = zed.get_positional_tracking_status()
#             # logging.info(f"{i} {tracking_state}")
#             #Get rotation and translation and displays it
#             if tracking_state == sl.POSITIONAL_TRACKING_STATE.OK:
#                 # logging.warning(f"Tracking state is OK at {i}th index!")
#                 rotation = camera_pose.get_rotation_vector()
#                 translation = camera_pose.get_translation(py_translation)
#                 # logging.info(f"translation: {translation.get()}")
#                 # ROTATION.append(rotation)
#                 # TRANSLATION.append(translation.get())
#                 # text_rotation = str((round(rotation[0], 2), round(rotation[1], 2), round(rotation[2], 2)))
#                 # text_translation = str((round(translation.get()[0], 2), round(translation.get()[1], 2), round(translation.get()[2], 2)))
#             # else:
#                 # logging.error(f"Tracking state at {i}th index: {tracking_state}")

#             pose_data = camera_pose.pose_data(sl.Transform())
#             logging.info(f"{pose_data.get_translation().get()}")
#             TRANSLATION.append(pose_data.get_translation().get())
#             # logging.info(f"type(pose_data): {type(pose_data)}")
#             # logging.info(f"dir(pose_data): {dir(pose_data)}")
#             # logging.info(f"pose_data: {pose_data}")
#             # break
#         else:
#             logging.error(f"Error gravving the {i}th frame!")
#             exit(1)

#     plot_multidimensional_data(TRANSLATION)

#     zed.close()


def extract_camera_pose(svo_file_path, viz=False):
    
    zed = sl.Camera()
    init_params = sl.InitParameters()
    init_params.set_from_svo_file(svo_file_path)
    init_params.svo_real_time_mode = False  # Don't play in real-time
    init_params.coordinate_units = sl.UNIT.METER

    status = zed.open(init_params)
    if status != sl.ERROR_CODE.SUCCESS:
        print(f"Error opening SVO file: {status}")
        return None

    # Enable positional tracking
    # tracking_params = sl.PositionalTrackingParameters()
    tracking_params = sl.PositionalTrackingParameters() #set parameters for Positional Tracking
    tracking_params.enable_imu_fusion = True
    tracking_params.mode = sl.POSITIONAL_TRACKING_MODE.GEN_1

    if zed.enable_positional_tracking(tracking_params) != sl.ERROR_CODE.SUCCESS:
        print(f"Error enabling positional tracking: {status}")
        return None

    # Prepare runtime parameters
    runtime_parameters = sl.RuntimeParameters()

    zed_pose = sl.Pose()
    poses = []
    i = 0

    total_frames = zed.get_svo_number_of_frames()
    for i in tqdm(range(0, total_frames - 1)):
        if zed.grab(runtime_parameters) == sl.ERROR_CODE.SUCCESS:
            state = zed.get_position(zed_pose, sl.REFERENCE_FRAME.CAMERA)
            # logging.info(f'{i} {state}')
            translation = zed_pose.get_translation(sl.Translation()).get()
            rotation = zed_pose.get_rotation_matrix().get_euler_angles()
            rotation_deg = np.degrees(rotation)

            # Rotation in rpy format
            pose = [translation[0], translation[1], translation[2], rotation_deg[0], rotation_deg[1], rotation_deg[2]]
            poses.append(pose[:3])
        else:
            break

    zed.close()
    poses_array = np.array(poses)
    # plot_multidimensional_data(poses_array)
    
    return poses_array

if __name__== '__main__':
    # main()
    coloredlogs.install(level="INFO", force=True)  # install a handler on the root logger
    SVO_FOLDER = f"../input/svo-files"
    SVO_FILE = "front_2023-11-03-10-46-17.svo"
    SVO_PATH=f"{SVO_FOLDER}/{SVO_FILE}"
    
    # get_frame_count(SVO_PATH)
    extract_camera_pose(SVO_PATH)
    # poses = extract_poses(SVO_PATH)