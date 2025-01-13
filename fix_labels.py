#! /usr/bin/env python3

import boto3
import re
from typing import List
from urllib.parse import urlparse
import os

from logger import get_logger

def get_leaf_folders(s3_uri: str) -> List[str]:
    """
    Recursively find all folders matching pattern 'number_to_number' under .svo directories
    
    Args:
        s3_uri (str): S3 URI in the format 's3://bucket-name/path/to/folder'
        
    Returns:
        List[str]: List of S3 URIs of matching folders (e.g., '.../front_2024-02-22-13-32-18.svo/86_to_228/')
    """
    # Parse S3 URI to get bucket and prefix
    parsed_uri = urlparse(s3_uri)
    if not parsed_uri.netloc:
        raise ValueError("Invalid S3 URI format. Expected 's3://bucket-name/path'")
    
    bucket_name = parsed_uri.netloc
    prefix = parsed_uri.path.lstrip('/')
    
    # Initialize S3 client
    s3_client = boto3.client('s3')
    
    # Pattern for matching folders like 'number_to_number' (e.g., '86_to_228')
    folder_pattern = re.compile(r'^\d+_to_\d+$')
    # Pattern for matching .svo directories
    svo_pattern = re.compile(r'.*\.svo$')
    
    matching_folders = []
    
    def explore_folder(current_prefix: str):
        """Recursively explore folders and find matching folders under .svo directories"""
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix=current_prefix,
            Delimiter='/'
        )
        
        # Process each subfolder
        for prefix_obj in response.get('CommonPrefixes', []):
            folder_path = prefix_obj['Prefix']
            folder_name = folder_path.rstrip('/').split('/')[-1]
            parent_folder = '/'.join(folder_path.rstrip('/').split('/')[:-1])
            
            # If parent is an .svo directory and current folder matches the numeric pattern
            if svo_pattern.match(parent_folder.split('/')[-1]) and folder_pattern.match(folder_name):
                matching_folders.append(f's3://{bucket_name}/{folder_path}')
            
            # Continue exploring subfolders
            explore_folder(folder_path)
    
    # Start exploration from the initial prefix
    explore_folder(prefix)
    return matching_folders

def download_s3_folder(s3_uri: str, local_dir: str) -> None:
    """
    Download all contents of an S3 folder to a local directory
    
    Args:
        s3_uri (str): S3 URI in the format 's3://bucket-name/path/to/folder'
        local_dir (str): Local directory path where files should be downloaded
    """

    logger = get_logger("download_s3_folder")

    logger.info(f"====================")
    logger.info(f"Downloading {s3_uri} to {local_dir}")
    logger.info(f"====================\n")
    
    # Parse S3 URI
    parsed_uri = urlparse(s3_uri)
    bucket_name = parsed_uri.netloc
    prefix = parsed_uri.path.lstrip('/')
    
    # Initialize S3 client
    s3_client = boto3.client('s3')
    
    # List all objects in the S3 folder
    paginator = s3_client.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
        for obj in page.get('Contents', []):
            # Get the relative path of the file
            s3_path = obj['Key']
            # Create the local file path
            local_path = os.path.join(local_dir, os.path.relpath(s3_path, prefix))
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            # Download the file
            s3_client.download_file(bucket_name, s3_path, local_path)

# Example usage:
if __name__ == "__main__":
    
    logger = get_logger("fix_labels")
    
    
    
    s3_uri = "s3://occupancy-dataset/output-backend/dense-reconstruction/dairy/"
    matching_folders = get_leaf_folders(s3_uri)
    
    for folder in matching_folders:
        
        sub_folder = folder.split('/')[-2]
        svo_folder = folder.split('/')[-3]

        logger.info(f"folder: {folder}")
        logger.info(f"sub_folder: {sub_folder}")
        logger.info(f"svo_folder: {svo_folder}")

        DENSE_RECON_OUTPUT_DIR=f"output-backend/dense-reconstruction/{svo_folder}/{sub_folder}"

        logger.info(f"DENSE_RECON_OUTPUT_DIR: {DENSE_RECON_OUTPUT_DIR}")

        # os.makedirs(DENSE_RECON_OUTPUT_DIR, exist_ok=True)
        
        # Example usage of the new function
        download_s3_folder(folder, DENSE_RECON_OUTPUT_DIR)
        


        break


       

