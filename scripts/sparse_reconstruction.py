#!/usr/bin/env python3

#%load_ext autoreload
#%autoreload 2
import tqdm, tqdm.notebook
tqdm.tqdm = tqdm.notebook.tqdm  # notebook-friendly progress bars
import os
import time
import sys
from hloc import extract_features, match_features, reconstruction, pairs_from_exhaustive, visualization
from hloc.visualization import plot_images, read_image
from hloc.utils.viz_3d import init_figure, plot_points, plot_reconstruction, plot_camera_colmap
from pixsfm.util.visualize import init_image, plot_points2D
from pixsfm.refine_hloc import PixSfM
from pixsfm import ostream_redirect
from PIL import Image, ImageDraw
import pycolmap
from pathlib import Path
import os
import shutil
import torch 
import numpy as np     
import argparse 
import pyzed.sl as sl
import logging, coloredlogs
import gc
import cv2
# from memory_profiler import profile

# from scriutils_module import io_utils
# from scripts.utils_module import io_utils
from scripts.utils_module import io_utils

# redirect the C++ outputs to notebook cells
cpp_out = ostream_redirect(stderr=True, stdout=True)
cpp_out.__enter__()


# LOGGING SETUP
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(lineno)d')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
coloredlogs.install(level='INFO', logger=logger, force=True)


def get_zed_camera_params(svo_loc):
    
    zed_file_path = os.path.abspath(svo_loc)
    print(f"zed_file_path: {zed_file_path}")

    input_type = sl.InputType()
    input_type.set_from_svo_file(zed_file_path)
    init = sl.InitParameters(input_t=input_type, svo_real_time_mode=False)
    init.coordinate_units = sl.UNIT.METER   

    zed = sl.Camera()
    status = zed.open(init)
    if status != sl.ERROR_CODE.SUCCESS:
        print(repr(status))
        exit()


    calibration_params = zed.get_camera_information().camera_configuration.calibration_parameters
    zed_camera_params = [calibration_params.left_cam.fx, calibration_params.left_cam.fy, calibration_params.left_cam.cx, calibration_params.left_cam.cy, 0, 0 ,0 , 0]
    
    #print(f"zed_camera_params: {zed_camera_params}")
    camera_params= ",".join(str(x) for x in zed_camera_params)

    return camera_params

'''
Generates input data for the pixSFM pipeline 
by processing the output of the svo pipeline
'''
def generate_input_folder(src_dir, dst_dir):

    logging.warning(f"src_dir: {src_dir}")
    logging.warning(f"dst_dir: {dst_dir}")

    io_utils.delete_folders([dst_dir])
    io_utils.create_folders([dst_dir])

    # Create 'left' and 'right' directories inside 'dataset'
    os.makedirs(os.path.join(dst_dir, 'left'), exist_ok=True)
    os.makedirs(os.path.join(dst_dir, 'right'), exist_ok=True)

    # Iterate over all directories in the source directory
    for dir_name in os.listdir(src_dir):
        frame_dir = os.path.join(src_dir, dir_name)
        if os.path.isdir(frame_dir):
            images_dir = os.path.join(frame_dir, 'images')
            if os.path.isdir(images_dir):
                # Copy 'left.jpg' to 'dataset/left' and 'right.jpg' to 'dataset/right'
                for file_name in os.listdir(images_dir):
                    if file_name == 'left_image.jpg':
                        shutil.copy(os.path.join(images_dir, file_name), os.path.join(dst_dir, 'left', dir_name + '_.jpg'))
                    elif file_name == 'right_image.jpg':
                        shutil.copy(os.path.join(images_dir, file_name), os.path.join(dst_dir, 'right', dir_name + '_.jpg'))
                    # if file_name == 'left_image.png':
                    #     shutil.copy(os.path.join(images_dir, file_name), os.path.join(dst_dir, 'left', dir_name + '_.png'))
                    # elif file_name == 'right_image.png':
                    #     shutil.copy(os.path.join(images_dir, file_name), os.path.join(dst_dir, 'right', dir_name + '_.png'))



def remove_hood(input_path, output_dir):

    img_name = os.path.basename(input_path)
    os.makedirs(output_dir, exist_ok=True)
    img = cv2.imread(str(input_path))

    h, w, _ = img.shape
    
    if img is None:
        return
    x1, y1, x2, y2 = [int(0.68* h), int(0.21 * w), int(h), int(0.85 * w)]  
    
    # Black out the bbox region
    img[x1:x2, y1:y2] = 0
        
    output_path = os.path.join(output_dir, img_name)
    cv2.imwrite(str(output_path), img)
    
    # logger.warning("=======================")
    # logger.warning(f"input_path: {input_path}")
    # logger.warning(f"output_path: {output_path}")
    # logger.warning("=======================")
	

'''
:param svo_output: path to the svo files
:param images: Path to the directory containing the images
:param outputs: Path to the directory where the output files will be stored
:param opencv_camera_params: Camera parameters in the opencv format
'''

