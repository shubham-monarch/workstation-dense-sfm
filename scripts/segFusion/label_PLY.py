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

def compute_color_distance(color1: np.ndarray, color2: np.ndarray) -> float:
	"""
	Compute the Euclidean distance between two colors in BGR space
	
	Args:
		color1: First color in BGR format (numpy array)
		color2: Second color in BGR format (numpy array)
	Returns:
		float: Euclidean distance between colors
	"""
	return np.sqrt(np.sum((color1 - color2) ** 2))

def is_close_color(color1: np.ndarray, color2: np.ndarray, tolerance: float = 15.0) -> bool:
	"""
	Check if two BGR colors are close to each other using Euclidean distance
	
	Args:
		color1: First color in BGR format
		color2: Second color in BGR format
		tolerance: Maximum allowed distance between colors
	Returns:
		bool: True if colors are within tolerance
	"""
	return compute_color_distance(color1, color2) <= tolerance

def validate_color_map(color_map: Dict[int, Tuple[int, int, int]]) -> None:
	"""
	Validate the color map format and values
	
	Args:
		color_map: Dictionary mapping labels to BGR colors
	Raises:
		ValueError: If color map is invalid
	"""
	if not color_map:
		raise ValueError("Empty color map provided")
	
	for label, color in color_map.items():
		if not isinstance(label, int):
			raise ValueError(f"Invalid label type: {label} (must be integer)")
		if not isinstance(color, (tuple, list)) or len(color) != 3:
			raise ValueError(f"Invalid color format for label {label}: {color}")
		if not all(isinstance(c, int) and 0 <= c <= 255 for c in color):
			raise ValueError(f"Invalid color values for label {label}: {color}")

def get_label(bgr: np.ndarray, color_map: Dict[int, Tuple[int, int, int]]) -> int:
	"""
	Get label for a BGR pixel using the color map with nearest neighbor matching
	
	Args:
		bgr: Color in [B, G, R] format
		color_map: Dictionary mapping labels to BGR colors
	Returns:
		int: Matched label or 0 if no match found
	"""
	min_distance = float('inf')
	best_label = 0
	
	for label, color in color_map.items():
		distance = compute_color_distance(bgr, np.array(color))
		if distance < min_distance:
			min_distance = distance
			best_label = label
	
	# Only return the label if the distance is within a reasonable threshold
	return best_label if min_distance <= 25.0 else 0

def label_PLY(ply_segmented: str, mavis_file: str) -> None:
	"""
	Add semantic labels to a PLY file based on color mapping
	
	Args:
		ply_segmented: Path to input PLY file
		mavis_file: Path to MAVIS YAML file containing color mapping
	"""
	try:
		# Load and validate color map
		with open(mavis_file, 'r') as f:
			data = yaml.safe_load(f)
		
		color_map = data.get("color_map", {})
		validate_color_map(color_map)
		
		# Read point cloud
		pcd = o3d.io.read_point_cloud(ply_segmented)
		if not pcd.has_colors():
			raise ValueError(f"PLY file {ply_segmented} has no color information")
		
		points = np.asarray(pcd.points)
		colors_rgb = np.asarray(pcd.colors)
		colors_bgr = colors_rgb[:, [2, 1, 0]] * 255  # Convert to BGR and scale to 0-255
		
		# Process labels with progress bar
		labels = np.zeros(len(points), dtype=np.uint8)
		for idx, color_bgr in enumerate(tqdm(colors_bgr, desc="Processing labels")):
			labels[idx] = get_label(color_bgr, color_map)
		
		# Write labeled PLY file
		with open(ply_segmented, 'w') as f:
			f.write(f"ply\nformat ascii 1.0\nelement vertex {len(points)}\n")
			f.write("property float x\nproperty float y\nproperty float z\n")
			f.write("property uchar red\nproperty uchar green\nproperty uchar blue\n")
			f.write("property uchar label\n")
			f.write("end_header\n")
			
			rgb_colors = (colors_rgb * 255).astype(np.uint8)
			for point, rgb, label in zip(points, rgb_colors, labels):
				f.write(f"{point[0]:.6f} {point[1]:.6f} {point[2]:.6f} "
						f"{rgb[0]} {rgb[1]} {rgb[2]} {label}\n")
		
		logging.info(f"Successfully labeled PLY file: {ply_segmented}")
		
	except Exception as e:
		logging.error(f"Error processing {ply_segmented}: {str(e)}")
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
	