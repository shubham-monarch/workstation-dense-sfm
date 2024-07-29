#!/usr/bin/env python3

import open3d as o3d
import argparse
import logging, coloredlogs
from .p360_dataset import P360DatasetGenerator

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some paths and bounding box.')
    parser.add_argument('--bounding_box', type=int, nargs=6, required = True, help='Bounding box coordinates as six integers (min_x, max_x, min_y, max_y, min_z, max_z)')
    parser.add_argument('--dense_reconstruction_folder', type=str, required= True,  help='Path to the [cameras.bin, images.bin, points3D.bin] folder')
    parser.add_argument('--output_folder', type=str, required = True, help='Path to the output directory')
    args = parser.parse_args()
    
    bounding_box = tuple(args.bounding_box) 
    sfm_path = args.dense_reconstruction_folder 
    output_path = args.output_folder 

    p360_generator_ = P360DatasetGenerator(bounding_box, sfm_path, output_path)
    p360_generator_.generate()

    # example usage
    # bounding_box = (-50, 50, -5, 5, -3, 3)
    # sfm_path = "/home/skumar/ext_ssd/workstation-sfm-setup/output-backend/dense-reconstruction/front_2023-11-03-11-18-57.svo/50_to_150"
    # output_path = 'framewise-ply/'  
    # p360_generator_ = P360DatasetGenerator(bounding_box, sfm_path, output_path)
    # #dataset_generator.generate()
    # p360_generator_.generate()
