#! /usr/bin/env python3

import logging,coloredlogs
import argparse
from read_write_model import read_images_binary, qvec2rotmat
import numpy as np

def cam_extrinsics(img):
    R = qvec2rotmat(img.qvec)
    t = img.tvec.reshape(3,-1)
    R_t = np.concatenate((R,t), axis = 1)
    R_t = np.vstack([np.array([0,0,0,1]), R_t])
    return R_t   


'''
e_lw => left camera pose in world frame (4 * 4)
e_rw => right camera pose in world frame (4 * 4)
'''
def calculate_relative_pose(e_lw, e_rw): 
    from scipy.spatial.transform import Rotation
    e_rl = e_rw * np.linalg.inv(e_lw) #right camera in the frame of the left camera
    R = e_rl[:3,:3] #extracting the rotation matrix
    dx = e_rl[0,3]
    dy = e_rl[1,3]
    dz = e_rl[2,3]
    dquat = Rotation.from_matrix(R).as_quat()
    #rel_pose =  [dx, dy] + dquat
    rel_pose = [dx,dy,dz]
    for q in dquat: 
        rel_pose.append(q)
    return rel_pose
    #return [dx,dy]
    #print(f"dx: {dx} dy: {dy} dquat: {dquat}")


def main(rba_folder):
    
    images_BIN = f"{rba_folder}/images.bin"
    dict_images = read_images_binary(images_BIN) 
    num_images = len(dict_images)
    logging.info(f"num_images in rba_folder: {num_images}")

    # for k, v in dict_images.items():
    #     logging.info(f"{k} {v.name}")
        # break

    rel_poses = []

    for idx in range(1, num_images // 2 ):
        # print(f"Image {idx}: {dict_images[idx]}")
        img_left = dict_images[idx]
        img_right = dict_images[idx + (num_images // 2)]
        logging.info(f"{img_left.name} {img_right.name}")
        E_LW = cam_extrinsics(img_left)  # left camera pose w.r.t world
        E_RW = cam_extrinsics(img_right) # right camera pose w.r.t world
        rel_pose = calculate_relative_pose(E_LW, E_RW)     
        rel_poses.append(rel_pose)

    logging.warning(f"Relative camera poses after RBA =>")    
    for pose in rel_poses:
            logging.info(pose[:3])

    
if __name__ == "__main__":
    coloredlogs.install(level="DEBUG", force=True)  # install a handler on the root logger

    parser = argparse.ArgumentParser(description='Script to process a SVO file')
    parser.add_argument('--rba_output', type=str, required = True, help='Path to the rba output file')
    args = parser.parse_args()  
    
    logging.warning(f"[rba.py]")

    main(args.rba_output)