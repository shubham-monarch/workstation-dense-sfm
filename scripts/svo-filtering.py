#! /usr/bin/env python 

import pyzed.sl as sl
import logging, coloredlogs
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
import utils
import os


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

# Example usage
initial_frame_sequences = [(0, 20), (32, 89)]  # Example initial frame sequences
viable_frame_sequences = apply_filters(initial_frame_sequences, filter_pipeline)


'''
plotting multidimensional data
'''
def plot_data(data, output_folder, labels = None):
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
        if labels is None:
            plt.ylabel(f'Dim {dim + 1}')
        else: 
            plt.ylabel(labels[dim])
        plt.grid(True)
    
    plt.xlabel('Data Point Index')
    plt.tight_layout()

    utils.delete_folders([output_folder])
    utils.create_folders([output_folder])
    
    plt.savefig(f"{output_folder}/trajectory.png")
    plt.show()
    plt.close()

'''
extract the z-direction camera poses
'''
def extract_camera_poses(svo_file : str, output_folder : str) -> np.ndarray:
    
    zed = sl.Camera()
    init_params = sl.InitParameters()
    init_params.set_from_svo_file(svo_file)
    init_params.svo_real_time_mode = False  # Don't play in real-time
    init_params.coordinate_units = sl.UNIT.METER

    status = zed.open(init_params)
    if status != sl.ERROR_CODE.SUCCESS:
        print(f"Error opening SVO file: {status}")
        return None

    # Enable positional tracking
    tracking_params = sl.PositionalTrackingParameters()
    if zed.enable_positional_tracking(tracking_params) != sl.ERROR_CODE.SUCCESS:
        print(f"Error enabling positional tracking: {status}")
        return None

    # Prepare runtime parameters
    runtime_parameters = sl.RuntimeParameters()

    zed_pose = sl.Pose()
    svo_poses = []
    
    total_frames = zed.get_svo_number_of_frames()
    for i in tqdm(range(0, total_frames - 1)):
        if zed.grab(runtime_parameters) == sl.ERROR_CODE.SUCCESS:
            state = zed.get_position(zed_pose, sl.REFERENCE_FRAME.CAMERA)
            translation = zed_pose.get_translation(sl.Translation()).get()
            rotation = zed_pose.get_rotation_matrix().get_euler_angles()
            rotation_deg = np.degrees(rotation)

            # Rotation in rpy format
            pose = [translation[0], translation[1], translation[2], rotation_deg[0], rotation_deg[1], rotation_deg[2]]
            svo_poses.append(pose[:1])
        else:
            break

    zed.close()
    svo_poses = np.array(svo_poses)
    filename = os.path.basename(svo_file)
    plot_data(svo_poses, f"{output_folder}/{filename}", labels=['z'])
    return svo_poses


if __name__ == "__main__":
    
    coloredlogs.install(level="INFO", force=True)  
    # initial_frame_sequences = [(0, 20), (32, 89)]  # Example initial frame sequences
    # viable_frame_sequences = apply_filters(initial_frame_sequences, filter_pipeline)
    # process_viable_frame_sequences(viable_frame_sequences)   
    
    # svo-filtering directories
    INPUT_FOLDER = f"{PROJECT_INPUT_FOLER}/svo-files"
    OUTPUT_FOLER=f"{PROJECT_OUTPUT_FOLDER}/filtered-svo-files"
    SVO_FILE = "front_2023-11-03-10-46-17.svo"
    SVO_PATH=f"{INPUT_FOLDER}/{SVO_FILE}"   
    
    logging.info(f"output_folder: {OUTPUT_FOLER}")

    utils.delete_folders([OUTPUT_FOLER])
    utils.create_folders([OUTPUT_FOLER])

    extract_camera_poses(SVO_PATH, OUTPUT_FOLER)

    # project directories
    
    
    
