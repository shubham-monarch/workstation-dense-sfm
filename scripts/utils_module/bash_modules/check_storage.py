#! /usr/bin/env python3

import json
import logging,coloredlogs
import argparse
import sys
import os
from scripts.utils_module import io_utils


def get_folder_size(folder_path):
	total_size = 0
	for dirpath, dirnames, filenames in os.walk(folder_path):
		for f in filenames:
			fp = os.path.join(dirpath, f)
			# skip if it is symbolic link
			if not os.path.islink(fp):
				total_size += os.path.getsize(fp)
	
	total_size_in_gb = total_size / (1024**3)
	return total_size_in_gb

if __name__ == "__main__":
	coloredlogs.install(level="INFO",force=True)

	logging.info("=======================")
	logging.info(f"CHECKING STORAGE SIZE")
	logging.info("=======================\n")


	target_folder = "/home/ubuntu/workstation-sfm-setup"
	folder_size = get_folder_size(target_folder)

	# folders_to_delete = [os.path.join(target_folder, "output-backend"), 
	# 					os.path.join(target_folder, "input-backend"),
	# 					os.path.join(target_folder, "output")]

	folders_to_delete = [os.path.join(target_folder, "bkp-logs")]
	
	logging.info(f"Folder size: {folder_size} GB")
	logging.info(f"folders to delete: {folders_to_delete}")

	
	if folder_size > 100:
		logging.info("=======================")
		logging.info(f"Folder size is greater than 100 GB. Deleting folders: {folders_to_delete}")
		logging.info("=======================\n")

		io_utils.delete_folders(folders_to_delete)