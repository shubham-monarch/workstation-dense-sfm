#! /usr/bin/env python3

import logging
import coloredlogs
import open3d as o3d
import os
import numpy as np
import yaml
from tqdm import tqdm
import argparse
from scripts.utils_module import io_utils
import shutil
from typing import Tuple, Dict, Optional


def is_close(colors: np.ndarray, target_color: tuple, threshold: int = 20) -> np.ndarray:
    """
    Check if colors are close to target_color by comparing each RGB component individually.

    Args:
        colors (np.ndarray): A numpy array of shape (N, 3) containing RGB colors.
        target_color (tuple): A tuple of (R, G, B) values to compare against.
        threshold (int): Maximum difference for each color component to be considered close.

    Returns:
        np.ndarray: A boolean mask array of shape (N,) where True indicates close colors.
    """
    # Convert target_color to a numpy array for broadcasting
    target_color = np.array(target_color)
    
    # Calculate the absolute difference for each color component
    color_diff = np.abs(colors - target_color)
    
    # Check if all color components are within the threshold
    return np.all(color_diff <= threshold, axis=1)



# def label_PLY(ply_segmented: str, dairy_yaml: str) -> None:
def label_PLY(pcd_path: str, dairy_yaml: str) -> None:
	"""
	Add semantic labels to a PLY file based on color mapping
	
	Args:
		ply_segmented: Path to input PLY file
		mavis_file: Path to MAVIS YAML file containing color mapping
	"""
	try:
		with open(dairy_yaml, 'r') as file:
			dairy_config = yaml.safe_load(file)
		
		# get colors and labels from yaml
		color_to_label = {}
		for label, color in dairy_config['color_map'].items():
			# convert yaml BGR colors to RGB for comparison
			rgb_color = (color[2], color[1], color[0])  # BGR to RGB
			color_to_label[tuple(rgb_color)] = label
		
		pcd = o3d.io.read_point_cloud(pcd_path)
		
		colors_RGB = np.asarray(pcd.colors)
		colors_BGR = colors_RGB[:, [2, 1, 0]] * 255  # Convert to BGR and scale to 0-255
		colors_BGR = colors_BGR.astype(np.uint32)
		
		points = np.asarray(pcd.points)
		labels = np.zeros(len(points), dtype=np.uint8)
		
		# create a mask for all points that have not been labeled yet
		unlabeled_mask = np.ones(len(labels), dtype=bool)

		# iterate through each defined color and update matching points
		for target_color, label in color_to_label.items():
			# update labels for points with similar colors
			similar_color_mask = is_close(colors_BGR, target_color, threshold=20)
			labels[similar_color_mask] = label
			# update the unlabeled mask
			unlabeled_mask[similar_color_mask] = False
		
		# set the label for points not in color_to_label to 0
		labels[unlabeled_mask] = 0
		
		# Write labeled PLY file
		with open(pcd_path, 'w') as f:
			f.write(f"ply\nformat ascii 1.0\nelement vertex {len(points)}\n")
			f.write("property float x\nproperty float y\nproperty float z\n")
			f.write("property uchar red\nproperty uchar green\nproperty uchar blue\n")
			f.write("property uchar label\n")
			f.write("end_header\n")
			
			# Vectorized formatting and writing
			rgb_colors = (colors_RGB * 255).astype(np.uint8)
			combined_data = np.hstack((points, rgb_colors, labels.reshape(-1,1)))
			np.savetxt(f, combined_data, 
					  fmt='%.6f %.6f %.6f %d %d %d %d',
					  comments='')
		
		# logging.info(f"Successfully labeled PLY file: {pcd_path}")
		
	except Exception as e:
		logging.error(f"Error processing {pcd_path}: {str(e)}")
		raise

def main():
	coloredlogs.install(level="INFO", force=True)
	
	logging.info("=======================")
	logging.info("ADDING LABELS TO POINTCLOUD")
	logging.info("=======================\n")
	
	parser = argparse.ArgumentParser()
	parser.add_argument("--PLY_folder", type=str, required=True, 
					   help="Folder with frame-to-frame PLY files")
	parser.add_argument("--output_folder", type=str, required=True, 
					   help="Output folder for the labelled PLY files")
	parser.add_argument("--mavis", type=str, required=True, 
					   help="Path to the Mavis.yaml file")
	
	args = parser.parse_args()
	
	# Prepare output directory
	io_utils.delete_folders([args.output_folder])
	io_utils.create_folders([args.output_folder])
	
	# Copy PLY files to output directory
	for root, _, files in os.walk(args.PLY_folder):
		for file in files:
			if file.endswith(".ply"):
				src_path = os.path.join(root, file)
				rel_path = os.path.relpath(root, args.PLY_folder)
				dest_path = os.path.join(args.output_folder, rel_path, file)
				io_utils.create_folders([os.path.dirname(dest_path)])
				shutil.copy(src_path, dest_path)
	
	# Process PLY files
	for root, _, files in os.walk(args.output_folder):
		for file in files:
			if file.lower().endswith('.ply') and file.lower().startswith('left'):
				ply_path = os.path.join(root, file)
				try:
					label_PLY(ply_path, args.mavis)
				except Exception as e:
					logging.error(f"Failed to process {file}: {str(e)}")

if __name__ == "__main__":
	main()
	