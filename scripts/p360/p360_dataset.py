import numpy as np
import os
import open3d as o3d
import pycolmap
from pathlib import Path
import time
import sys

from tqdm import tqdm

from collections import namedtuple

from .camera_helpers import CameraHelpers
from . import read_write_model
from ..utils_module import io_utils

BoundingBox = namedtuple('BoundingBox', ['min_x', 'max_x', 'min_y', 'max_y', 'min_z', 'max_z'])

class P360DatasetGenerator:
    """
    Helper class to  generate cropped pointcloud around the camera pose for each frame  
    :param bounding_box: tuple representing the dimensions of the bounding box (min_x, max_x, min_y, max_y, min_z, max_z)
    :param dense_sfm_path: path to the dense sfm reconstruction folder containing images.bin, cameras.bin, points3D.bin
    :param output_path: Path containing frame-wise cropped pointcloud
    """

    def __init__(self, 
                 bounding_box, 
                 sfm_folder_path, 
                 ply_folder_path):

        # dimensions of the bounding box
        self.bb = BoundingBox(*bounding_box)

        # path to the dense reconstruction folder
        self.sfm_path = sfm_folder_path
        
        # initializing and updating the pycolmap model
        self.sfm_model = pycolmap.Reconstruction()
        self.sfm_model.read_binary(sfm_folder_path)
        
        # initializing camera helper
        self.camera_helper = CameraHelpers()    

        # ply folder path to write the cropped pointcloud
        self.ply_folder_path = ply_folder_path

    def generate_indices(self):

        file_list = os.listdir(self.image_path)
        # Code to split file name and extract frame number
    
    def get_file_paths(self, frame_id):
        # Get paths to camera poses, segmentations, images, and point clouds
        pass

    def _transform_pcl(self, pcl, camera_pose):
        # Transform the point cloud to the camera frame
        pass

    def _crop_pcl(self, pcl):
        # Crop the point cloud to the bounding box
        pass

    def _transform_points3d_to_camera_frame(self, camera_rt):
        """ 
        transforms the 3d points in the sfm model from WORLD to CAMERA frame 
        :param camera_rt (np.ndaary): 3 * 4 camera extrinsics matrix
        :return np.ndarray: n * 3 numpy array representing the 3d points in the camera frame
        """

        sfm_points_dict = self.sfm_model.points3D

        X = np.array([value.xyz for value in sfm_points_dict.values()]) #co-ordinates in world frame
        ones = np.ones((X.shape[0], 1))
        X_homo = np.hstack((X, ones)) #homogeneous co-ordinates
    
        camera_rt_homo = np.vstack((camera_rt, np.array([0, 0, 0, 1])))
        
        Xc_homo = np.dot(camera_rt_homo ,X_homo.T).T #homogeneous co-ordinates in camera frame 
        Xc =  Xc_homo[:, :3] / Xc_homo[:, 3:] #dehomogenizing
        return Xc
    
    def transform_model_to_camera_frame(self,camera_Rt):
        """ 
        transforms the pycolmap model from WORLD to CAMERA frame 
        :param camera_rt (np.ndaary): 3 * 4 camera extrinsics matrix
        :return pycolmap.Reconstruction(): model with the pointclouds in the camera frame
        """
        
        points3d_in_camera_frame = self._transform_points3d_to_camera_frame(camera_Rt)
        output_model = pycolmap.Reconstruction()
        for (id, input_pt), new_pt in zip(self.sfm_model.points3D.items(), points3d_in_camera_frame):
            output_model.add_point3D(xyz = new_pt , track = pycolmap.Track(), color = input_pt.color)
        
        return output_model        

    def _frame_id(self,image_id): 
        name_ = self.sfm_model.images[image_id].name 
        frame_id = int(name_.split("/")[-1].split("_")[1])
        return frame_id

    def write_sfm_model_to_disk(self, model, image_id):
        """
        writes the model as a PLY file to the disk
        default location: ply/sfm_in_camera_frame/left/frame_id.ply
        :param model pycolmap.Reconstruction object
        :param image_id 
        :return str: path to the written PLY file
        """

        image_name = self.sfm_model.images[image_id].name
        # checks for left/right frame
        is_left = (image_name.split("/")[0] == "left")
        frame_id = self._frame_id(image_id) 
        
        # exporting the model as PLY file
        ply_file_path = self.ply_folder_path + ("/left/" if is_left else "/right/")
        # os.makedirs(ply_file_path, exist_ok=True)    
        io_utils.delete_folders([ply_file_path])
        io_utils.create_folders([ply_file_path])
        ply_file_path += "frame_" + str(frame_id) + ".ply"
        model.export_PLY(ply_file_path)
        return ply_file_path

    def write_cropped_pcl_to_disk(self, cropped_pcl, image_id, prefix="cropped_pcl/"):
        """
        writes the cropped pointcloud as a PLY file to the disk
        :param cropped_pcl open3d.geometry.PointCloud object
        :param image_id
        """
        
        image_name = self.sfm_model.images[image_id].name
        is_left = (image_name.split("/")[0] == "left")
        frame_id = self._frame_id(image_id)

        output_path = "../ply/" + prefix  + ("/left/" if is_left else "/right/")
        
        io_utils.delete_folders([output_path])  
        io_utils.create_folders([output_path])
        
        output_path += "frame_" + str(frame_id) + ".ply"
        o3d.io.write_point_cloud(output_path, cropped_pcl)

    def generate_cropped_pcl(self, ply_path):
        """
        transforms the pointcloud from the WORLD to CAMERA frame 
        and crops the pointcloud region around the camera pose
        (specified by the bounding box)
        :param ply_path (str) =>  path to the sfm_in_camera_frame ply file
        :return open3d.geometry.PointCloud: cropped pointcloud around the camera pose
        """

        # Reading the point cloud in open3d
        pcd = o3d.io.read_point_cloud(ply_path)
        # Define the bounding box
        min_bound = [self.bb.min_x, self.bb.min_y, self.bb.min_z]  # replace with the minimum x, y, z coordinates of the bounding box
        max_bound = [self.bb.max_x, self.bb.max_y, self.bb.max_z]  # replace with the maximum x, y, z coordinates of the bounding box
        # cropping the pointcloud
        bbox = o3d.geometry.AxisAlignedBoundingBox(min_bound, max_bound)
        cropped_pcd = pcd.crop(bbox)
        return cropped_pcd
        
    def generate(self):
        ''' Generate frame-wise cropped pointcloud around the camera'''
        
        sfm_image_ids = []
        sfm_images_dict = self.sfm_model.images
        for image_id, _  in sfm_images_dict.items():
            sfm_image_ids.append(image_id)        
        sfm_image_ids = sorted(sfm_image_ids)

        for image_id in tqdm(sfm_image_ids):
            sfm_image = sfm_images_dict[image_id]
            
            # camera extrinsics for the current image id
            cam_Rt = self.camera_helper.cam_extrinsics(sfm_image)   
            
            # sfm model transformed from WORLD to CAMERA frame
            sfm_in_camera_frame_model = self.transform_model_to_camera_frame(cam_Rt)
            PLY_path = self.write_sfm_model_to_disk(sfm_in_camera_frame_model, image_id)
            
            #cropping the sfm_in_camera frame pointcloud
            #cropped_pcl = self.generate_cropped_pcl(PLY_path)
            #self.write_cropped_pcl_to_disk(cropped_pcl, image_id)
            
            #break
            
    