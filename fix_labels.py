#! /usr/bin/env python3

import boto3
import re
from typing import List
from urllib.parse import urlparse
import os
from tqdm import tqdm
import json
from pathlib import Path
import shutil
import time

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

    logger.warning("-------------------------" * 2)
    logger.warning(f"Downloading {s3_uri}...")
    logger.warning("-------------------------" * 2 + "\n")
    
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
    
    # Initialize or load existing results dictionary
    results_file = 'index/label.json'
    if os.path.exists(results_file):
        with open(results_file, 'r') as f:
            results = json.load(f)
    else:
        results = {
            "successful_labels": [],
            "failed_labels": []
        }
    
    # Add progress bar for folder processing
    for folder in tqdm(matching_folders, desc="Processing folders", unit="folder"):
        start_time = time.time()

        sub_folder = folder.split('/')[-2]  # e.g., "86_to_228"
        svo_filename = os.path.relpath(folder, "s3://occupancy-dataset/output-backend/dense-reconstruction/")
        svo_filename = svo_filename.replace(f"/{sub_folder}", "")

        # logger.info(f"====================")
        # logger.info(f"Processing {folder}")
        # logger.info(f"====================\n")
        
        # Extract start and end indices from sub_folder
        start_idx, end_idx = map(int, sub_folder.split('_to_'))
        
        DENSE_RECON_OUTPUT_DIR = f"output-backend/dense-reconstruction/{svo_filename}/{sub_folder}"
        
        # Create label_info for checking
        label_info = {
            "svo_filename": svo_filename,
            "start_idx": start_idx,
            "end_idx": end_idx
        }
        
        # Skip if already processed
        if any(label_info == existing for existing in results["successful_labels"]) or \
           any(label_info == existing for existing in results["failed_labels"]):
            logger.warning(f"Skipping {svo_filename} ({sub_folder}) - already processed")
            continue
        
        # Download the dense reconstruction folder from S3
        download_s3_folder(folder, DENSE_RECON_OUTPUT_DIR)
        
        logger.info("─" * 50)
        logger.info(f"Processing...")
        logger.info(f"SVO_FILENAME:           {svo_filename}")
        logger.info(f"SUB_FOLDER:             {sub_folder}")
        logger.info(f"SVO_START_IDX:          {start_idx}")
        logger.info(f"SVO_END_IDX:            {end_idx}")
        logger.info("─" * 50 + "\n")
        
        # Call main-file.sh with the extracted parameters
        cmd = f"./main-file.sh '{svo_filename}' {start_idx} {end_idx}"
        result = os.system(cmd)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        if result == 0:
            logger.warning("-------------------------" * 2)
            logger.warning(f"Successfully processed {svo_filename} in {processing_time:.2f} seconds")
            logger.warning("-------------------------" * 2 + "\n")
            
            results["successful_labels"].append(label_info)
            # Write results after each successful processing
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=4)
        else:
            logger.error(f"main-file.sh failed with exit code {result} after {processing_time:.2f} seconds")
            results["failed_labels"].append(label_info)
            continue
        
        try:
            shutil.rmtree(f"output-backend/")
        except Exception as e:
            logger.error(f"Error removing the output-backend directory: {e}")
        

       

