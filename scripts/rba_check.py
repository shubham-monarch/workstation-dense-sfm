#! /usr/bin/env python3

import logging,coloredlogs
import argparse
from read_write_model import read_images_binary, qvec2rotmat
import numpy as np
import os
import sys

def cam_extrinsics(img):
    R = qvec2rotmat(img.qvec)
    t = img.tvec.reshape(3,-1)
    R_t = np.concatenate((R,t), axis = 1)
    R_t = np.vstack([R_t, np.array([0,0,0,1])])
    return R_t   


'''
e_lw => left camera pose in world frame (4 * 4)
e_rw => right camera pose in world frame (4 * 4)
'''
def calculate_relative_pose(e_lw, e_rw): 
    from scipy.spatial.transform import Rotation
   
    e_wl = np.linalg.inv(e_lw)
    e_rl = np.dot(e_rw, e_wl)
    
    R = e_rl[:3,:3] #extracting the rotation matrix
    dx = e_rl[0,3]
    dy = e_rl[1,3]
    dz = e_rl[2,3]
    dquat = Rotation.from_matrix(R).as_quat()
    rel_pose = [dx,dy,dz]
    for q in dquat: 
        rel_pose.append(q)
    return rel_pose

def check_ba_convergence(rig_ba_rel_poses, threshold=0.01):
    """
    Checks if the bundle adjustment converged successfully by ensuring the standard deviation
    of dx, dy, dz across relative poses is below a certain threshold.
    
    Parameters:
    - rig_ba_rel_poses: List of relative poses, each containing [dx, dy, dz, qx, qy, qz, qw]
    - threshold: Maximum allowed standard deviation to consider as converged
    
    Returns:
    - True if the bundle adjustment converged successfully, False otherwise
    """
    # Extract dx, dy, dz from each relative pose
    translations = np.array(rig_ba_rel_poses)[:, :3]  # First three elements are dx, dy, dz
    
    # Calculate the standard deviation for dx, dy, dz
    std_dev = np.std(translations, axis=0)
    
    logging.warning(f"std_dev: {std_dev}")

    # Check if all standard deviations are below the threshold
    if np.all(std_dev < threshold):
        print("Bundle adjustment converged successfully.")
        return True
    else:
        print(f"Bundle adjustment did not converge successfully. Standard deviations: {std_dev}")
        return False


'''
check rba results for consistency
'''
def check_results(rba_folder: str) -> bool:
    
    images_BIN = f"{rba_folder}/images.bin"
    dict_images = read_images_binary(images_BIN) 
    num_images = len(dict_images)
    # logging.info(f"num_images in rba_folder: {num_images}")

    rel_poses = []

    # import numpy as np
    rig_ba_rel_poses = []
    num_images = len(dict_images.keys())
    for idx in range(1, num_images // 2):
        
        left_img = dict_images[idx]
        right_img = dict_images[idx + num_images // 2]
        e_lw = cam_extrinsics(left_img)  #left camera pose w.r.t. world
        e_rw = cam_extrinsics(right_img) #right camera pose w.r.t world
        rel_pose = calculate_relative_pose(e_lw, e_rw)
        rig_ba_rel_poses.append(rel_pose)

    flag = check_ba_convergence(rig_ba_rel_poses)
    logging.warning(f"flag: {flag}")
    return flag

    
if __name__ == "__main__":
    coloredlogs.install(level="DEBUG", force=True)  # install a handler on the root logger

    parser = argparse.ArgumentParser(description='Script to process a SVO file')
    parser.add_argument('--rba_output', type=str, required = True, help='Path to the rba output file')
    args = parser.parse_args()  
    logging.warning(f"[rba_check.py]")
    for key, value in vars(args).items():
        logging.info(f"{key}: {value}")

    success = check_results(args.rba_output)
    # success = False
    if success:
        logging.info("RBA results are consistent")
        sys.exit(0)
    else:
        logging.error("RBA results are not consistent")
        sys.exit(1)