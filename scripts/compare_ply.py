#! /usr/bin/env python3 

import rerun as rr  # NOTE: `rerun`, not `rerun-sdk`!
import numpy as np
import open3d as o3d
import logging, coloredlogs

PROJECT_ROOT="../"
OUTPUT_FOLDER=f"{PROJECT_ROOT}/output"
PLY_FOLDER=f"{OUTPUT_FOLDER}/ply-files"


def read_ply(ply_file):
	ply = o3d.io.read_point_cloud(ply_file)
	positions = np.asarray(ply.points)
	if ply.colors:  # Check if colors are available
		colors = np.asarray(ply.colors) * 255  # Scaling colors to 0-255 range
		colors = colors.astype(np.uint8)
	else:
		colors = np.zeros(positions.shape, dtype=np.uint8)  # Default color if not available
	return positions, colors



if __name__ == "__main__":
	rr.init("AUTO-SEGMENTED vs ANNOTATED", spawn=True)
	coloredlogs.install(level="INFO", force=True)
	# positions = np.zeros((10, 3))
	# positions[:,0] = np.linspace(-10,10,10)

	# colors = np.zeros((10,3), dtype=np.uint8)
	# colors[:,0] = np.linspace(0,255,10)

	# rr.log(
	# 	"my_points",
	# 	rr.Points3D(positions, colors=colors, radii=0.5)
	# )

	ply_auto_segmented = f"{PLY_FOLDER}/auto_segmented.ply"
	ply_annotated = f"{PLY_FOLDER}/annotated.ply"

	logging.info(f"ply_auto_segmented : {ply_auto_segmented}")
	logging.info(f"ply_annotated : {ply_annotated}")
	
	positions1, colors1 = read_ply(ply_auto_segmented)
	positions2, colors2 = read_ply(ply_annotated)

	rr.log(
    "Auto-Segmented",
    rr.Points3D(positions1, colors=colors1, radii=0.5)
)

	# Plot the second set of points
	rr.log(
		"Annotated",
		rr.Points3D(positions2, colors=colors2, radii=0.5)
	)