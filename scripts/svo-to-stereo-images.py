#!/usr/bin/env python3

import pyzed.sl as sl
import os
import shutil
import json
import sys
import argparse
import warnings
from pathlib import Path
import coloredlogs, logging
from tqdm import tqdm

from utils_module import io_utils

def main(filepath, output_folder, svo_step = 2):
    
    filepath = os.path.abspath(filepath)
    output_path = os.path.abspath(output_folder)

    logging.info(f"svo_file: {filepath}")
    
    input_type = sl.InputType()
    input_type.set_from_svo_file(filepath)


    init = sl.InitParameters(input_t=input_type, svo_real_time_mode=False)
    init.coordinate_units = sl.UNIT.METER   

    zed = sl.Camera()
    status = zed.open(init)
    if status != sl.ERROR_CODE.SUCCESS:
        print(repr(status))
        exit()

    runtime_parameters = sl.RuntimeParameters()

    image_l = sl.Mat()
    image_r = sl.Mat()
    
    total_frames = zed.get_svo_number_of_frames()
    # logging.info(f"Extracting {(end - start) // svo_step} stereo-images from the SVO file!")
    logging.info(f"Extracting {total_frames // svo_step} stereo-images from the SVO file!")
    
    io_utils.delete_folders([output_path])
    io_utils.create_folders([output_path])
    
    for frame_idx in tqdm(range(0, total_frames, svo_step)):
        if zed.grab(runtime_parameters) == sl.ERROR_CODE.SUCCESS:
            zed.set_svo_position(frame_idx)
            zed.retrieve_image(image_l, sl.VIEW.LEFT)
            zed.retrieve_image(image_r, sl.VIEW.RIGHT)
            image_l.write( os.path.join(output_path, f'left/frame_{frame_idx}.jpg') )
            image_r.write( os.path.join(output_path, f'right/frame_{frame_idx}.jpg') )
        else:
            sys.exit(1)
    zed.close()

if __name__ == "__main__":

    coloredlogs.install(level="DEBUG", force=True)  # install a handler on the root logger

    parser = argparse.ArgumentParser(description='Script to process a SVO file')
    parser.add_argument('--svo_path', type=str, required = True, help='target svo file path')
    parser.add_argument('--output_dir', type=str, required = True, help='output directory path')
    parser.add_argument('--svo_step', type=int, required = False, default = 1, help='frame skipping frequency')  
    args = parser.parse_args()  
    
    
    logging.warning(f"[svo-to-stereo-images.py]")
    for key, value in vars(args).items():
        logging.info(f"{key}: {value}")
    
    main(Path(args.svo_path), Path(args.output_dir), args.svo_step)
