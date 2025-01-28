#! /usr/bin/env python3

import boto3
from urllib.parse import urlparse
import open3d as o3d
import yaml
import numpy as np
from pathlib import Path
import random
import os
from tqdm import tqdm
import json


from logger import get_logger
from data_generator_s3 import DataGeneratorS3, LeafFolder, JSONIndex

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

def correct_pcd_label(pcd: o3d.t.geometry.PointCloud, dairy_yaml: str) -> o3d.t.geometry.PointCloud:
    """
    correct point cloud labels based on point colors using the mapping in dairy.yaml
    
    args:
        pcd: point cloud object
        dairy_yaml: path to the yaml file containing color to label mapping
    """
    logger = get_logger("correct_pcd_label")
    
    with open(dairy_yaml, 'r') as file:
        dairy_config = yaml.safe_load(file)
    
    # get colors and labels from yaml
    color_to_label = {}
    for label, color in dairy_config['color_map'].items():
        # convert yaml BGR colors to RGB for comparison
        rgb_color = (color[2], color[1], color[0])  # BGR to RGB
        color_to_label[tuple(rgb_color)] = label
    
    # convert pcd colors and labels to numpy for efficient operations
    colors = pcd.point['colors'].numpy()  # shape: (N, 3), in RGB
    labels = pcd.point['label'].numpy()  # shape: (N,)
    
    # scale colors to match yaml values (0-255)
    colors = colors.astype(np.int32)
    
    # create a mask for all points that have not been labeled yet
    unlabeled_mask = np.ones(len(labels), dtype=bool)

    # iterate through each defined color and update matching points
    for target_color, label in color_to_label.items():
        # update labels for points with similar colors
        similar_color_mask = is_close(colors, target_color, threshold=20)
        labels[similar_color_mask] = label
        # update the unlabeled mask
        unlabeled_mask[similar_color_mask] = False
    
    # set the label for points not in color_to_label to 0
    labels[unlabeled_mask] = 0
    
    # update pcd labels
    pcd.point['label'] = o3d.core.Tensor(labels)
    
    # save corrected pcd
    return pcd

def get_s3_client():
    """Create and return an S3 client"""
    return boto3.client('s3')

def parse_s3_uri(s3_uri):
    """Parse S3 URI into bucket and prefix"""
    parsed = urlparse(s3_uri)
    bucket = parsed.netloc
    prefix = parsed.path.lstrip('/')
    return bucket, prefix

def list_numbered_folders(s3_uri):
    """List all folders that match the pattern xxxx_to_xxxx"""
    s3_client = get_s3_client()
    bucket, prefix = parse_s3_uri(s3_uri)
    
    # List all objects with the given prefix
    paginator = s3_client.get_paginator('list_objects_v2')
    matching_folders = set()
    
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        if 'Contents' not in page:
            continue
            
        for obj in page['Contents']:
            key = obj['Key']
            # Split the path into components
            parts = key.split('/')
            
            # Look for folders matching the pattern xxxx_to_xxxx
            for part in parts:
                if '_to_' in part and part[0].isdigit():
                    folder_path = f"s3://{bucket}/{key[:key.index(part) + len(part)]}"
                    matching_folders.add(folder_path)
    
    return sorted(list(matching_folders))
    
def get_label_distribution(pcd: o3d.t.geometry.PointCloud, dairy_yaml: str):
    """ get label distribution of point cloud"""
    logger = get_logger("get_label_distribution")
    
    # read labels from yaml file
    with open(dairy_yaml, 'r') as file:
        dairy_config = yaml.safe_load(file)
    
    # get labels from yaml config
    labels = sorted(dairy_config['labels'].keys())
    labels.append(0)

    pcd_labels = pcd.point['label'].numpy()
    
    logger.info("───────────────────────────────")
    
    for label in labels:
        label_mask = pcd_labels == label
        valid_labels = pcd.point['label'].numpy()[label_mask]
        logger.info(f"{label}: {len(valid_labels)} ({len(valid_labels) / len(pcd_labels) * 100:.2f}%)")

    logger.info("───────────────────────────────")


def select_pcd_by_label(pcd: o3d.t.geometry.PointCloud, label: int):
    """ select pcd by label"""
    mask = pcd.point["label"] == label
    pcd_labels = pcd.select_by_index(mask.nonzero()[0])
    return pcd_labels

