#! /usr/bin/env python3

import logging,coloredlogs
import open3d as o3d
import os
import numpy as np
import yaml
from tqdm import tqdm
import argparse
from scripts.utils_module import io_utils
import shutil

def is_close_color(color1: np.ndarray, color2: np.ndarray, tolerance=10) -> bool:
	'''
	Check if two bgr colors are close to each other
	'''
	return all(abs(c1 - c2) <= tolerance for c1, c2 in zip(color1, color2))

def get_label(bgr: np.ndarray, color_map: dict) -> int:
	'''
	Get label for a bgr pixel using the color_map

	:param bgr: color in [b, g, r] format
	:param color_map: dict: color_map to use for mapping colors to labels
	'''

	for label, color in color_map.items():
		if is_close_color(bgr, np.array(color)):
			return label
	
	# default to 0 if not found
	return 0

def label_PLY(ply_segmented: str, mavis_file: str) -> None:
	# ply_segmented = args.PLY_segmented
	# mavis_file = args.mavis

	with open(mavis_file, 'r') as f:
		data = yaml.safe_load(f)
	
	color_map = data.get("color_map", {})
	
	# {label : (r, g, b)} to {(r, g, b) : label}
	color_map = {key: tuple(value) for key, value in color_map.items()}

	pcd = o3d.io.read_point_cloud(ply_segmented)
	points, colors_rgb = np.asarray(pcd.points), np.asarray(pcd.colors)
	colors_bgr = colors_rgb[:, [2, 1, 0]]  # Reorder RGB to BGR
	
	labels = np.array([get_label(color_bgr * 255, color_map) for color_bgr in tqdm(colors_bgr, desc="Processing labels for PLY file")])

	# update the segmented PLY file with labels 
	with open(ply_segmented, 'w') as f:
		f.write(f"ply\nformat ascii 1.0\nelement vertex {len(points)}\n")
		f.write("property float x\nproperty float y\nproperty float z\n")
		f.write("property uchar red\nproperty uchar green\nproperty uchar blue\n")
		f.write("property uchar label\n")
		f.write("end_header\n")
		for point, rgb, label in zip(points, (colors_rgb*255).astype(np.uint8), labels):
			f.write(f"{point[0]} {point[1]} {point[2]} {rgb[0]} {rgb[1]} {rgb[2]} {label}\n")

	# logging.info("Finished adding labels to the segmented PLY file!")
	
if __name__ == "__main__":
	coloredlogs.install(level="INFO", force=True)
	
	logging.info("=======================")
	logging.info("ADDING LABELS TO POINTCLOUD")
	logging.info("=======================")
	

	parser = argparse.ArgumentParser()
	# parser.add_argument("--rgb_images", type=str, required= True)
	parser.add_argument("--PLY_folder", type=str, required= True, help="Folder with frame-to-frame PLY files")
	parser.add_argument("--output_folder", type=str, required= True, help="Output folder for the labelled PLY files")
	parser.add_argument("--mavis", type=str, required=True, help="Path to the Mavis.yaml file")

	args = parser.parse_args()

	PLY_folder = args.PLY_folder
	input_folder = args.PLY_folder
	output_folder = args.output_folder

	# clear the output folder
	io_utils.delete_folders([output_folder])
	io_utils.create_folders([output_folder])

	# copy the PLY files to the output folder
	shutil.copytree(PLY_folder, output_folder,  dirs_exist_ok=True)
	
	for root, dirs, files in os.walk(output_folder):
		for file in tqdm(files):
			if file.lower().endswith('.ply'):	
				ply_segmented = os.path.join(root, file)
				label_PLY(ply_segmented, args.mavis)
			