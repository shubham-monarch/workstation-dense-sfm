#! /usr/bin/env python3

import os
import boto3
import logging, coloredlogs
import sys
from botocore.exceptions import ClientError
import argparse
from tqdm import tqdm

def upload_folder_to_s3(local_folder, bucket_name, s3_folder, overwrite=False):
	s3 = boto3.client('s3')
	
	success_count = 0
	failure_count = 0
	skipped_count = 0
	total_files = 0

	try:
		
		total_files = sum(len(files) for _, _, files in os.walk(local_folder))

		for root, dirs, files in os.walk(local_folder):
			for file in tqdm(files, desc="Uploading to S3.."):
				# logging.info(f"file: {file}")
				total_files += 1
				local_path = os.path.join(root, file)
				relative_path = os.path.relpath(local_path, local_folder)
				s3_path = os.path.join(s3_folder, relative_path).replace("\\", "/")
				
				try:
					# Check if file already exists in S3
					try:
						s3.head_object(Bucket=bucket_name, Key=s3_path)
						file_exists = True
					except ClientError:
						file_exists = False

					if file_exists and not overwrite:
						# logging.warning(f"Skipping {local_path} as it already exists in S3")
						skipped_count += 1
					else:
						# logging.info(f"Uploading {local_path} to {s3_path}")
						s3.upload_file(local_path, bucket_name, s3_path)
						success_count += 1
				except ClientError as e:
					logging.error(f"Error uploading {local_path}: {e}")
					failure_count += 1

	except Exception as e:
		logging.error(f"An error occurred: {e}")
		return False, {"total": total_files, "success": success_count, "failure": failure_count, "skipped": skipped_count}

	if failure_count == 0:
		return True, {"total": total_files, "success": success_count, "failure": failure_count, "skipped": skipped_count}
	else:
		return False, {"total": total_files, "success": success_count, "failure": failure_count, "skipped": skipped_count}


if __name__ == "__main__":
	coloredlogs.install(level='INFO', force=True)

	logging.info("=======================")
	logging.info(f"UPLOADING FOLDER TO S3")
	logging.info("=======================\n")


	parser = argparse.ArgumentParser(description='Process some paths and bounding box.')
	parser.add_argument('--folder_LOCAL', type=str,  required = True, help='Folder to upload to S3')
	parser.add_argument('--folder_S3', type=str,  required = True, help='Prefix for S3 folder')
	parser.add_argument('--bucket_S3', type=str,  required = True, help='S3 bucket name')
	
	args = parser.parse_args()
	
	# Set your parameters
	# local_folder = "output-backend/labelled-pointclouds/RJM/2024_06_06_utc/svo_files/front_2024-06-06-10-01-19.svo/4_to_146"
	# bucket_name = "occupancy-dataset"
	# s3_folder = os.path.relpath(local_folder, "output-backend/")
	
	folder_LOCAL = args.folder_LOCAL
	folder_S3 = args.folder_S3 
	bucket_S3 = args.bucket_S3

	# print args
	logging.info(f"folder_LOCAL: {folder_LOCAL}")
	logging.info(f"folder_S3: {folder_S3}")
	logging.info(f"bucket_S3: {bucket_S3}")
	
	flag =  upload_folder_to_s3(folder_LOCAL, bucket_S3, folder_S3)

	if flag:
		sys.exit(0)
	else:
		sys.exit(1)