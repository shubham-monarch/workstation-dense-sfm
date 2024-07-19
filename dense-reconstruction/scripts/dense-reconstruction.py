#!/usr/bin/env python 

import pycolmap 
from pathlib import Path
import shutil
import os
import argparse
import logging, coloredlogs


def dense_sfm_pipeline(mvs_path, output_path, image_dir):

    # if(mvs_path.exists()):
    #     try:
    #         #outputs.rmdir()
    #         shutil.rmtree(mvs_path)
    #         print(f"{mvs_path} removed")
    #     except OSError as e:
    #         print(f"An error occurred while deleting the directory: {e}")


    # pycolmap.undistort_images(mvs_path, output_path, image_dir)
    # pycolmap.patch_match_stereo(mvs_path)  # requires compilation with CUDA
    # pycolmap.stereo_fusion(mvs_path / "dense.ply", mvs_path)
    # pycolmap.stereo_fusion(mvs_path , f"{mvs_path}/bin/")
    logging.debug(f"mvs_path: {mvs_path}")

if __name__ == "__main__": 
    #mvs_path = Path("../output/")
    coloredlogs.install(level="DEBUG", fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    parser = argparse.ArgumentParser(description='Dense Reconstruction Pipeline')
    parser.add_argument('--mvs_path', type=str, required=  True, help='Path to dense reconstruction output')
    parser.add_argument('--output_path', type=str, required=  True, help='Path to rig)_bundle_adjuster output')
    parser.add_argument('--image_dir', type=str, required=  True, help='Path to sparse reconstruction dataset')
    args = parser.parse_args()
    
    #mvs_path = Path("dense-reconstruction/output/")
    #output_path = Path("rig-bundle-adjuster/output/")
    #image_dir = Path("sparse-reconstruction/pixsfm_dataset/")    

    print(f"mvs_path: {os.path.abspath(Path(args.mvs_path))}")
    print(f"output_path: {os.path.abspath(Path(args.output_path))}")
    print(f"image_dir: {os.path.abspath(Path(args.image_dir))}")

    dense_sfm_pipeline(Path(args.mvs_path), Path(args.output_path), Path(args.image_dir))    
