#! /usr/bin/env python3
import open3d as o3d
# from open3d.pipelines import registration as treg
import numpy as np
import copy
import time
import math
import fast_global_registration 
import utils
import logging, coloredlogs

if o3d.__DEVICE_API__ == 'cuda':
	import open3d.cuda.pybind.t.pipelines.registration as treg
else:
	import open3d.cpu.pybind.t.pipelines.registration as treg


PROJECT_ROOT="../"
OUTPUT_FOLDER=f"{PROJECT_ROOT}/output"
PLY_FOLDER=f"{OUTPUT_FOLDER}/ply-files"


def draw_registration_result(source, target, transformation):

	source_temp = source.clone()
	target_temp = target.clone()

	# source_temp.paint_uniform_color([1.0, 0.0, 0.0])  # Red color
	source_temp.transform(transformation) 
	frame1 = o3d.geometry.TriangleMesh.create_coordinate_frame(size=10, origin=[0, 0, 0])	

	o3d.visualization.draw_geometries(
		[
		source_temp.to_legacy(),
		#  source_b.to_legacy(),
		target_temp.to_legacy(),
		#  frame1
		#  frame2
		],
		zoom=0.4459,
		front=[0.9288, -0.2951, -0.2242],
		lookat=[1.6784, 2.0612, 1.4451],
		# lookat=[0, 0, 0],
		up=[-0.3402, -0.9189, -0.1996])


def run_multiscale_icp(source, target):
	logging.warning("Run Multi-Scale ICP")
	logging.info(f"type(source) : {type(source)}")

	# source_t = source.to(o3d.core.Device("CUDA:0"))  # Assuming you want to use CUDA device 0
	# target_t = target.to(o3d.core.Device("CUDA:0"))
	source_cuda = source.cuda(0)
	target_cuda = target.cuda(0)

	target_cuda.estimate_normals(max_nn=30, radius=0.1)

	
	voxel_sizes = o3d.utility.DoubleVector([0.1, 0.05, 0.025])

	# List of Convergence-Criteria for Multi-Scale ICP:
	criteria_list = [
		treg.ICPConvergenceCriteria(relative_fitness=0.0001,
									relative_rmse=0.0001,
									max_iteration=20),
		treg.ICPConvergenceCriteria(0.00001, 0.00001, 15),
		treg.ICPConvergenceCriteria(0.000001, 0.000001, 10)
	]

	# `max_correspondence_distances` for Multi-Scale ICP (o3d.utility.DoubleVector):
	max_correspondence_distances = o3d.utility.DoubleVector([0.3, 0.14, 0.07])

	# Initial alignment or source to target transform.
	init_source_to_target = o3d.core.Tensor.eye(4, o3d.core.Dtype.Float32)

	# Select the `Estimation Method`, and `Robust Kernel` (for outlier-rejection).
	estimation = treg.TransformationEstimationPointToPlane()

	# Save iteration wise `fitness`, `inlier_rmse`, etc. to analyse and tune result.
	callback_after_iteration = lambda loss_log_map : print("Iteration Index: {}, Scale Index: {}, Scale Iteration Index: {}, Fitness: {}, Inlier RMSE: {},".format(
		loss_log_map["iteration_index"].item(),
		loss_log_map["scale_index"].item(),
		loss_log_map["scale_iteration_index"].item(),
		loss_log_map["fitness"].item(),
		loss_log_map["inlier_rmse"].item()))
	
	# Setting Verbosity to Debug, helps in fine-tuning the performance.
	# o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Debug)

	s = time.time()

	# registration_ms_icp = treg.multi_scale_icp(source, target, voxel_sizes,
	# 										criteria_list,
	# 										max_correspondence_distances,
	# 										init_source_to_target, estimation,
	# 										callback_after_iteration)

	registration_ms_icp = treg.multi_scale_icp(source_cuda, target_cuda, voxel_sizes,
											criteria_list,
											max_correspondence_distances,
											init_source_to_target, estimation,
											callback_after_iteration)


	ms_icp_time = time.time() - s
	print("Time taken by Multi-Scale ICP: ", ms_icp_time)
	print("Inlier Fitness: ", registration_ms_icp.fitness)
	print("Inlier RMSE: ", registration_ms_icp.inlier_rmse)

	draw_registration_result(source_cuda, target_cuda, registration_ms_icp.transformation)


if __name__ == "__main__":
	
	coloredlogs.install(level="INFO", force=True)
	voxel_size = 0.05  # means 5cm for this dataset
	
	
	# o3d.visualization.draw_geometries([source.to_legacy()],
    #                               zoom=1,
    #                               front=[0.4257, -0.2125, -0.8795],
    #                               lookat=[2.6172, 2.0475, 1.532],
    #                               up=[-0.0694, -0.9768, 0.2024])
	
	# exit()
	# logging.info(f"Data type of points in source: {source.point['points'].dtype}")
	# logging.warning(f"================================================")
	# logging.info(f"type(source) : {type(source)}")
	# logging.info(f"{dir(type(source))}")
	# logging.warning(f"================================================")
	
	# # logging.info(f"len(points): {len(source.points)}")
	# positions_dtype = source.point.positions.dtype
	# logging.info(f"positions_dtype : {positions_dtype}")

	# source.point['positions'] = source.point['positions'].to(dtype=o3d.core.Dtype.Float64)

	# positions_dtype = source.point.positions.dtype

	# logging.info(f"type(positions) : {type(positions)}")	
	# logging.info(f"{len(source.point.positions)}")
	# starget = o3d.t.io.read_point_cloud(f"{PLY_FOLDER}/annotated.ply")
	
	# source_clean = source.remove_radius_outlier(nb_points=16, radius=0.05)
	

	source = o3d.t.io.read_point_cloud(f"{PLY_FOLDER}/auto_segmented.ply")
	
	target = o3d.t.io.read_point_cloud(f"{PLY_FOLDER}/annotated.ply")
	target.point['positions'] = target.point['positions'].to(dtype=o3d.core.Dtype.Float32)
	

	source_, mask = source.remove_statistical_outliers(nb_neighbors=20, std_ratio=2.0)
	target_, mask = target.remove_statistical_outliers(nb_neighbors=20, std_ratio=2.0)
	
	
	# run_multiscale_icp(source, target)
	run_multiscale_icp(source_, target_)