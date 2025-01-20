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
import cv2
def main(filepath, start, end, dir_path_, svo_step = 1):

    # logging.debug("Inside the main function!")

    filepath = os.path.abspath(filepath)
    dir_path = os.path.abspath(dir_path_)

    logging.info(f"svo_file: {filepath}")
    logging.info(f"start_idx: {start} end_idx: {end}")

    input_type = sl.InputType()
    input_type.set_from_svo_file(filepath)


    init = sl.InitParameters(input_t=input_type, svo_real_time_mode=False)
    init.coordinate_units = sl.UNIT.METER   

    zed = sl.Camera()
    status = zed.open(init)
    # logging.warn(f"Total frames: {zed.get_svo_number_of_frames()}")
    if status != sl.ERROR_CODE.SUCCESS:
        print(repr(status))
        exit()

    runtime_parameters = sl.RuntimeParameters()

    image = sl.Mat()
    image_r = sl.Mat()
    
    logging.info(f"Trying to delete the {dir_path} directory")
    try:
        shutil.rmtree(dir_path)
        logging.info(f"Cleared the {dir_path} directory!")
    except OSError as e:
        logging.warning("Warning: %s : %s" % (dir_path, e.strerror))

    logging.info(f"Extracting {(end - start) // svo_step} stereo-images from the SVO file!")
    for frame_idx in tqdm(range(start, end, svo_step)):
        if zed.grab(runtime_parameters) == sl.ERROR_CODE.SUCCESS:
            zed.set_svo_position(frame_idx)
            if frame_idx == start:
                continue
            # logging.debug(f"Processing {frame_idx}th frame!")
            # create the outputm directory
            output_dir = os.path.join(dir_path, "frame_{}/images".format(frame_idx) )    
            os.makedirs( output_dir, exist_ok=True )
            # reading and writing the images to the output directory
            zed.retrieve_image(image, sl.VIEW.LEFT)
            zed.retrieve_image(image_r, sl.VIEW.RIGHT)
            
            # Convert to numpy array and resize
            left_img = image.get_data()
            right_img = image_r.get_data()
            left_img_resized = cv2.resize(left_img, (640, 480))
            right_img_resized = cv2.resize(right_img, (640, 480))
            
            # Save directly using cv2 instead of converting back to sl.Mat
            cv2.imwrite(os.path.join(output_dir, 'left_image.jpg'), left_img_resized)
            cv2.imwrite(os.path.join(output_dir, 'right_image.jpg'), right_img_resized)
            # image.write( os.path.join(output_dir, 'left_image.png') )
            # image_r.write( os.path.join(output_dir, 'right_image.png') )
        
        else:
            sys.exit(1)
    zed.close()

if __name__ == "__main__":

    coloredlogs.install(level="DEBUG", force=True)  # install a handler on the root logger

    parser = argparse.ArgumentParser(description='Script to process a SVO file')
    parser.add_argument('--svo_path', type=str, required = True, help='target svo file path')
    parser.add_argument('--start_frame', type=int, required = True, help='number of frames to be extracted')
    parser.add_argument('--end_frame', type=int, required = True, help='number of frames to be extracted')
    parser.add_argument('--output_dir', type=str, required = True, help='output directory path')
    parser.add_argument('--svo_step', type=int, required = False, default = 1, help='frame skipping frequency')  
    args = parser.parse_args()  
    
    # logging.debug(f"svo_path: {args.svo_path}")
    # logging.debug(f"start_frame: {args.start_frame}")
    # logging.debug(f"end_frame: {args.end_frame}")
    # logging.debug(f"output_dir: {args.output_dir}")
    # logging.debug(f"svo_step: {args.svo_step}")

    logging.warning(f"[svo-to-stereo-images.py]")
    for key, value in vars(args).items():
        logging.info(f"{key}: {value}")
    
    main(Path(args.svo_path), args.start_frame, args.end_frame , Path(args.output_dir), args.svo_step)
