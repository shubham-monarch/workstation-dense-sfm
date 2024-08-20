#! /usr/bin/env python3

import json
import logging,coloredlogs
import argparse
from scripts.utils_module import io_utils
import os

def update_svo_index(svo_file: str, index_file: str) -> bool:
	"""
	Adds the given svo_file to the index file,
	if it is not already present.
	"""

	try:
		# Attempt to open and read the index file; if it doesn't exist, use an empty list
		io_utils.create_folders([os.path.dirname(index_file)])
		try:
			with open(index_file, 'r') as file:
				processed_files = json.load(file)
		except FileNotFoundError:
			processed_files = []
		
		# Check if svo_file is already in the list
		if svo_file in processed_files:
			return False  # svo_file is already in the index, no update needed
		
		# If svo_file is not in the list, append it
		processed_files.append(svo_file)
		
		# Write the updated list back to the index file
		with open(index_file, 'w') as file:
			json.dump(processed_files, file)
		
		return True  # svo_file was added to the index
	except Exception as e:
		print(f"An error occurred: {e}")
		return False  # An error occurred


if __name__ == "__main__":
	coloredlogs.install(level="INFO",force=True)

	logging.info("=======================")
	logging.info(f"ADDING SVO FILE TO SVO_INDEX")
	logging.info("=======================\n")


	parser = argparse.ArgumentParser(description='Process some paths and bounding box.')
	parser.add_argument('--index_file', type=str,  required = True, help='Path to svo_index.json')
	parser.add_argument('--svo_file', type=str,  required = True, help='Path to svo file')
	
	args = parser.parse_args()

	logging.info(f"Index file: {args.index_file}")
	logging.info(f"SVO file: {args.svo_file}")
	
	# index_file = "index/svo_index.json"
	# svo_file = "abcd.svo"

	# update = update_svo_index(svo_file, index_file)
	update = update_svo_index(args.svo_file, args.index_file)
		
	
