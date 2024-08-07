#! /usr/bin/env python3

import os

import numpy as np
import cv2
import argparse
import yaml
import logging, coloredlogs
from tqdm import tqdm

from scripts.vo.utils.tools import plot_keypoints
from scripts.vo.utils.vis_helpers import plot_histograms
from scripts.utils_module.io_utils import create_folders, delete_folders

# from scripts.vo.DataLoader import create_dataloader
from scripts.vo.Detectors import create_detector
from scripts.vo.Matchers import create_matcher
from scripts.vo.VO.VisualOdometry import VisualOdometry, AbosluteScaleComputer
from scripts.vo.DataLoader import ZEDLoader
import time
import matplotlib.pyplot as plt
import fnmatch
import shutil
import random
import json

# from scripts.vo.svo_to_stereo_images import get_camera_params
# from scripts.vo import svo_to_stereo_images
from scripts.utils_module import zed_utils


#[TO-DO]
# - error-handling =>  vineyards/front_2024-06-05-09-48-13.svo
# - handling large continuos valid segment
# - sampling viable segments
# - integrate with main.sh
# - integrate svo-extraction

def keypoints_plot(img, vo):
    if img.shape[2] == 1:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    return plot_keypoints(img, vo.kptdescs["cur"]["keypoints"], vo.kptdescs["cur"]["scores"])


# def write_seq_to_disk(input_dir : str, sequences : tuple, output_dir = "outputs"):
    
#     input_dir_ = os.path.join("test_imgs/sequences/00/", input_dir)

#     img_N = len([file for file in os.listdir(input_dir_) if file.endswith('.png')]) 
#     # logging.info(f"num_images: {img_N}")   
    
#     images_list = os.listdir(input_dir_)
#     filtered_files = fnmatch.filter(images_list, "left_*.png")
#     sorted_images = sorted(filtered_files, key=lambda x: int(x.split('_')[1].split('.')[0]))
    
#     # updating sorted images with full path
#     for i, image in enumerate(sorted_images):
#         image = os.path.join(input_dir_, image) 
#         sorted_images[i] = image

#     output_dir = os.path.join(output_dir, input_dir)
#     for (st,en) in tqdm(sequences):
#         output_dir_ = os.path.join(output_dir, f"{st}_{en}")
    
#         # logging.warning(f"output_dir: {output_dir_}")
        
#         delete_folders([output_dir_])
#         create_folders([output_dir_])
        
#         for i in range(st, en + 1):
#             # logging.info(f"{i}: {sorted_images[i]}")
#             shutil.copy(sorted_images[i], output_dir_)    
    

# required by main.sh
def get_json_path(svo_path : str, input_root=None, output_root=None):
    # print (svo_path)
    if input_root is None:
        input_root = "input-backend/svo-files"
    if output_root is None:
        output_root = "output-backend/vo"
    
    # removing "input-backend/svo-files" from the json-path
    json_path = os.path.relpath(svo_path, input_root)
    
    # prepeding "output-backend/vo" to the json-path
    json_path = os.path.join(output_root, json_path)

    # replacing ".svo" with ".json"
    json_path = json_path.replace(".svo", ".json")

    print(json_path)

