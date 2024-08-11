import numpy as np
import os
import open3d as o3d
import pycolmap
from pathlib import Path
import time
import sys

from tqdm import tqdm

from collections import namedtuple
import logging, coloredlogs

from .camera_helpers import CameraHelpers
from . import read_write_model
from ..utils_module import io_utils

from scripts.utils_module import io_utils

coloredlogs.install(level='INFO', force=True)

BoundingBox = namedtuple('BoundingBox', ['min_x', 'max_x', 'min_y', 'max_y', 'min_z', 'max_z'])

class P360DatasetGenerator:
    """
    Helper class to  generate cropped pointcloud around the camera pose for each frame  
    :param bounding_box: tuple representing the dimensions of the bounding box (min_x, max_x, min_y, max_y, min_z, max_z)
    :param dense_sfm_path: path to the dense sfm reconstruction folder containing images.bin, cameras.bin, points3D.bin
    :param output_path: Path containing frame-wise cropped pointcloud
    """

    def __init__(self, 
                 mode,
                 bounding_box, 
                 dense_recon_folder, 
                 pcl_output, 
                 pcl_cropped_output):


        self.dense_recon_folder = dense_recon_folder
        self.mode = mode

        # dimensions of the bounding box
        self.bb = BoundingBox(*bounding_box)

        # path to the dense reconstruction folder
        self.sfm_path = dense_recon_folder
        
        # initializing and updating the pycolmap model
        self.sfm_model = pycolmap.Reconstruction()
        self.sfm_model.read_binary(dense_recon_folder)
        
        # initializing camera helper
        self.camera_helper = CameraHelpers()    

        # path to write the camera-frame (cropped) pointclouds
        
        self.pcl_output = pcl_output
        self.pcl_cropped_output = pcl_cropped_output

        logging.info(f"pcl_output: {pcl_output}")
        logging.info(f"pcl_cropped_output: {pcl_cropped_output}")
        

        io_utils.delete_folders([self.pcl_output, self.pcl_cropped_output])
        io_utils.create_folders([self.pcl_output, self.pcl_cropped_output])

        
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
    
    def transform_model_to_camera_frame(self,camera_Rt) -> pycolmap.Reconstruction:
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

    # def write_sfm_model_to_disk(self, model, image_id, output_folder):
    #     """
    #     writes the model as a PLY file to the disk
    #     default location: ply/sfm_in_camera_frame/left/frame_id.ply
    #     :param model pycolmap.Reconstruction object
    #     :param image_id 
    #     :return str: path to the written PLY file
    #     """

    #     image_name = self.sfm_model.images[image_id].name
    #     # checks for left/right frame
    #     is_left = (image_name.split("/")[0] == "left")
    #     frame_id = self._frame_id(image_id) 
        
    #     ply_file_path = output_folder + ("/left/" if is_left else "/right/")
        
    #     io_utils.create_folders([ply_file_path])
        
    #     ply_file_path += "frame_" + str(frame_id) + ".ply"
        
    #     # exporting the model as PLY file
    #     model.export_PLY(ply_file_path)
    #     return ply_file_path
    
    def write_PLY(self, model : pycolmap.Reconstruction,  output_folder : str, is_left : bool) -> None:

        ply_file_path = os.path.join(output_folder, "left.ply" if is_left else "right.ply")
        model.export_PLY(ply_file_path)

    def write_cropped_pcl_to_disk(self, cropped_pcl, image_id, output_folder):
        """
        writes the cropped pointcloud as a PLY file to the disk
        :param cropped_pcl open3d.geometry.PointCloud object
        :param image_id
        """
        
        image_name = self.sfm_model.images[image_id].name
        is_left = (image_name.split("/")[0] == "left")
        frame_id = self._frame_id(image_id)

        output_path = output_folder + ("/left/" if is_left else "/right/")
        
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
    
    def frame_from_name(self, name : str) -> int:
        '''
        extracts the frame number from the image name

        input: left/frame_1000_.jpg
        output: 1000
        '''
        return name.split("/")[-1].split("_")[1]
    
    def generate(self, frame_skip_rate):
        ''' Generate frame-wise cropped pointcloud around the camera'''
        
        sfm_image_ids = []
        sfm_images_dict = self.sfm_model.images
        

        for image_id, _  in sfm_images_dict.items():
            if image_id <= len(sfm_images_dict) // 2:
                sfm_image_ids.append(image_id)        
        
        sfm_image_ids = sorted(sfm_image_ids)

        # for id in sfm_image_ids:
        #     logging.info(f"{id} {sfm_images_dict[id].name}")

        # for image_id in tqdm(sfm_image_ids):
        for index, image_id in enumerate(tqdm(sfm_image_ids)):
            
            # cropping [1 / 10] frames
            if index % frame_skip_rate != 0:
                continue
            
            image_id_LEFT = image_id
            image_id_RIGHT = image_id + len(sfm_images_dict) // 2
            
            image_LEFT = sfm_images_dict[image_id_LEFT]
            image_RIGHT = sfm_images_dict[image_id_RIGHT]
            
            frame_id = self.frame_from_name(image_LEFT.name)
        
            
            # camera extrinsics for the current image id
            # cam_Rt = self.camera_helper.cam_extrinsics(sfm_image)   
            cam_Rt_LEFT = self.camera_helper.cam_extrinsics(image_LEFT)   
            cam_Rt_RIGHT = self.camera_helper.cam_extrinsics(image_RIGHT)   
            

            # sfm model transformed from WORLD to CAMERA frame
            sfm_camera_frame_LEFT = self.transform_model_to_camera_frame(cam_Rt_LEFT)
            sfm_camera_frame_RIGHT = self.transform_model_to_camera_frame(cam_Rt_RIGHT)

            # ply_LEFT = self.write_sfm_model_to_disk(sfm_camera_frame_LEFT, image_id_LEFT, self.pcl_output)
            # ply_RIGHT = self.write_sfm_model_to_disk(sfm_camera_frame_RIGHT, image_id_RIGHT, self.pcl_output)
            
            # save (ply_LEFT, ply_RIGHT) and (img_LEFT, img_RIGHT) to [frame_folder]
            frame_folder = os.path.join(self.pcl_output, f"frame-{frame_id}")
            
            # clearing the frame folder
            io_utils.delete_folders([frame_folder])
            io_utils.create_folders([frame_folder])

            # saving left / right PLY
            self.write_PLY(sfm_camera_frame_LEFT, frame_folder, is_left = True)
            self.write_PLY(sfm_camera_frame_RIGHT, frame_folder, is_left = False)
            
            # saving left / right images
            images_folder = os.path.join(self.dense_recon_folder, "images")
            left_image = os.path.join(images_folder, image_LEFT.name)
            right_image = os.path.join(images_folder, image_RIGHT.name)

            io_utils.copy_file(left_image, frame_folder, name = "left.jpg")
            io_utils.copy_file(right_image, frame_folder, name = "right.jpg")
            
            # io_utils.copy_file(left_image, frame_folder)
            # io_utils.copy_file(right_image, frame_folder)
            

            # logging.info(f"frame_folder: {frame_folder}")
            # # # cropping the sfm_in_camera frame pointcloud
            # cropped_pcl = self.generate_cropped_pcl(PLY_path)
            # self.write_cropped_pcl_to_disk(cropped_pcl, image_id, self.pcl_cropped_output)
            