# @profile
def sparse_reconstruction_pipeline(opencv_camera_params, images, outputs):
    try:
        # Your existing code for sparse reconstruction pipeline
        io_utils.delete_folders([outputs])
        
        sfm_pairs = outputs / 'pairs-sfm.txt'
        loc_pairs = outputs / 'pairs-loc.txt'
        features = outputs / 'features.h5'
        matches = outputs / 'matches.h5'
        raw_dir = outputs / "raw"
        ref_dir_locked = outputs / "ref_locked"

        print(f"{os.listdir(images)}")

        feature_conf = extract_features.confs['superpoint_aachen']
        matcher_conf = match_features.confs['superglue']

        references_left = [str(p.relative_to(images)) for i, p in enumerate((images / 'left/').iterdir())]
        references_right = [str(p.relative_to(images)) for i, p in enumerate((images / 'right/').iterdir())]

        references_left = sorted(references_left, key=lambda x: int(x.split('/')[-1].split('_')[1]))
        references_right = sorted(references_right, key=lambda x: int(x.split('/')[-1].split('_')[1]))

        references = references_left + references_right
        references = sorted(references, key=lambda x: int(x.split('/')[-1].split('_')[1]))

        for ref in references:
            input_path = images / ref
            output_dir = os.path.dirname(images / ref)
            remove_hood(images / ref, output_dir)
            # logger.warning("=======================")
            # logger.warning(f"input_path: {input_path}")
            # logger.warning(f"output_dir: {output_dir}")
            # logger.warning("=======================")
        
        features_path_ = extract_features.main(feature_conf, images, image_list=references, feature_path=features)

        pairs_from_exhaustive.stereo_main(sfm_pairs, image_list=references)

        match_features.main(matcher_conf, sfm_pairs, features=features, matches=matches)

        gc.collect()
        
        conf2 = {
            "BA": {"optimizer": {"refine_focal_length": False,"refine_extra_params": False, "refine_extrinsics": False}},
            "dense_features": {"max_edge":1024}
        }

        sfm = PixSfM(conf=conf2)

        image_options = dict(camera_model='OPENCV', camera_params=opencv_camera_params)

        mapper_options_two = dict(ba_refine_focal_length=False, ba_refine_extra_params=False, ba_refine_principal_point=False)

        hloc_args_not_locked = dict(image_list=references, image_options=image_options, camera_mode="PER_FOLDER", mapper_options=mapper_options_two)
        
        logging.warning("Before sfm.reconstruction")
        K_locked, sfm_outputs_not_locked = sfm.reconstruction(ref_dir_locked, images, sfm_pairs, features, matches, **hloc_args_not_locked)
        logging.warning("After sfm.reconstruction")

        logging.info("Sparse reconstruction finished!")
        logging.info(f"K_locked.summary(): {K_locked.summary()}")

    except MemoryError as e:
        logging.error(f"Memory error occurred: {e}")
        logging.error("Attempting to free up memory and continue...")

        # Add your custom logic to free up memory and continue
        # For example, you can try to clear caches, release objects, or reduce the workload
        gc.collect()
        torch.cuda.empty_cache()

        # If the memory issue persists, you can choose to exit the script or continue with a reduced workload
        # if still_memory_issue():
        #     logging.error("Unable to free up enough memory. Exiting the script.")
        #     sys.exit(1)
        # else:
        #     logging.info("Memory freed up. Continuing the sparse reconstruction pipeline.")
        #     # Resume the pipeline with reduced workload or modified parameters
            
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        raise



#TO-DO : add svo parsing
if __name__ == "__main__":
   
    coloredlogs.install(level="DEBUG", force=True)  # install a handler on the root logger
    
    # gc.collect()

    logging.warning(f"[sparse-recosntruction.py]")
    
    parser = argparse.ArgumentParser(description='Sparse Reconstruction Pipeline')
    parser.add_argument('--svo_images', type=str, required=  True, help='Path to the svo -> stereoimages')
    parser.add_argument('--input_dir', type=str, required=  True, help='Path to the sparse-reconstruction input folder')
    parser.add_argument('--output_dir', type=str, required=  True, help='Path to the output directory')
    parser.add_argument('--svo_file', type=str, required=  True, help='Path to the svo file')
    args = parser.parse_args()
    
    # logging.warning(f"[sparse-reconstruction.py] args: {args}")
    # Assuming args is parsed using argparse
    for key, value in vars(args).items():
        logging.info(f"{key}: {value}")
    
    generate_input_folder(Path(args.svo_images), Path(args.input_dir))
    
    zed_camera_params = get_zed_camera_params(args.svo_file)
    logging.warning(f"zed_camera_params ==> {zed_camera_params}")
    
        
    sparse_reconstruction_pipeline( zed_camera_params, 
                                    Path(args.input_dir),
                                    Path(args.output_dir))
