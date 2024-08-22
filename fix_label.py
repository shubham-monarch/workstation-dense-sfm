#! /usr/bin/env python3

import subprocess
import os
import boto3
import logging, coloredlogs
import shutil

def download_s3_folder(bucket_name, s3_folder, local_dir=None):
    """
    Download all contents of an s3 folder to a local directory.

    :param bucket_name: Name of the S3 bucket.
    :param s3_folder: Folder path inside the S3 bucket.
    :param local_dir: Local directory to download the files to. If None, uses the current directory.
    """
    s3 = boto3.client('s3')
    if local_dir is None:
        local_dir = os.getcwd()
    
    paginator = s3.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket_name, Prefix=s3_folder):
        for obj in page.get('Contents', []):
            # Remove the S3 folder path and keep the rest
            local_file_path = os.path.join(local_dir, os.path.relpath(obj['Key'], s3_folder))
            local_file_dir = os.path.dirname(local_file_path)
            
            # Create local directory structure if it doesn't exist
            if not os.path.exists(local_file_dir):
                os.makedirs(local_file_dir)
            
            # Download the file
            print(f"Downloading {obj['Key']} to {local_file_path}")
            s3.download_file(bucket_name, obj['Key'], local_file_path)


if __name__ == "__main__":
    
    coloredlogs.install(level="INFO", force=True)

    
    script_path = "./main-file.sh"
    arg4="2"
    arg5="vineyards"

    # svo_files = ['front_2024-06-05-09-29-54.svo', 'front_2024-06-05-09-38-13.svo']
    svo_files = ['front_2024-06-05-09-38-13.svo', 
    'front_2024-06-05-09-43-13.svo',
    'front_2024-06-05-10-29-30.svo',
    'front_2024-06-05-10-34-31.svo',
    'front_2024-06-05-11-42-41.svo',
    'front_2024-06-06-09-31-19.svo',
    'front_2024-06-06-09-36-19.svo',
    'front_2024-06-06-09-41-19.svo',
    'front_2024-06-06-10-01-19.svo',
    'front_2024-06-06-10-06-19.svo',
    'front_2024-06-06-10-28-40.svo',
    'front_2024-06-06-10-33-41.svo']

    # svo_files = ['front_2024-06-05-09-38-13.svo']
    prefix = "output-backend/dense-reconstruction/RJM/2024_06_06_utc/svo_files/"
    bucket_name="occupancy-dataset"

        
    for svo_file in svo_files:
        s3_folder = prefix + svo_file
        local_dir = prefix + svo_file
        download_s3_folder(bucket_name, s3_folder, local_dir)    

        subfolders = [f.name for f in os.scandir(local_dir) if f.is_dir()]

        for subfolder in subfolders:
            parts = subfolder.split('_')
            first_idx = int(parts[0])
            last_idx = int(parts[-1])
            logging.info(f"[{first_idx}, {last_idx}]")

            arg1="RJM/2024_06_06_utc/svo_files/" + svo_file
            arg2=f"{first_idx}"
            arg3=f"{last_idx}"

            # Run the script with arguments
            result = subprocess.run(["bash", script_path, str(arg1), str(arg2), str(arg3), str(arg4), str(arg5)], capture_output=True, text=True)
            print("Output:", result.stdout)
            print("Error:", result.stderr)

            subfolder_local_dir = os.path.join(local_dir, subfolder)
            # shutil.rmtree(subfolder_local_dir)
        
        # delete the dense-resconstruction folder
        shutil.rmtree("output-backend")
        shutil.rmtree("output")