def test_pcd_labels(src_uri: str, dairy_yaml: str):
    
    logger = get_logger("test_pcd_labels")

    output_dir = f"debug/updated-pcds"
    os.makedirs(output_dir, exist_ok=True)
    
    leaf_folders = DataGeneratorS3.get_leaf_folders([src_uri])

    logger.info(f"───────────────────────────────")
    logger.info(f"len(leaf_folders): {len(leaf_folders)}")  
    logger.info(f"───────────────────────────────")
    
    random.seed(42) # set seed for reproducibility
    random_leaf_folders = random.sample(leaf_folders, 10)
    
    for idx, leaf_folder in enumerate(tqdm(random_leaf_folders, desc="Processing PCDs")):
        pcd_URI = os.path.join(leaf_folder, "left-segmented-labelled.ply")

        logger.warning(f"───────────────────────────────")
        logger.warning(f"{idx}: {pcd_URI}")
        logger.warning(f"───────────────────────────────")
        
        try:
            pcd_path = LeafFolder.download_file(pcd_URI)
            pcd = o3d.t.io.read_point_cloud(pcd_path)

            updated_pcd = correct_pcd_label(pcd, dairy_yaml)
            get_label_distribution(updated_pcd, dairy_yaml)

            output_path = os.path.join(output_dir, f"updated-pcd-{idx}.ply")
            o3d.t.io.write_point_cloud(output_path, updated_pcd)

            # read labels from yaml file
            with open(dairy_yaml, 'r') as file:
                dairy_config = yaml.safe_load(file)
            labels = sorted(dairy_config['labels'].keys())
            # labels.append(0)

            for label in labels:        
                selected_pcd = select_pcd_by_label(updated_pcd, label)
                output_path = os.path.join(output_dir, f"updated-pcd-{idx}-{label}.ply")
                o3d.t.io.write_point_cloud(output_path, selected_pcd)

        except Exception as e:
            logger.error(f"Error processing {pcd_URI}: {e}")
            raise e

def fix_pcds_in_folder(folder_uri: str, dairy_yaml: str):
    """ fix pcds in a folder"""
    logger = get_logger("fix_pcds_in_folder")
    
    index = JSONIndex(json_path=f"index/update-labels.json")
    
    leaf_folders = DataGeneratorS3.get_leaf_folders([folder_uri])
    leaf_folders.sort(key=lambda x: int(x.split('-')[-1]))
    
    folder_is_processed = True
    # check if all pcds in the folder are processed
    for leaf_folder in leaf_folders:
        pcd_URI = os.path.join(leaf_folder, "left-segmented-labelled.ply")
        if not index.has_file(pcd_URI):
            folder_is_processed = False
            break
    
    if folder_is_processed:
        logger.info(f"───────────────────────────────")
        logger.info(f"Skipping {folder_uri} as it is already processed.")
        logger.info(f"───────────────────────────────")
        return
    

    leaf_folder_1 = leaf_folders[0]
    pcd_URI = os.path.join(leaf_folder_1, "left-segmented-labelled.ply")
    pcd_path = LeafFolder.download_file(pcd_URI)
    pcd = o3d.t.io.read_point_cloud(pcd_path)
    updated_pcd = correct_pcd_label(pcd, dairy_yaml)
    updated_labels = updated_pcd.point['label'].numpy()
    # get_label_distribution(updated_pcd, dairy_yaml)

    # logger.info(f"───────────────────────────────")
    # logger.info(f"fixing pcds in folder")
    # logger.info(f"───────────────────────────────")
    
    
    for folder in leaf_folders[1:]:
        pcd_URI = os.path.join(folder, "left-segmented-labelled.ply")
        
        if not index.has_file(pcd_URI):
        
            pcd_path = LeafFolder.download_file(pcd_URI)
            
            # logger.warning(f"───────────────────────────────")
            # logger.warning(f"{pcd_URI}")
            # logger.warning(f"───────────────────────────────")
            
            pcd = o3d.t.io.read_point_cloud(pcd_path)
            pcd.point['label'] = o3d.core.Tensor(updated_labels)
            o3d.t.io.write_point_cloud(pcd_path, pcd)  # Write to local file
            flag = LeafFolder.upload_file(pcd_path, pcd_URI)  # Upload to S3
            
            if flag:
                index.add_file(pcd_URI)
                index.save_index()


if __name__ == "__main__":
    logger = get_logger("update_labels")
    base_uri = "s3://occupancy-dataset/occ-dataset/dairy"

    folders = list_numbered_folders(base_uri)

    # logger.info("───────────────────────────────")
    # logger.info(f"len(folders): {len(folders)}")
    # logger.info("───────────────────────────────")

    # index = JSONIndex(json_path=f"index/update-labels.json")


    for folder in tqdm(folders, desc="Processing folders"):
        
        logger.info(f"───────────────────────────────")
        logger.info(f"Processing {folder}")
        logger.info(f"───────────────────────────────")
        
        fix_pcds_in_folder(folder, "config/dairy.yaml")

    # test_pcd_labels("s3://occupancy-dataset/occ-dataset/dairy/grimius", "config/dairy.yaml")

    # /fix_pcds_in_folder("s3://occupancy-dataset/occ-dataset/dairy/grimius/2024_02_20/front/front_2024-02-13-09-57-14.svo/148_to_290", "config/dairy.yaml")

    
    
    
    
    
    
    
    
    
    
    
    
    