def run(args, svo_folder_path : str, camera_params : dict): 
    with open(args.config, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    
    loader = ZEDLoader.KITTILoader(config, svo_folder_path, camera_params)
    
    detector = create_detector(config["detector"])
    matcher = create_matcher(config["matcher"])

    absscale = AbosluteScaleComputer()
    
    logging.warning("=======================")
    zed_camera = loader.cam
    for attr, value in zed_camera.__dict__.items():
        logging.info(f"{attr}: {value}")
    logging.warning("=======================")
                
    total_frames = len(loader)
    
    vo = VisualOdometry(detector, matcher, zed_camera, total_frames)
    
    for i, img in enumerate(loader):
        
        logging.warning(f"PROCESSING [{i} / {total_frames}] FRAME")
        
        R, t = vo.update(img)
        
        img1 = keypoints_plot(img, vo)
    
        cv2.imshow("keypoints", img1)
        if cv2.waitKey(10) == 27:
            break

    cv2.destroyAllWindows()
    
    logging.info("=======================")
    logging.info("VO HAS FINISHED!")
    logging.info("=======================")
    
    return vo


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='python_vo')    
    parser.add_argument('--config', type=str, default='scripts/vo/params/kitti_superpoint_flannmatch.yaml',
                        help='config file')
    # parser.add_argument('--o', type=str, default = "output-backend/vo", help='Root output directory')
    parser.add_argument('--i', type=str, required= True, help='Path to input svo files / folder')
    parser.add_argument('--svo_step', type=int, required= False, default=2, help='Extract every n-th frame from the SVO file')

    
    # root folders for svo-filtering
    ROOT_OUTPUT = "input-backend/vo"
    ROOT_INPUT = "input-backend/svo-files"
    
    # root folders for valid sequences
    ROOT_VALID_SEQ = "output-backend/vo"


    args = parser.parse_args()
    coloredlogs.install(level='INFO', force=True)
    
    with open(args.config, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    
    # storing rel and abs paths for svo files
    svo_path_abs = []
    svo_path_rel = []
    logging.info(f"args.i: {args.i}")
    print(f"input: {args.i}")

    
    if os.path.isfile(args.i):
        svo_path_abs.append(args.i)
        svo_path_rel.append(os.path.relpath(args.i, ROOT_INPUT))
    elif os.path.isdir(args.i):
        for dirpath, dirnames, filenames in os.walk(args.i):
            for filename in filenames:
                if filename.endswith('.svo'):
                    svo_path_abs.append(os.path.join(dirpath, filename))
                    svo_path_rel.append(os.path.relpath(os.path.join(dirpath, filename), ROOT_INPUT))

    
    random.shuffle(svo_path_rel)

    # svo_path_rel = ['vineyards/RJM/front_2024-06-05-09-48-13.svo']

    for i, svo_folder in enumerate(svo_path_rel):
        
        logging.warning("=======================")
        logging.warning(f"svo_file: {svo_folder}")
        logging.warning("=======================")
        
        output_path = os.path.join(ROOT_OUTPUT, svo_folder)
        input_path = os.path.join(ROOT_INPUT, svo_folder)
        
        error_found = False  # Initialize error_found as False

        try:
            zed_utils.extract_vo_stereo_images(input_path, output_path, args.svo_step)
            camera_params = zed_utils.get_camera_params(os.path.join(ROOT_INPUT, svo_folder))
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            error_found = True  # Set error_found to True in case of an exception

        if error_found:
            continue    

        logging.error("=======================")
        logging.error(f"STARTING VO FOR [{i} / {len(svo_path_rel)}] FOLDER!")
        logging.error("=======================")
        # time.sleep(5)
        
        vo  = run(args, svo_folder, camera_params)  
        # seq_list = vo.get_viable_sequences()
        
        # (st1, en1), (st2, en2), ...
        seq_tuples = vo.get_sequence_pairs()

        logging.info("=======================")
        logging.info("VALID SEQUENCES")
        logging.info("=======================")
        for seq in seq_tuples:
            logging.info(f"{seq}")


        logging.info("=======================")
        logging.info("SAVING SEQUENCES TO DISK!")
        logging.info("=======================")
        
        seq_file_path = os.path.join(ROOT_VALID_SEQ, svo_folder)
        seq_file_path = os.path.splitext(seq_file_path)[0] + ".json"

        seq_parent_dir = os.path.dirname(seq_file_path)
        
        create_folders([seq_parent_dir])

        logging.info(f"seq_file_path: {seq_file_path}")
        
        if len(seq_tuples) > 0:
            with open(seq_file_path, 'w') as file:
                json.dump(seq_tuples, file)

        logging.info("=======================")
        logging.info(f"WRITTEN VALID SEQUENCES TO {seq_file_path}!")
        logging.info("=======================")
        
        # time.sleep(1)
        
        # return seq_file_path
        # write_seq_to_disk(folder, seq_tuples)

    logging.info("=======================")
    logging.info("DELETING THE INPUT SVO FOLDERS!")
    logging.info("=======================")
    
    # delete_folders(svo_folders_abs)
        