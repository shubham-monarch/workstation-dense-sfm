#!/usr/bin/env python 

import pycolmap 
from pathlib import Path
import shutil

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
    mvs_path = Path("../output/")
    output_path = Path("../../rig_bundle_adjuster/output/")
    image_dir = Path("../../sparse-reconstruction/pixsfm_dataset/")

    dense_sfm_pipeline(mvs_path, output_path, image_dir)    