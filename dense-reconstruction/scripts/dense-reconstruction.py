#!/usr/bin/env python 

import pycolmap 
from pathlib import Path
import shutil
import os

def dense_sfm_pipeline(mvs_path, output_path, image_dir):

    if(mvs_path.exists()):
        try:
            #outputs.rmdir()
            shutil.rmtree(mvs_path)
            print(f"{mvs_path} removed")
        except OSError as e:
            print(f"An error occurred while deleting the directory: {e}")


    pycolmap.undistort_images(mvs_path, output_path, image_dir)
    pycolmap.patch_match_stereo(mvs_path)  # requires compilation with CUDA
    pycolmap.stereo_fusion(mvs_path / "dense.ply", mvs_path)


if __name__ == "__main__": 
    #mvs_path = Path("../output/")
    mvs_path = Path("dense-reconstruction/output/")
    output_path = Path("rig-bundle-adjuster/output/")
    image_dir = Path("sparse-reconstruction/pixsfm_dataset/")
    

    print(f"mvs_path: {os.path.abspath(mvs_path)}")
    print(f"output_path: {os.path.abspath(output_path)}")
    print(f"image_dir: {os.path.abspath(image_dir)}")


    dense_sfm_pipeline(mvs_path, output_path, image_dir)    
