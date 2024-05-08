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

# redirect the C++ outputs to notebook cells
cpp_out = ostream_redirect(stderr=True, stdout=True)
cpp_out.__enter__()

'''
Generates input data for the pixSFM pipeline 
by processing the output of the svo pipeline
'''
def parse_svo_data(src_dir, dst_dir):
    #src_dir = '../svo_output'
    #dst_dir = 'pixsfm_dataset'

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



'''
:param svo_output: path to the svo files
:param images: Path to the directory containing the images
:param outputs: Path to the directory where the output files will be stored
:param opencv_camera_params: Camera parameters in the opencv format
'''
def sparse_reconstruction_pipeline( svo_output,
                                    opencv_camera_params,
                                    images, 
                                    outputs):
    
    print(f"torch.__version__: {torch.__version__}")
    print(f"torch.cuda.get_arch_list(): {torch.cuda.get_arch_list()}")
    
    print(f"camera_params: {opencv_camera_params}")
    #images = Path('pixsfm_dataset/')
    #outputs = Path('output/')

    if(outputs.exists()):
        try:
            #outputs.rmdir()
            shutil.rmtree(outputs)
            print(f"{outputs} removed")
        except OSError as e:
            print(f"An error occurred while deleting the directory: {e}")


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

    '''sorting references so that each stereo pair is together in the list '''
    references = sorted(references, key=lambda x: int(x.split('/')[-1].split('_')[1]))

    features_path_ = extract_features.main(feature_conf, images, image_list= references, feature_path=features)

    pairs_from_exhaustive.stereo_main(sfm_pairs, image_list=references)

    match_features.main(matcher_conf, sfm_pairs, features=features, matches=matches)

    
    conf2 = {
        "BA": {"optimizer": {"refine_focal_length": False,"refine_extra_params": False, "refine_extrinsics": False}},
        "dense_features": {"max_edge":1024}
    }

    sfm = PixSfM(conf=conf2)

    image_options = dict(camera_model='OPENCV', 
                        camera_params=opencv_camera_params
                        )

    mapper_options_two = dict(ba_refine_focal_length=False, 
                        ba_refine_extra_params=False,
                        ba_refine_principal_point=False)

    hloc_args_not_locked = dict(image_list=references,
                    image_options=image_options,
                    camera_mode="PER_FOLDER",
                    mapper_options=mapper_options_two)

    K_locked, sfm_outputs_not_locked = sfm.reconstruction(ref_dir_locked, images, sfm_pairs, features, matches, **hloc_args_not_locked)

    print("Sparse reconstruction finished!")

    print(f"K_locked.summary(): {K_locked.summary()}")


#TO-DO : add svo parsing

if __name__ == "__main__":
   
    parser = argparse.ArgumentParser(description='Sparse Reconstruction Pipeline')
    parser.add_argument('--svo_dir', type=str, required=  True, help='Path to the svo directory')
    parser.add_argument('--camera_params', type=str, required= True, help='Camera parameters in the opencv format')
    args = parser.parse_args()
    
    cwd = os.path.dirname(__file__)
    
    print(f"cwd: {cwd}")

    # path to the images folder
    input_dir=  os.path.join(cwd,  "../pixsfm_dataset/") 
    
    # path to the sparse reconstruction output files
    output_dir= os.path.join(cwd, "../output/")
    
    print(f"input_dir: {os.path.abspath(input_dir)}")
    

    fx = 1093.2768
    fy = 1093.276
    cx = 964.989
    cy = 569.276
    camera_param_ =','.join(map(str, (fx, fy, cx, cy, 0, 0, 0, 0)))

    sparse_reconstruction_pipeline( Path(args.svo_dir),
                                    camera_param_, 
                                    Path(input_dir), 
                                    Path(output_dir))
