#! /usr/bin/env python3 

import pyzed.sl as sl
import numpy as np
import cv2
import os
import matplotlib.pyplot as plt
import logging, coloredlogs

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
    tracking_params = sl.PositionalTrackingParameters()
    if zed.enable_positional_tracking(tracking_params) != sl.ERROR_CODE.SUCCESS:
        print(f"Error enabling positional tracking: {status}")
        return None

    # Prepare runtime parameters
    runtime_parameters = sl.RuntimeParameters()

    zed_pose = sl.Pose()
    poses = []
    i = 0

    logging.warning(f"Total #frames : {zed.get_svo_number_of_frames()}")
    total_frames = zed.get_svo_number_of_frames()
    for i in range(0, total_frames-1):
        if zed.grab(runtime_parameters) == sl.ERROR_CODE.SUCCESS:
            
            # if viz:
            #     if i%10 == 0:
            #         img = sl.Mat()
            #         zed.retrieve_image(img, sl.VIEW.LEFT)
            #         if os.path.exists("viz") == False:
            #             os.makedirs("viz")
            #         path = os.path.join("viz", f"frame_{i}.png")
            #         cv2.imwrite(path, img.get_data())

            
            state = zed.get_position(zed_pose, sl.REFERENCE_FRAME.WORLD)
            translation = zed_pose.get_translation(sl.Translation()).get()
            rotation = zed_pose.get_rotation_matrix().get_euler_angles()
            rotation_deg = np.degrees(rotation)

            # Rotation in rpy format
            pose = [translation[0], translation[1], translation[2], rotation_deg[0], rotation_deg[1], rotation_deg[2]]
            poses.append(pose)
        else:
            break

    zed.close()
    poses_array = np.array(poses)
    
    return poses_array

def plot_poses(poses_array):

    fig, axs = plt.subplots(2, 3, figsize=(20, 10))
    fig.suptitle("Camera Pose")

    axs[0, 0].plot(poses_array[:, 0])
    axs[0, 0].set_title("X")

    axs[0, 1].plot(poses_array[:, 1])
    axs[0, 1].set_title("Y")

    axs[0, 2].plot(poses_array[:, 2])
    axs[0, 2].set_title("Z")

    axs[1, 0].plot(poses_array[:, 3])
    axs[1, 0].set_title("Roll")

    axs[1, 1].plot(poses_array[:, 4])
    axs[1, 1].set_title("Pitch")

    axs[1, 2].plot(poses_array[:, 5])
    axs[1, 2].set_title("Yaw")

    plt.show()

def calculate_velocities(poses_array, time_interval):
    linear_velocities = np.diff(poses_array[:, :3], axis=0) / time_interval
    angular_velocities = np.diff(poses_array[:, 3:], axis=0) / time_interval
    
    return linear_velocities, angular_velocities

def identify_smooth_segments(poses_array, time_interval, max_linear_velocity, max_angular_velocity):
    linear_velocities, angular_velocities = calculate_velocities(poses_array, time_interval)
    
    # Identify indices where velocities are below thresholds
    smooth_linear = np.all(np.abs(linear_velocities) < max_linear_velocity, axis=1)
    smooth_angular = np.all(np.abs(angular_velocities) < max_angular_velocity, axis=1)
    smooth = smooth_linear & smooth_angular

    # Identify continuous segments of smooth movement
    segments = []
    start_idx = None
    for i, is_smooth in enumerate(smooth):
        if is_smooth and start_idx is None:
            start_idx = i
        elif not is_smooth and start_idx is not None:
            segments.append((start_idx, i))
            start_idx = None
    
    # Edge case when segment extends past end of array
    if start_idx is not None:
        segments.append((start_idx, len(smooth)))
    
    return segments


def main():
    coloredlogs.install(level="INFO", force=True)  # install a handler on the root logger
    # Example usage
    SVO_FOLDER = f"../input/svo-files"
    # svo_file = "front_2024-04-17-08-23-26.svo"
    svo_file = "front_2024-02-14-05-22-20.svo"
    SVO_FILE_PATH=f"{SVO_FOLDER}/{svo_file}"
    # poses_array = extract_camera_pose(svo_file_path, False)
    poses_array = extract_camera_pose(SVO_FILE_PATH, False)
    # print(poses_array)
    # plot_poses(poses_array)
    time_interval = 0.1
    
    velocity_arr, _ = calculate_velocities(poses_array, time_interval)
    
    
    x_velocity = velocity_arr[:, 0]  # Extract the first column for x-velocity

    # Generate an array of indices/time points for the x-axis
    time_points = np.arange(len(x_velocity))

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(time_points, x_velocity, label='X-Velocity')
    plt.title('X-Velocity over Time')
    plt.xlabel('Time Point')
    plt.ylabel('X-Velocity')
    plt.legend()
    plt.show()


    logging.info(f"len(velocity_arr) : {len(velocity_arr)}")
    
    max_linear_velocity = 8
    max_angular_velocity = 100
    
    # segments = identify_smooth_segments(poses_array, time_interval, max_linear_velocity, max_angular_velocity)
    # print(segments)

if __name__== '__main__':
    main()
